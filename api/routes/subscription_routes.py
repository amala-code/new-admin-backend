from fastapi import APIRouter, HTTPException

from api.model.payment_model import OrderRequest, PaymentResponse, PaymentVerification
from api.services.payment_service import PaymentService

router = APIRouter()
payment_service = PaymentService()

@router.get("/membership-amount")
async def get_membership_amount():
    return {"amount": 600}

@router.post("/create-order")
async def create_order(order_request: OrderRequest):
    try:
        return await payment_service.create_order(order_request)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/verify-payment", response_model=PaymentResponse)
async def verify_payment(payment_data: PaymentVerification):
    return await payment_service.verify_payment(payment_data)