from datetime import datetime, timezone
from uuid import uuid4

import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.config import settings
from app.db.database import get_db
from app.models import Course, CourseEnrollment, PaymentOrder, User
from app.schemas.payment import (
    CompletePaymentReq,
    CompletedPurchaseRes,
    CreatePaymentOrderReq,
    CreatePaymentOrderRes,
)
from app.schemas.response import ApiResponse

router = APIRouter(prefix="/payments", tags=["payments"])
PORTONE_API_BASE_URL = "https://api.portone.io"


def _require_portone_configuration() -> None:
    if not all((settings.PORTONE_STORE_ID, settings.PORTONE_CHANNEL_KEY, settings.PORTONE_API_SECRET)):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="포트원 결제 설정이 완료되지 않았습니다.",
        )


@router.post("/orders", response_model=ApiResponse[CreatePaymentOrderRes])
def create_payment_order(
    req: CreatePaymentOrderReq,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    _require_portone_configuration()
    course = db.get(Course, req.course_id)
    if course is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="강의를 찾을 수 없습니다.")

    enrolled = db.scalar(
        select(CourseEnrollment.id).where(
            CourseEnrollment.user_id == user.idx,
            CourseEnrollment.course_id == course.id,
        )
    )
    if enrolled is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="이미 수강 중인 강의입니다.")

    payment_id = f"course-{uuid4().hex}"
    order = PaymentOrder(
        payment_id=payment_id,
        user_id=user.idx,
        course_id=course.id,
        store_id=settings.PORTONE_STORE_ID,
        amount=course.price,
    )
    db.add(order)
    db.commit()

    return ApiResponse(
        code=200,
        message="결제 주문을 생성했습니다.",
        result=CreatePaymentOrderRes(
            payment_id=payment_id,
            order_name=course.title[:80],
            amount=course.price,
            currency="KRW",
            store_id=settings.PORTONE_STORE_ID,
            channel_key=settings.PORTONE_CHANNEL_KEY,
        ),
    )


@router.post("/complete", response_model=ApiResponse[CompletedPurchaseRes])
def complete_payment(
    req: CompletePaymentReq,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    _require_portone_configuration()
    order = db.scalar(select(PaymentOrder).where(PaymentOrder.payment_id == req.payment_id))
    if order is None or order.user_id != user.idx:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="결제 주문을 찾을 수 없습니다.")

    course = db.get(Course, order.course_id)
    if course is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="강의를 찾을 수 없습니다.")

    if order.status == "PAID":
        return ApiResponse(
            code=200,
            message="이미 결제가 확인되었습니다.",
            result=CompletedPurchaseRes(
                payment_id=order.payment_id,
                course_id=course.id,
                course_title=course.title,
                status=order.status,
            ),
        )

    try:
        response = httpx.get(
            f"{PORTONE_API_BASE_URL}/payments/{order.payment_id}",
            headers={"Authorization": f"PortOne {settings.PORTONE_API_SECRET}"},
            timeout=10.0,
        )
        response.raise_for_status()
        payment = response.json()
    except (httpx.HTTPError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="포트원에서 결제 정보를 확인하지 못했습니다.",
        ) from None

    if not isinstance(payment, dict):
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="포트원 결제 응답을 확인하지 못했습니다.")

    amount = payment.get("amount")
    payment_is_valid = (
        payment.get("id") == order.payment_id
        and payment.get("storeId") == order.store_id
        and payment.get("status") == "PAID"
        and payment.get("currency") == "KRW"
        and isinstance(amount, dict)
        and amount.get("total") == order.amount
    )
    if not payment_is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="결제 상태 또는 금액이 주문 정보와 일치하지 않습니다.",
        )

    enrolled = db.scalar(
        select(CourseEnrollment.id).where(
            CourseEnrollment.user_id == user.idx,
            CourseEnrollment.course_id == course.id,
        )
    )
    if enrolled is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="이미 수강 중인 강의입니다.")

    order.status = "PAID"
    order.paid_at = datetime.now(timezone.utc)
    db.add(CourseEnrollment(user_id=user.idx, course_id=course.id, payment_order_id=order.id))
    db.commit()

    return ApiResponse(
        code=200,
        message="결제가 확인되어 강의 수강이 등록되었습니다.",
        result=CompletedPurchaseRes(
            payment_id=order.payment_id,
            course_id=course.id,
            course_title=course.title,
            status=order.status,
        ),
    )
