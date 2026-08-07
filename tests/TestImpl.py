import typer
from typer.testing import CliRunner

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from dbrownell_BrythonWebviewTest import __version__


# Brython must download and execute ~6MB of JavaScript (brython.js + brython_stdlib.js) before it
# runs index.py and binds the click handler. On slow or heavily loaded CI runners this takes a
# while, so allow a generous timeout.
BRYTHON_LOAD_TIMEOUT = 60

# Timeout for a single calculation round trip once Brython is loaded.
RESULT_TIMEOUT = 30


# ----------------------------------------------------------------------
def WaitForBrython(driver: WebDriver) -> None:
    """Wait until Brython has executed index.py and bound the submit button's click handler.

    The submit button is present in the static HTML immediately, well before Brython finishes
    loading, so waiting for the element alone races against the handler being bound. Clicking
    before then is silently a no-op and the result element never updates.
    """

    WebDriverWait(driver, BRYTHON_LOAD_TIMEOUT).until(
        EC.visibility_of_element_located((By.ID, "submitBtn")),
    )

    WebDriverWait(driver, BRYTHON_LOAD_TIMEOUT).until(
        lambda d: d.find_element(By.ID, "submitBtn").get_attribute("data-ready") == "true",
    )


# ----------------------------------------------------------------------
def _ClickAndWaitForResult(
    driver: WebDriver,
    button: WebElement,
    result: WebElement,
    expected: str,
) -> None:
    """Click the submit button and wait for the result element to show the expected text.

    Retries the click once if the expected text has not appeared within the timeout. The click
    handler is asynchronous, and a click dispatched while Brython is still settling can be lost.
    """

    button.click()

    try:
        WebDriverWait(driver, RESULT_TIMEOUT).until(lambda d: result.text.strip() == expected)
    except TimeoutException:
        # The click may have been dropped; try once more before failing so that a single lost
        # event does not fail the run.
        button.click()
        WebDriverWait(driver, RESULT_TIMEOUT).until(lambda d: result.text.strip() == expected)

    assert result.text.strip() == expected


# ----------------------------------------------------------------------
def TestVersion(app: typer.Typer) -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["--version"])

    assert result.exit_code == 0
    assert result.output.strip() == __version__


# ----------------------------------------------------------------------
def TestMissingValues(driver: WebDriver) -> None:
    button = driver.find_element(By.ID, "submitBtn")
    result = driver.find_element(By.ID, "result")
    num1 = driver.find_element(By.ID, "num1")
    num2 = driver.find_element(By.ID, "num2")

    expected = "Please enter valid numbers"

    # No values
    _ClickAndWaitForResult(driver, button, result, expected)

    # num1 is empty
    num1.clear()
    num2.clear()
    num2.send_keys("3.14")
    _ClickAndWaitForResult(driver, button, result, expected)

    # num2 is empty
    num1.clear()
    num2.clear()
    num1.send_keys("5")
    _ClickAndWaitForResult(driver, button, result, expected)


# ----------------------------------------------------------------------
def TestOperations(driver: WebDriver) -> None:
    button = driver.find_element(By.ID, "submitBtn")
    result = driver.find_element(By.ID, "result")
    num1 = driver.find_element(By.ID, "num1")
    num2 = driver.find_element(By.ID, "num2")
    op = Select(driver.find_element(By.ID, "operation"))

    num1.send_keys("10")
    num2.send_keys("2")

    for operation, expected in [
        ("add", """{"result":12.0}"""),
        ("sub", """{"result":8.0}"""),
        ("mult", """{"result":20.0}"""),
        ("div", """{"result":5.0}"""),
    ]:
        op.select_by_value(operation)
        _ClickAndWaitForResult(driver, button, result, expected)
