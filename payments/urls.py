from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('pricing/', views.pricing_page, name='pricing'),
    path('premium-features/', views.premium_features, name='premium_features'),
    path('create-payment-intent/', views.create_payment_intent, name='create_payment_intent'),
    path('success/', views.payment_success, name='success'),
    path('cancel/', views.payment_cancel, name='cancel'),
    path('webhook/', views.stripe_webhook, name='webhook'),
    path('history/', views.payment_history, name='history'),
]
