"""
URL configuration for scanner app
"""

from django.urls import path, include
from . import views


app_name = "scanner"

urlpatterns = [
    path('', views.scanner_home, name='scanner_home'),
    path('upload/', views.upload_receipt, name='upload_receipt'),
    path('history/', views.receipt_history, name='receipt_history'),
    path('receipt/<int:receipt_id>/', views.receipt_detail, name='receipt_detail'),
    path('receipt/<int:receipt_id>/create-transaction/', views.create_transaction_from_receipt, name='create_transaction_from_receipt'),
    path('api/status/', views.scanner_status, name='scanner_status'),
]
