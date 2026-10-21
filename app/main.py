from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from app.api.routers import board, courses, payments, user
from app.db.database import Base, engine
from app.db.migrations import migrate_user_table
from app.models import Board, Course, SocialAccount, User
from sqlalchemy.orm import Session

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
app.include_router(courses.router)
app.include_router(payments.router)

migrate_user_table(engine)
Base.metadata.create_all(bind=engine)


def seed_courses():
    with Session(engine) as db:
        if db.query(Course).first() is not None:
            return
        db.add_all(
            [
                Course(title="파이썬으로 시작하는 웹 개발", description="파이썬 기초부터 FastAPI로 나만의 웹 API를 만드는 실전 강의입니다.", instructor="김민준", category="개발 · 프로그래밍", price=49000, thumbnail="/static/courses/python-web.svg", level="입문", duration="12시간", rating=4.8),
                Course(title="Vue 3 실전 프런트엔드", description="컴포지션 API와 상태 관리로 사용자에게 사랑받는 화면을 만듭니다.", instructor="김민준", category="개발 · 프로그래밍", price=59000, thumbnail="/static/courses/vue3.svg", level="중급", duration="9시간", rating=4.9),
                Course(title="SQL과 데이터베이스 첫걸음", description="관계형 데이터베이스의 원리를 배우고 SQL로 데이터를 다루는 법을 익힙니다.", instructor="김민준", category="데이터", price=39000, thumbnail="/static/courses/sql.svg", level="입문", duration="7시간", rating=4.7),
            ]
        )
        db.commit()


seed_courses()
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/")
def main():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/{frontend_path:path}")
def frontend_routes(frontend_path: str):
    """Serve the Vue shell for its client-side page routes on direct visits."""
    route = frontend_path.strip("/")
    if route in {"register", "login", "login/kakao/callback", "posts", "posts/new", "learn", "payment/complete"}:
        return FileResponse(STATIC_DIR / "index.html")
    if route.startswith("posts/") and route.removeprefix("posts/").isdigit():
        return FileResponse(STATIC_DIR / "index.html")
    if route.startswith("course/") and route.removeprefix("course/").isdigit():
        return FileResponse(STATIC_DIR / "index.html")
    raise HTTPException(status_code=404, detail="페이지를 찾을 수 없습니다.")
