import stripe
from fastapi import APIRouter, Request, HTTPException

stripe.api_key = "Hi"
router = APIRouter()

@router.post("/create-checkout-session")
async def create_checkout_session(request: Request):
    data = await request.json()
    cart = data.get("cart", [])

    try:
        line_items = []
        for item in cart:
            # Convert percentage discount to final price in cents
            price_after_discount = int(item["price"] * (1 - item["discount"] / 100) * 100)

            line_items.append({
                "price_data": {
                    "currency": "usd",
                    "product_data": {
                        "name": item["name"],
                        "images": [item["image"]] if item.get("image") else [],
                        "metadata": {
                            "brand": item["brand"],
                            "original_price": str(item["price"]),
                            "discount_percent": str(item["discount"]),
                        }
                    },
                    "unit_amount": price_after_discount,
                },
                "quantity": item["quantity"],
            })

        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=line_items,
            mode="payment",
            success_url="http://localhost:5173/checkout/success",
            cancel_url="http://localhost:5173/checkout/failed",
        )

        # ✅ Print session details for debugging
        print("Session created successfully:", session)
        return {"url": session.url}

    except stripe.error.CardError as e:
        # Handle card errors specifically
        print("Card error:", e.error.message)
        raise HTTPException(status_code=400, detail=f"Card error: {e.error.message}")

    except stripe.error.RateLimitError as e:
        # Handle rate limit errors
        print("Rate limit error:", str(e))
        raise HTTPException(status_code=429, detail="Too many requests to Stripe API")

    except stripe.error.InvalidRequestError as e:
        # Handle invalid parameters to Stripe API
        print("Invalid request error:", str(e))
        raise HTTPException(status_code=400, detail="Invalid request to Stripe API")

    except stripe.error.AuthenticationError as e:
        # Handle authentication errors
        print("Authentication error:", str(e))
        raise HTTPException(status_code=401, detail="Authentication with Stripe API failed")

    except stripe.error.APIConnectionError as e:
        # Handle network communication errors
        print("Network error:", str(e))
        raise HTTPException(status_code=503, detail="Network error with Stripe API")

    except stripe.error.StripeError as e:
        # Handle generic Stripe errors
        print("Stripe error:", str(e))
        raise HTTPException(status_code=500, detail="An error occurred with Stripe API")

    except Exception as e:
        # Handle other unexpected errors
        print("Unexpected error:", str(e))
        raise HTTPException(status_code=500, detail="An unexpected error occurred")