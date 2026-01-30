import typer
from typer.testing import CliRunner

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from dbrownell_BrythonWebviewTest import __version__


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

    wait = WebDriverWait(driver, 15)

    # No values
    old_value = result.text

    button.click()

    wait.until(lambda d: result.text != old_value and result.text.strip() != "")
    assert result.text == "Please enter valid numbers"

    # num1 is empty
    num1.clear()
    num2.clear()
    num2.send_keys("3.14")
    button.click()
    assert result.text == "Please enter valid numbers"

    # num2 is empty
    num1.clear()
    num2.clear()
    num1.send_keys("5")
    button.click()
    assert result.text == "Please enter valid numbers"


# ----------------------------------------------------------------------
def TestOperations(driver: WebDriver) -> None:
    button = driver.find_element(By.ID, "submitBtn")
    result = driver.find_element(By.ID, "result")
    num1 = driver.find_element(By.ID, "num1")
    num2 = driver.find_element(By.ID, "num2")
    op = Select(driver.find_element(By.ID, "operation"))

    num1.send_keys("10")
    num2.send_keys("2")

    wait = WebDriverWait(driver, 15)

    # Add
    old_value = result.text

    op.select_by_value("add")
    button.click()

    wait.until(lambda d: result.text != old_value and result.text.strip() != "")
    assert result.text == """{"result":12.0}"""

    # Subtract
    old_value = result.text

    op.select_by_value("sub")
    button.click()

    wait.until(lambda d: result.text != old_value and result.text.strip() != "")
    assert result.text == """{"result":8.0}"""

    # Multiply
    old_value = result.text

    op.select_by_value("mult")
    button.click()

    wait.until(lambda d: result.text != old_value and result.text.strip() != "")
    assert result.text == """{"result":20.0}"""

    # Divide
    old_value = result.text

    op.select_by_value("div")
    button.click()

    wait.until(lambda d: result.text != old_value and result.text.strip() != "")
    assert result.text == """{"result":5.0}"""
