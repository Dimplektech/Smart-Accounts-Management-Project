"""
Serializers for the scanner app
"""

from rest_framework import serializers
from .models import Receipt, ReceiptItem


class ReceiptItemSerializer(serializers.ModelSerializer):
    """Serializer for ReceiptItem model"""

    class Meta:
        model = ReceiptItem
        fields = ["id", "name", "quantity", "price", "total"]


class ReceiptSerializer(serializers.ModelSerializer):
    """Serializer for Receipt model"""

    items = ReceiptItemSerializer(many=True, read_only=True)

    class Meta:
        model = Receipt
        fields = [
            "id",
            "image",
            "original_filename",
            "raw_text",
            "parsed_data",
            "status",
            "created_at",
            "updated_at",
            "merchant_name",
            "total_amount",
            "date",
            "tax_amount",
            "items",
        ]
        read_only_fields = [
            "raw_text",
            "parsed_data",
            "status",
            "created_at",
            "updated_at",
            "merchant_name",
            "total_amount",
            "date",
            "tax_amount",
        ]


class ReceiptUploadSerializer(serializers.Serializer):
    """Serializer for receipt upload"""

    image = serializers.ImageField()

    def validate_image(self, value):
        """Validate uploaded image"""
        # Check file size (10MB limit)
        if value.size > 10 * 1024 * 1024:
            raise serializers.ValidationError("Image file too large (>10MB)")

        # Check file type
        if not value.content_type.startswith("image/"):
            raise serializers.ValidationError("File must be an image")

        return value
