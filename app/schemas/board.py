# 조회용 요청 X 게시글 번호로만 요청하면 됨.

# 조회용 응답, 번호, 제목, 내용

# 작성용 요청, 제목, 내용

#작성용 응답  번호, 제목, 내용


from pydantic import BaseModel


class ReadRes(BaseModel):
    idx:      int
    title:    str
    contents: str


class RegisterReq(BaseModel):
    title:    str
    contents: str

class RegisterRes(BaseModel):
    idx   :   int
    title:    str
    contents: str


class BoardListRes(BaseModel):
    items: list[ReadRes]
    total: int



