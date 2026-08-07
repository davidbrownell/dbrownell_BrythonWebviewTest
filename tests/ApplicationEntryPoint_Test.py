import os
import signal
import socket
import subprocess
import sys
import time

from collections.abc import Generator
from pathlib import Path
from typing import Any, Mapping
from unittest.mock import Mock

import pytest

from click.testing import Result
from dbrownell_Common import SubprocessEx
from _pytest.monkeypatch import MonkeyPatch
from selenium import webdriver
from selenium.webdriver.remote.webdriver import WebDriver

from typer.testing import CliRunner

from dbrownell_BrythonWebviewTest.ApplicationEntryPoint import app
from dbrownell_BrythonWebviewTest.Impl.EntryPointUtils import GetUnusedPort

import TestImpl


# Selenium tests for ApplicationEntryPoint require pywebview (a GUI),
# which is not available in headless CI environments.
_skip_headless = pytest.mark.skipif(
    os.environ.get("CI", "").lower() in ("true", "1")
    or os.environ.get("GITHUB_ACTIONS", "").lower() in ("true", "1"),
    reason="ApplicationEntryPoint selenium tests require a GUI display (pywebview)",
)


# ----------------------------------------------------------------------
def test_Version() -> None:
    TestImpl.TestVersion(app)


# ----------------------------------------------------------------------
def test_NoArgs(monkeypatch: MonkeyPatch) -> None:
    result, threading, webview = _Execute(monkeypatch, [])

    assert threading is not None
    assert webview is not None

    assert threading["kwargs"]["host"] == "127.0.0.1"
    assert webview[1] == f"http://{threading['kwargs']['host']}:{threading['kwargs']['port']}/"


# ----------------------------------------------------------------------
def test_Port(monkeypatch: MonkeyPatch) -> None:
    result, threading, webview = _Execute(monkeypatch, ["--port", "12345"])

    assert threading is not None
    assert webview is not None

    assert threading["kwargs"]["port"] == 12345
    assert webview[1] == f"http://{threading['kwargs']['host']}:{threading['kwargs']['port']}/"


# ----------------------------------------------------------------------
@_skip_headless
def test_MissingValues(_driver: WebDriver) -> None:
    TestImpl.TestMissingValues(_driver)


# ----------------------------------------------------------------------
@_skip_headless
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

    debug_port = GetUnusedPort()

    entry_point_filename = (
        Path(__file__).parent.parent / "src" / "dbrownell_BrythonWebviewTest" / "ApplicationEntryPoint.py"
    )

    assert entry_point_filename.is_file(), entry_point_filename

    popen_kwargs: dict = {
        "shell": True,
        "stderr": subprocess.STDOUT,
        "stdin": subprocess.PIPE,
        "stdout": subprocess.PIPE,
    }

    env = os.environ.copy()

    # On Unix, start in a new session so we can kill the entire process group
    if sys.platform != "win32":
        popen_kwargs["start_new_session"] = True

        # Ensure that pywebview uses the Qt backend, which is based on Chromium and allows us to
        # use the debugging port.
        env["PYWEBVIEW_GUI"] = "qt"

    with subprocess.Popen(
        f'python "{entry_point_filename}" --debug --debug-port {debug_port}',
        env=env,
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

            else:
                # ----------------------------------------------------------------------
                def LinuxFinally() -> None:
                    os.killpg(os.getpgid(result.pid), signal.SIGTERM)

                # ----------------------------------------------------------------------

                finally_func = LinuxFinally

            # Wait for pywebview's remote debugging port to accept connections. Block until a TCP connection
            # succeeds.
            timeout = 30.0  # seconds
            deadline = time.monotonic() + timeout

            while time.monotonic() < deadline:
                try:
                    with socket.create_connection(("127.0.0.1", debug_port), timeout=1):
                        break
                except OSError:
                    time.sleep(0.5)

            if time.monotonic() > deadline:
                raise TimeoutError(f"Port {debug_port} did not become available within {timeout}s.")

            if sys.platform == "win32":
                # pywebview uses Edge WebView2 on Windows
                options = webdriver.EdgeOptions()
                options.add_experimental_option("debuggerAddress", f"127.0.0.1:{debug_port}")
                driver = webdriver.Edge(options=options)
            else:
                # pywebview uses Qt/Chromium on other platforms
                options = webdriver.ChromeOptions()
                options.add_experimental_option("debuggerAddress", f"127.0.0.1:{debug_port}")
                driver = webdriver.Chrome(options=options)

            try:
                TestImpl.WaitForBrython(driver)

                yield driver

            finally:
                driver.quit()

        finally:
            finally_func()
            result.wait()


# ----------------------------------------------------------------------
def _Execute(
    monkeypatch: MonkeyPatch,
    args: list[str],
    *,
    expect_failure: bool = False,
) -> tuple[Result, Mapping[str, Any] | None, tuple[Any, ...] | None]:
    threading_mock = Mock()
    webview_mock = Mock()

    monkeypatch.setattr("dbrownell_BrythonWebviewTest.ApplicationEntryPoint.threading", threading_mock)
    monkeypatch.setattr("dbrownell_BrythonWebviewTest.ApplicationEntryPoint.webview", webview_mock)

    result = CliRunner().invoke(app, args)

    if expect_failure:
        assert result.exit_code != 0, result.stdout
        return result, None, None

    assert result.exit_code == 0, result.stdout
    return result, threading_mock.mock_calls[0].kwargs, webview_mock.mock_calls[0].args
