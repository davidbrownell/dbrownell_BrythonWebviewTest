import sys
from pathlib import Path
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates


# ----------------------------------------------------------------------
if getattr(sys, "frozen", False):
    # When running as a PyInstaller-bundled executable, bundled data files (templates, static assets)
    # are extracted to a temporary directory whose path is stored in sys._MEIPASS. The standard
    # __file__-based resolution doesn't work because the source .py files no longer exist on disk
    # in their original locations.
    _BASE_DIR = Path(sys._MEIPASS) / "dbrownell_BrythonWebviewTest" / "web"  # noqa: SLF001  # ty: ignore[unresolved-attribute]
else:
    _BASE_DIR = Path(__file__).parent

app = FastAPI()

# This value should be set externally
app.state.token: str | None = None

security = HTTPBearer()
templates = Jinja2Templates(directory=_BASE_DIR)


# ----------------------------------------------------------------------
def _ValidateToken(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
) -> str:
    assert app.state.token is not None

    token = credentials.credentials

    if token != app.state.token:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid or missing token",
        )

    return token


# ----------------------------------------------------------------------
app.mount("/static", StaticFiles(directory=_BASE_DIR / "static", html=True))


# ----------------------------------------------------------------------
@app.get("/")
def index() -> object:
    return RedirectResponse("/static/index.html")


# ----------------------------------------------------------------------
@app.get("/index.py")
def index_py(request: Request) -> object:
    if app.state.token is None:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Token validation has not been configured",
        )

    return templates.TemplateResponse(
        "index.jinja2.py",
        {
            "request": request,
            "token": app.state.token,
        },
    )


# ----------------------------------------------------------------------
@app.get("/add")
def add(num1: float, num2: float, _: Annotated[str, Depends(_ValidateToken)]) -> dict:
    return {"result": num1 + num2}


# ----------------------------------------------------------------------
@app.get("/sub")
def sub(num1: float, num2: float, _: Annotated[str, Depends(_ValidateToken)]) -> dict:
    return {"result": num1 - num2}


# ----------------------------------------------------------------------
@app.get("/mult")
def mult(num1: float, num2: float, _: Annotated[str, Depends(_ValidateToken)]) -> dict:
    return {"result": num1 * num2}


# ----------------------------------------------------------------------
@app.get("/div")
def div(num1: float, num2: float, _: Annotated[str, Depends(_ValidateToken)]) -> dict:
    result = "undefined" if num2 == 0.0 else num1 / num2

    return {"result": result}
