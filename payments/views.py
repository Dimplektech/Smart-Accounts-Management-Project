import stripe
import json
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.urls import reverse
from .models import Payment, Subscription, PremiumFeature
from decimal import Decimal
from django.contrib.auth.models import User


def user_has_premium(user):
    """Check if user has premium access"""
    return Payment.objects.filter(
        user=user, status="completed", payment_type="premium_upgrade"
    ).exists()


@login_required
def pricing_page(request):
    print("DEBUG: pricing_page view called!")  # Debug print
    """Display simple pricing plans"""
    plans = [
        {
            "name": "Free",
            "price": 0,
            "features": [
                "Basic Receipt Scanning",
                "Up to 10 receipts/month",
                "Basic expense tracking",
            ],
            "is_free": True,
            "stripe_price_id": "",  # No Stripe price for free plan
        },
        {
            "name": "Premium",
            "price": 9.99,
            "features": [
                "Unlimited Receipt Scanning",
                "Advanced OCR Processing",
                "Expense Analytics",
                "Data Export",
                "Priority Support",
            ],
            "is_free": False,
            "stripe_price_id": "price_premium",  # You can replace with actual Stripe price ID
        },
    ]
    return render(
        request,
        "payments/pricing.html",  # Changed from simple_pricing.html to pricing.html
        {"plans": plans, "stripe_publishable_key": settings.STRIPE_PUBLISHABLE_KEY},
    )


@login_required
def create_payment_intent(request):
    """Create a Stripe Payment Intent"""
    if request.method == "POST":
        try:
            # Set Stripe API key
            stripe.api_key = settings.STRIPE_SECRET_KEY

            data = json.loads(request.body)
            amount = int(float(data.get("amount", 0)) * 100)  # Convert to cents
            payment_type = data.get("payment_type", "premium_upgrade")

            # Create payment intent
            intent = stripe.PaymentIntent.create(
                amount=amount,
                currency="usd",
                metadata={"user_id": request.user.id, "payment_type": payment_type},
            )

            # Create payment record
            payment = Payment.objects.create(
                user=request.user,
                stripe_payment_intent_id=intent.id,
                amount=Decimal(amount / 100),
                payment_type=payment_type,
                description=data.get("description", ""),
            )

            return JsonResponse(
                {"client_secret": intent.client_secret, "payment_id": payment.id}
            )

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"error": "Invalid request method"}, status=405)


@login_required
def payment_success(request):
    """Handle successful payment"""
    payment_intent_id = request.GET.get("payment_intent")
    feature_type = request.GET.get("feature_type")

    if payment_intent_id:
        try:
            payment = Payment.objects.get(stripe_payment_intent_id=payment_intent_id)
            payment.status = "completed"
            payment.save()

            # If it's a premium feature purchase, create the feature record
            if payment.payment_type == "premium_feature" and feature_type:
                # Create or update the premium feature for the user
                premium_feature, created = PremiumFeature.objects.get_or_create(
                    user=request.user,
                    feature=feature_type,
                    defaults={"payment": payment, "is_active": True},
                )

                if not created:
                    # If feature already exists, update it
                    premium_feature.is_active = True
                    premium_feature.payment = payment
                    premium_feature.save()

                messages.success(
                    request,
                    f"Payment completed successfully! You now have access to {premium_feature.get_feature_display()}!",
                )
            else:
                # Regular premium upgrade
                messages.success(
                    request,
                    "Payment completed successfully! You now have premium access!",
                )

        except Payment.DoesNotExist:
            messages.error(request, "Payment not found.")

    return render(request, "payments/success.html")


@login_required
def payment_cancel(request):
    """Handle cancelled payment"""
    messages.info(request, "Payment was cancelled.")
    return render(request, "payments/cancel.html")


@csrf_exempt
@require_POST
def stripe_webhook(request):
    """Handle Stripe webhooks"""
    # Set Stripe API key
    stripe.api_key = settings.STRIPE_SECRET_KEY

    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except ValueError:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        return HttpResponse(status=400)

    # Handle the event
    if event["type"] == "payment_intent.succeeded":
        payment_intent = event["data"]["object"]

        try:
            payment = Payment.objects.get(stripe_payment_intent_id=payment_intent["id"])
            payment.status = "completed"
            payment.save()
        except Payment.DoesNotExist:
            pass

    elif event["type"] == "payment_intent.payment_failed":
        payment_intent = event["data"]["object"]

        try:
            payment = Payment.objects.get(stripe_payment_intent_id=payment_intent["id"])
            payment.status = "failed"
            payment.save()
        except Payment.DoesNotExist:
            pass

    return HttpResponse(status=200)


@login_required
def premium_features(request):
    try:
        print("DEBUG: premium_features view called!")  # Debug print (top)
        # Define available premium features (catalog)
        available_features = [
            {
                "name": "Advanced OCR Processing",
                "description": (
                    "Enhanced text recognition with 99% accuracy "
                    "for all receipt types"
                ),
                "price": 4.99,
                "feature_type": "advanced_ocr",
            },
            {
                "name": "Bulk Receipt Upload",
                "description": (
                    "Upload multiple receipts at once with " "batch processing"
                ),
                "price": 3.99,
                "feature_type": "bulk_upload",
            },
            {
                "name": "Advanced Expense Analytics",
                "description": (
                    "Detailed insights and reports on your " "spending patterns"
                ),
                "price": 5.99,
                "feature_type": "expense_analytics",
            },
            {
                "name": "Data Export Features",
                "description": ("Export your data to PDF, Excel, and " "CSV formats"),
                "price": 2.99,
                "feature_type": "export_data",
            },
            {
                "name": "Priority Customer Support",
                "description": ("Get priority support with faster response " "times"),
                "price": 1.99,
                "feature_type": "priority_support",
            },
        ]

        # Get user's purchased features
        user_features = PremiumFeature.objects.filter(
            user=request.user, is_active=True
        ).values_list("feature", flat=True)

        print(f"Features: {len(available_features)}")  # Debug print
        print(f"User features: {list(user_features)}")  # Debug print

        return render(
            request,
            "payments/premium_features_test.html",
            {
                "features": available_features,
                "user_features": list(user_features),
                "stripe_publishable_key": settings.STRIPE_PUBLISHABLE_KEY,
            },
        )
    except Exception as e:
        import traceback

        print("EXCEPTION in premium_features view:", e)
        traceback.print_exc()
        return render(
            request,
            "payments/premium_features_test.html",
            {"features": [], "user_features": [], "stripe_publishable_key": ""},
        )


@login_required
def payment_history(request):
    """Display user's payment history"""
    payments = Payment.objects.filter(user=request.user)
    return render(request, "payments/history.html", {"payments": payments})
