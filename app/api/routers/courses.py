from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_optional_current_user
from app.db.database import get_db
from app.models import Course, CourseEnrollment, User
from app.schemas.course import CourseList, CourseSummary
from app.schemas.response import ApiResponse

router = APIRouter(prefix="/courses", tags=["courses"])


@router.get("", response_model=ApiResponse[CourseList])
def list_courses(db: Session = Depends(get_db)):
    courses = db.scalars(select(Course).order_by(Course.id)).all()
    return ApiResponse(
        code=200,
        message="강의 목록을 조회했습니다.",
        result=CourseList(items=courses, total=len(courses)),
    )


@router.get("/{course_id}", response_model=ApiResponse[CourseSummary])
def get_course(
    course_id: int,
    db: Session = Depends(get_db),
    user: User | None = Depends(get_optional_current_user),
):
    course = db.get(Course, course_id)
    if course is None:
        raise HTTPException(status_code=404, detail="강의를 찾을 수 없습니다.")
    course.is_enrolled = user is not None and db.scalar(
        select(CourseEnrollment.id).where(
            CourseEnrollment.user_id == user.idx,
            CourseEnrollment.course_id == course.id,
        )
    ) is not None
    return ApiResponse(code=200, message="강의 상세 정보를 조회했습니다.", result=course)
