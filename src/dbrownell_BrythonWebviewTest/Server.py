from pathlib import Path
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()
app.state.token: str | None = None

security = HTTPBearer()
templates = Jinja2Templates(directory=Path(__file__).parent / "templates")


# ----------------------------------------------------------------------
def ValidateToken(
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
app.mount(
    "/static",
    StaticFiles(directory=Path(__file__).parent / "static"),
)


@app.get("/main.py")
def main_py(request: Request) -> object:
    if app.state.token is None:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Token validation has not been configured",
        )

    return templates.TemplateResponse(
        "main.py",
        {
            "request": request,
            "token": app.state.token,
        },
    )


@app.get("/add")
def add(num1: float, num2: float, _: Annotated[str, Depends(ValidateToken)]) -> dict:
    return {"result": num1 + num2}


@app.get("/sub")
def sub(num1: float, num2: float, _: Annotated[str, Depends(ValidateToken)]) -> dict:
    return {"result": num1 - num2}


@app.get("/mult")
def mult(num1: float, num2: float, _: Annotated[str, Depends(ValidateToken)]) -> dict:
    return {"result": num1 * num2}


@app.get("/div")
def div(num1: float, num2: float, _: Annotated[str, Depends(ValidateToken)]) -> dict:
    result = "undefined" if num2 == 0.0 else num1 / num2

    return {"result": result}
