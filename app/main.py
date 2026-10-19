from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from app.api.routers import board, user
from app.db.database import Base, engine
from app.models.board import Board
from app.models.user import User

app = FastAPI(title="노트 API", version="0.1.0")
STATIC_DIR = Path(__file__).resolve().parent.parent / "static"


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    message = exc.detail if isinstance(exc.detail, str) else "요청을 처리할 수 없습니다."
    return JSONResponse(
        status_code=exc.status_code,
        content={"code": exc.status_code, "message": message, "result": None},
        headers=exc.headers,
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"code": 422, "message": "요청 값이 올바르지 않습니다.", "result": None},
    )


@app.exception_handler(Exception)
async def unexpected_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"code": 500, "message": "서버 내부 오류가 발생했습니다.", "result": None},
    )

app.include_router(user.router)
app.include_router(board.router)

Base.metadata.create_all(bind=engine)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/")
def main():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/{frontend_path:path}")
def frontend_routes(frontend_path: str):
    """Serve the Vue shell for its client-side page routes on direct visits."""
    route = frontend_path.strip("/")
    if route in {"register", "login", "posts", "posts/new"}:
        return FileResponse(STATIC_DIR / "index.html")
    if route.startswith("posts/") and route.removeprefix("posts/").isdigit():
        return FileResponse(STATIC_DIR / "index.html")
    raise HTTPException(status_code=404, detail="페이지를 찾을 수 없습니다.")
