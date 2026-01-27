import random
import socket
import threading
import uuid

from typing import Annotated

import typer
import uvicorn
import webview

from dbrownell_Common.Streams.DoneManager import DoneManager, Flags as DoneManagerFlags
from typer.core import TyperGroup

from dbrownell_BrythonWebviewTest.Server import app as server


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
) -> None:
    """Run the app."""

    port = port or _GetUnusedPort()
    token = token or str(uuid.uuid4()).replace("-", "")

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
            f"http://127.0.0.1:{port}/static/main.html",
        )

        webview.start(debug=debug)


# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
def _GetUnusedPort() -> int:
    while True:
        port = random.randint(1024, 65535)  # noqa: S311
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            sock.bind(("127.0.0.1", port))
            sock.close()
            return port
        except OSError:
            pass


# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
if __name__ == "__main__":
    app()  # pragma: no cover
