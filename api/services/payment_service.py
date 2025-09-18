import datetime
import hashlib
import hmac
from fastapi import HTTPException

from conf import RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET, client
from model.payment_model import OrderRequest, PaymentResponse, PaymentVerification
from utils.db import members_collection

class PaymentService:
    
    async def create_order(self, order_request: OrderRequest):
        # Create order data
        order_data = {
            'amount': order_request.amount * 100,  # Convert to paise
            'currency': order_request.currency,
            'receipt': f'receipt_{order_request.amount}',
            'payment_capture': 1  # Auto capture payment
        }
        
        # Create order using Razorpay
        order = client.order.create(data=order_data)
        
        return {
            "order_id": order['id'],
            "amount": order['amount'],
            "currency": order['currency'],
            "key_id": RAZORPAY_KEY_ID
        }
    
    async def verify_payment(self, payment_data: PaymentVerification):
        try:
            # Verify signature
            generated_signature = hmac.new(
                RAZORPAY_KEY_SECRET.encode('utf-8'),
                (payment_data.razorpay_order_id + "|" + payment_data.razorpay_payment_id).encode('utf-8'),
                hashlib.sha256
            ).hexdigest()
            
            if generated_signature == payment_data.razorpay_signature:
                # Payment is verified
                # Fetch payment details
                payment_details = client.payment.fetch(payment_data.razorpay_payment_id)
                
                timestamp = datetime.datetime.now().strftime("%b %d, %Y, %H:%M:%S")
                date = datetime.datetime.now().strftime("%b %d, %Y")
                time = datetime.datetime.now().strftime("%H:%M:%S")

                result = members_collection.update_one({"id": payment_data.member_id}, {"$inc": {"amount_paid_total": payment_details["amount"] / 100}, "$set": {"amount_subscription": True, "amount_paid_subscription": payment_details['amount'] / 100, "transaction_id": payment_data.razorpay_payment_id, "date_of_subscription": timestamp}})

                if result.matched_count == 0:
                    raise HTTPException(status_code=404, detail=f"Member with id '{payment_data.member_id}' not found.")

                # Store payment details in your database here
                # save_payment_to_database(payment_details)
                
                return PaymentResponse(
                    payment_id=payment_data.razorpay_payment_id,
                    order_id=payment_data.razorpay_order_id,
                    signature=payment_data.razorpay_signature,
                    amount=payment_details['amount'],
                    date=date,
                    time=time,
                    status="success",
                    message="Payment verified successfully"
                )
            else:
                return PaymentResponse(
                    status="failed",
                    message="Payment verification failed - Invalid signature"
                )
        
        except Exception as e:
            return PaymentResponse(
                status="error",
                message=f"Error verifying payment: {str(e)}"
            )