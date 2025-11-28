from fastapi import APIRouter

router = APIRouter()

@router.post("/stripe/checkout")
def create_checkout_stub():
    # Stub: return a placeholder checkout URL; integrate Stripe later
    return {"checkoutUrl": "https://checkout.stripe.com/pay/demo"}

@router.post("/stripe/webhook")
def stripe_webhook_stub():
    # Stub: accept and return ok; implement signature verify and events later
    return {"received": True}

