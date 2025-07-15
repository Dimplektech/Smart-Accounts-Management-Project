from django.contrib import admin
from .models import Payment, Subscription, PremiumFeature


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = [
        "stripe_payment_intent_id",
        "user",
        "amount",
        "status",
        "payment_type",
        "created_at",
    ]
    list_filter = ["status", "payment_type", "created_at"]
    search_fields = ["stripe_payment_intent_id", "user__username", "user__email"]
    readonly_fields = ["stripe_payment_intent_id", "created_at", "updated_at"]


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ["user", "plan", "status", "current_period_end", "created_at"]
    list_filter = ["plan", "status", "created_at"]
    search_fields = ["user__username", "user__email", "stripe_subscription_id"]
    readonly_fields = [
        "stripe_subscription_id",
        "stripe_customer_id",
        "created_at",
        "updated_at",
    ]


@admin.register(PremiumFeature)
class PremiumFeatureAdmin(admin.ModelAdmin):
    list_display = ["user", "feature", "is_active", "expires_at", "created_at"]
    list_filter = ["feature", "is_active", "created_at"]
    search_fields = ["user__username", "user__email"]
    readonly_fields = ["created_at"]
