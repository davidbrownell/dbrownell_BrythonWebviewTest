import os
import signal
import subprocess
import sys
import time
import urllib.error
import urllib.request

from collections.abc import Generator
from pathlib import Path

import pytest

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from dbrownell_BrythonWebviewTest.LocalServerEntryPoint import app
from dbrownell_BrythonWebviewTest.Impl.EntryPointUtils import GetUnusedPort

import TestImpl


# ----------------------------------------------------------------------
def test_Version() -> None:
    TestImpl.TestVersion(app)


# ----------------------------------------------------------------------
def test_MissingValues(_driver: WebDriver) -> None:
    TestImpl.TestMissingValues(_driver)


# ----------------------------------------------------------------------
def test_Operations(_driver: WebDriver) -> None:
    TestImpl.TestOperations(_driver)


# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
@pytest.fixture
def _driver() -> Generator[WebDriver, None, None]:
    """Pytest fixture that launches the Brython webview application and yields a Selenium WebDriver.

    Starts the EntryPoint.py application in debug mode on an available port, connects
    to it via Edge WebDriver, waits for the UI to be ready, and yields the driver for
    test use. Cleans up by quitting the driver and terminating the application process
    tree on fixture teardown.

    Yields:
        WebDriver: A Selenium Edge WebDriver connected to the running webview application.
    """

    port = GetUnusedPort()

    entry_point_filename = (
        Path(__file__).parent.parent / "src" / "dbrownell_BrythonWebviewTest" / "LocalServerEntryPoint.py"
    )

    assert entry_point_filename.is_file(), entry_point_filename

    popen_kwargs: dict = {
        "shell": True,
        "stderr": subprocess.STDOUT,
        "stdin": subprocess.PIPE,
        "stdout": subprocess.PIPE,
    }

    # On Unix, start in a new session so we can kill the entire process group
    if sys.platform != "win32":
        popen_kwargs["start_new_session"] = True

    with subprocess.Popen(
        f'python "{entry_point_filename}" --port {port} --debug',
        **popen_kwargs,
    ) as result:
        try:
            if sys.platform == "win32":
                # ----------------------------------------------------------------------
                def Win32Finally() -> None:
                    subprocess.run(
                        f"taskkill /F /T /PID {result.pid}",
                        shell=True,
                        capture_output=True,
                    )

                # ----------------------------------------------------------------------

                finally_func = Win32Finally

                # Create an Edge driver, which is used by pywebview
                options = webdriver.EdgeOptions()
                options.add_argument("--headless=new")

                driver = webdriver.Edge(options=options)

            else:
                # ----------------------------------------------------------------------
                def LinuxFinally() -> None:
                    os.killpg(os.getpgid(result.pid), signal.SIGTERM)

                # ----------------------------------------------------------------------

                finally_func = LinuxFinally

                # Create a Chrome driver
                options = webdriver.ChromeOptions()
                options.add_argument("--headless=new")

                driver = webdriver.Chrome(options=options)

            try:
                # Wait for the server to be ready before navigating
                for _ in range(30):
                    try:
                        urllib.request.urlopen(f"http://127.0.0.1:{port}/", timeout=1)
                        break
                    except (ConnectionRefusedError, urllib.error.URLError, OSError):
                        time.sleep(1)

                driver.get(f"http://127.0.0.1:{port}/")

                WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "submitBtn")))

                yield driver

            finally:
                driver.quit()

        finally:
            finally_func()
            result.wait()
