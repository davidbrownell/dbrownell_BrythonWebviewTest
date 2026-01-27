import threading

from typing import Annotated

import typer
import uvicorn
import webview

from dbrownell_Common.Streams.DoneManager import DoneManager, Flags as DoneManagerFlags
from typer.core import TyperGroup

from dbrownell_BrythonWebviewTest.Impl import EntryPointUtils
from dbrownell_BrythonWebviewTest.web.Server import app as server


# ----------------------------------------------------------------------
class NaturalOrderGrouper(TyperGroup):  # noqa: D101
    # ----------------------------------------------------------------------
    def list_commands(self, *args, **kwargs) -> list[str]:  # noqa: ARG002, D102
        return list(self.commands.keys())  # pragma: no cover


# ----------------------------------------------------------------------
app = typer.Typer(
    cls=NaturalOrderGrouper,
    help=__doc__,
    no_args_is_help=True,
    pretty_exceptions_show_locals=False,
    pretty_exceptions_enable=False,
)


# ----------------------------------------------------------------------
@app.command("EntryPoint", no_args_is_help=False)
def EntryPoint(
    port: Annotated[
        int | None,
        typer.Option("--port", min=1024, max=65535, help="The port to run the server on."),
    ] = None,
    token: Annotated[
        str | None,
        typer.Option("--token", help="The token required to access protected endpoints."),
    ] = None,
    verbose: Annotated[  # noqa: FBT002
        bool,
        typer.Option("--verbose", help="Write verbose information to the terminal."),
    ] = False,
    debug: Annotated[  # noqa: FBT002
        bool,
        typer.Option("--debug", help="Write debug information to the terminal."),
    ] = False,
    debug_port: Annotated[
        int | None,
        typer.Option("--debug-port", min=1024, max=65535, help="The debug port used with the server."),
    ] = None,
) -> None:
    """Run the app."""

    port = EntryPointUtils.ResolvePort(port)
    token = EntryPointUtils.ResolveToken(token)

    if debug_port is not None:
        if not debug:
            msg = "'--debug' must be specified when using '--debug-port'."
            raise typer.BadParameter(msg)

        webview.settings["REMOTE_DEBUGGING_PORT"] = debug_port

    with DoneManager.CreateCommandLine(
        flags=DoneManagerFlags.Create(verbose=verbose, debug=debug),
    ):
        server.state.token = token

        t = threading.Thread(
            target=uvicorn.run,
            args=(server,),
            daemon=True,
            kwargs={"host": "127.0.0.1", "port": port},
        )

        t.start()

        webview.create_window(
            "Brython Webview Test",
            f"http://127.0.0.1:{port}/",
        )

        webview.start(debug=debug)


# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
if __name__ == "__main__":
    app()  # pragma: no cover
