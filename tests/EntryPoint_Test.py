from typing import Any, Mapping
from unittest.mock import Mock

from click.testing import Result
from _pytest.monkeypatch import MonkeyPatch
from typer.testing import CliRunner

from dbrownell_BrythonWebviewTest.EntryPoint import app


# ----------------------------------------------------------------------
def test_NoArgs(monkeypatch: MonkeyPatch) -> None:
    result, threading, webview = _Execute(monkeypatch, [])

    assert threading is not None
    assert webview is not None

    assert threading["kwargs"]["host"] == "127.0.0.1"
    assert (
        webview[1] == f"http://{threading['kwargs']['host']}:{threading['kwargs']['port']}/static/main.html"
    )


# ----------------------------------------------------------------------
def test_Port(monkeypatch: MonkeyPatch) -> None:
    result, threading, webview = _Execute(monkeypatch, ["--port", "12345"])

    assert threading is not None
    assert webview is not None

    assert threading["kwargs"]["port"] == 12345
    assert (
        webview[1] == f"http://{threading['kwargs']['host']}:{threading['kwargs']['port']}/static/main.html"
    )


# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
def _Execute(
    monkeypatch: MonkeyPatch,
    args: list[str],
    *,
    expect_failure: bool = False,
) -> tuple[Result, Mapping[str, Any] | None, tuple[Any, ...] | None]:
    threading_mock = Mock()
    webview_mock = Mock()

    monkeypatch.setattr("dbrownell_BrythonWebviewTest.EntryPoint.threading", threading_mock)
    monkeypatch.setattr("dbrownell_BrythonWebviewTest.EntryPoint.webview", webview_mock)

    result = CliRunner().invoke(app, args)

    if expect_failure:
        assert result.exit_code != 0, result.stdout
        return result, None, None

    assert result.exit_code == 0, result.stdout
    return result, threading_mock.mock_calls[0].kwargs, webview_mock.mock_calls[0].args
