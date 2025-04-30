import stripe
from fastapi import APIRouter, Request

stripe.api_key = 'HI'  # Replace with your Stripe secret key

router = APIRouter()

@router.post("/create-checkout-session")
async def create_checkout_session(request: Request):
    data = await request.json()
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": "usd",
                        "product_data": {
                            "name": data.get("product_name", "Sample Product"),
                        },
                        "unit_amount": data.get("amount", 1000),  # Amount in cents
                    },
                    "quantity": data.get("quantity", 1),
                },
            ],
            mode="payment",
            success_url="http://localhost:5173/checkout/success",
            cancel_url="http://localhost:5173/checkout/failed",
        )
        # ✅ Print session details for debugging
        if session:
            print("Session created successfully:", session)
        return {"url": session.url}
    except Exception as e:
        # Log the error for debugging
        print("Error creating checkout session:", str(e))
        return {"error": str(e)}
