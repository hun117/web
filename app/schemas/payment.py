from pydantic import BaseModel, Field


class CreatePaymentOrderReq(BaseModel):
    course_id: int = Field(gt=0)


class CreatePaymentOrderRes(BaseModel):
    payment_id: str
    order_name: str
    amount: int
    currency: str
    store_id: str
    channel_key: str


class CompletePaymentReq(BaseModel):
    payment_id: str = Field(min_length=6, max_length=64)


class CompletedPurchaseRes(BaseModel):
    payment_id: str
    course_id: int
    course_title: str
    status: str
