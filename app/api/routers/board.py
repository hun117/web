from fastapi import APIRouter, Response, Depends, HTTPException, status
from app.schemas.board import BoardListRes, ReadRes, RegisterReq, RegisterRes
from app.core.security import createToken
from app.db.database import SessionLocal
from app.models.board import Board
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.response import ApiResponse

router = APIRouter(prefix="/board", tags=["board"])

# 제어의 역전 : IoC, 객체 생성이나 프로그램의 실행 흐름의 제어를 외부로 넘기는 프로그래밍 방식
# 의존성 주입 DI 필요한 객체를 우리가 직접 생성하지 않고 외부에서 전달해주는 방식

@router.post("/rergister", response_model=ApiResponse[RegisterRes])
def register(req: RegisterReq, db: Session = Depends(get_db)):
    # db = SessionLocal()

    newBoard = Board(
        title=req.title, contents=req.contents
    )
    db.add(newBoard)
    db.commit()
    db.refresh(newBoard)
    return ApiResponse(code=200, message="게시글이 등록되었습니다.", result=newBoard)

@router.get("/read/{idx}", response_model=ApiResponse[ReadRes])
def read(idx: int, db: Session = Depends(get_db)):
    board = db.get(Board, idx)
    if board is None:
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")
    return ApiResponse(code=200, message="게시글을 조회했습니다.", result=board)


@router.get("/list", response_model=ApiResponse[BoardListRes])
def read_list(db: Session = Depends(get_db)):
    boards = db.scalars(select(Board).order_by(Board.idx.desc())).all()
    result = BoardListRes(items=boards, total=len(boards))
    return ApiResponse(code=200, message="게시글 목록을 조회했습니다.", result=result)

