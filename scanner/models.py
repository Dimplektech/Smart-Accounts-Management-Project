from django.db import models
from django.contrib.auth.models import User
import json


class Receipt(models.Model):
    """Model to store receipt information"""

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("processing", "Processing"),
        ("completed", "Completed"),
        ("failed", "Failed"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to="receipts/")
    original_filename = models.CharField(max_length=255)

    # OCR Results
    raw_text = models.TextField(blank=True, null=True)
    parsed_data = models.JSONField(default=dict, blank=True)

    # Status and metadata
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Extracted information
    merchant_name = models.CharField(max_length=255, blank=True, null=True)
    total_amount = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True
    )
    date = models.DateField(blank=True, null=True)
    tax_amount = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Receipt {self.id} - {self.merchant_name or 'Unknown'}"

    def get_parsed_data_pretty(self):
        """Return formatted JSON data"""
        return json.dumps(self.parsed_data, indent=2)


class ReceiptItem(models.Model):
    """Model to store individual items from receipt"""

    receipt = models.ForeignKey(Receipt, on_delete=models.CASCADE, related_name="items")
    name = models.CharField(max_length=255)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.name} - ${self.total}"


