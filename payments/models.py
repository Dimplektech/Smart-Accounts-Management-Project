from django.db import models
from django.contrib.auth.models import User


class Payment(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    
    PAYMENT_TYPE_CHOICES = [
        ('subscription', 'Subscription'),
        ('one_time', 'One Time Payment'),
        ('premium_feature', 'Premium Feature'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    stripe_payment_intent_id = models.CharField(max_length=255, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPE_CHOICES, default='one_time')
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Payment {self.stripe_payment_intent_id} - {self.user.username} - ${self.amount}"


class Subscription(models.Model):
    SUBSCRIPTION_STATUS_CHOICES = [
        ('active', 'Active'),
        ('canceled', 'Canceled'),
        ('past_due', 'Past Due'),
        ('unpaid', 'Unpaid'),
        ('trialing', 'Trialing'),
    ]
    
    PLAN_CHOICES = [
        ('basic', 'Basic Plan - $9.99/month'),
        ('premium', 'Premium Plan - $19.99/month'),
        ('pro', 'Pro Plan - $29.99/month'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='subscription')
    stripe_subscription_id = models.CharField(max_length=255, unique=True)
    stripe_customer_id = models.CharField(max_length=255)
    plan = models.CharField(max_length=20, choices=PLAN_CHOICES)
    status = models.CharField(max_length=20, choices=SUBSCRIPTION_STATUS_CHOICES, default='active')
    current_period_start = models.DateTimeField()
    current_period_end = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.plan} ({self.status})"


class PremiumFeature(models.Model):
    FEATURE_CHOICES = [
        ('advanced_ocr', 'Advanced OCR Processing'),
        ('bulk_upload', 'Bulk Receipt Upload'),
        ('expense_analytics', 'Advanced Expense Analytics'),
        ('export_data', 'Data Export Features'),
        ('priority_support', 'Priority Customer Support'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='premium_features')
    feature = models.CharField(max_length=30, choices=FEATURE_CHOICES)
    is_active = models.BooleanField(default=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='features')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'feature']
    
    def __str__(self):
        return f"{self.user.username} - {self.get_feature_display()}"
