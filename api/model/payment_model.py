from typing import Optional
from pydantic import BaseModel


class OrderRequest(BaseModel):
    amount: int
    currency: str

class PaymentVerification(BaseModel):
    member_id: str
    razorpay_payment_id: str
    razorpay_order_id: str
    razorpay_signature: str

class PaymentResponse(BaseModel):
    payment_id: Optional[str] = None
    order_id: Optional[str] = None
    signature: Optional[str] = None
    amount: Optional[int] = None
    date: Optional[str] = None
    time: Optional[str] = None
    status: str
    message: str