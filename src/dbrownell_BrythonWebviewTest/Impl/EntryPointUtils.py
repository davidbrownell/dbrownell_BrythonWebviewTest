import random
import secrets
import socket


# ----------------------------------------------------------------------
def GetUnusedPort() -> int:
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
def ResolvePort(port: int | None) -> int:
    return port or GetUnusedPort()


# ----------------------------------------------------------------------
def ResolveToken(token: str | None) -> str:
    return token or secrets.token_urlsafe(32)
