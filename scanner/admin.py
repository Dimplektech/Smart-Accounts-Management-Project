from django.contrib import admin
from .models import Receipt, ReceiptItem


@admin.register(Receipt)
class ReceiptAdmin(admin.ModelAdmin):
    """Admin interface for Receipt model"""

    list_display = [
        "id",
        "merchant_name",
        "total_amount",
        "date",
        "status",
        "created_at",
    ]
    list_filter = ["status", "created_at", "date"]
    search_fields = ["merchant_name", "original_filename"]
    readonly_fields = ["created_at", "updated_at", "raw_text", "parsed_data"]

    fieldsets = (
        (
            "Basic Information",
            {"fields": ("user", "image", "original_filename", "status")},
        ),
        (
            "Extracted Data",
            {"fields": ("merchant_name", "total_amount", "date", "tax_amount")},
        ),
        (
            "OCR Results",
            {"fields": ("raw_text", "parsed_data"), "classes": ("collapse",)},
        ),
        (
            "Timestamps",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )


@admin.register(ReceiptItem)
class ReceiptItemAdmin(admin.ModelAdmin):
    """Admin interface for ReceiptItem model"""

    list_display = ["receipt", "name", "quantity", "price", "total"]
    list_filter = ["receipt__created_at"]
    search_fields = ["name", "receipt__merchant_name"]
