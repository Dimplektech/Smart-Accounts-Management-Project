"""
OCR service for processing receipt images using Tesseract OCR
"""

import cv2
import pytesseract
import numpy as np
from PIL import Image
import re
from decimal import Decimal
from datetime import datetime
import json


class ReceiptOCRService:
    """Service class for OCR processing of receipts"""

    def __init__(self):
        # Configure tesseract path for Windows
        try:
            # Try common installation paths
            import platform

            if platform.system() == "Windows":
                import os

                possible_paths = [
                    r"C:\Program Files\Tesseract-OCR\tesseract.exe",
                    r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
                    r"C:\Tesseract-OCR\tesseract.exe",
                ]

                for path in possible_paths:
                    if os.path.exists(path):
                        pytesseract.pytesseract.tesseract_cmd = path
                        break
        except Exception as e:
            print(f"Warning: Could not configure Tesseract path: {e}")
            print("Please ensure Tesseract is installed and accessible")

    def preprocess_image(self, image_path):
        """Preprocess image for better OCR results"""
        try:
            # Read image
            image = cv2.imread(str(image_path))

            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            # Apply threshold to get image with only black and white
            _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

            return thresh
        except Exception as e:
            print(f"Error in image preprocessing: {e}")
            # Fallback: return original image path for direct OCR
            return str(image_path)

    def extract_text(self, image_path):
        """Extract text from receipt image using OCR"""
        try:
            # Try to preprocess image first
            processed_image = self.preprocess_image(image_path)

            if isinstance(processed_image, str):
                # Fallback: use original image directly
                pil_image = Image.open(processed_image)
            else:
                # Convert preprocessed image back to PIL Image for tesseract
                pil_image = Image.fromarray(processed_image)

            # Perform OCR with different PSM modes for better results
            configs = [
                "--psm 6",  # Single uniform block of text
                "--psm 4",  # Single column of text
                "--psm 3",  # Fully automatic page segmentation
            ]

            text = ""
            for config in configs:
                try:
                    text = pytesseract.image_to_string(pil_image, config=config)
                    if text.strip():  # If we got some text, use it
                        break
                except:
                    continue

            return text.strip()
        except Exception as e:
            print(f"Error extracting text: {str(e)}")
            return ""

    def parse_receipt_data(self, text):
        """Parse extracted text to extract structured data"""
        data = {
            "merchant_name": self.extract_merchant_name(text),
            "total_amount": self.extract_total_amount(text),
            "date": self.extract_date(text),
            "tax_amount": self.extract_tax_amount(text),
            "items": self.extract_items(text),
            "raw_text": text,
        }
        return data

    def extract_merchant_name(self, text):
        """Extract merchant name from receipt text"""
        lines = text.split("\n")

        # Skip common header phrases
        skip_phrases = [
            "thank you for shopping at",
            "thank you for shopping",
            "welcome to",
            "customer receipt",
            "receipt",
            "till receipt",
        ]

        # Look for merchant name in the first several lines
        for line in lines[:8]:  # Check first 8 lines instead of 5
            line = line.strip()
            line_lower = line.lower()

            # Skip empty lines and common phrases
            if len(line) < 3:
                continue

            # Skip lines that start with digits (dates, numbers)
            if re.match(r"^\d", line):
                continue

            # Skip common header phrases
            if any(phrase in line_lower for phrase in skip_phrases):
                continue

            # Skip lines with long numbers (phone, VAT reg, etc.)
            if re.search(r"\d{6,}", line):
                continue

            # Skip lines that are mostly punctuation or symbols
            if len(re.sub(r"[^a-zA-Z\s]", "", line)) < 3:
                continue

            # Look for common business indicators
            business_indicators = [
                "ltd",
                "limited",
                "inc",
                "corp",
                "company",
                "express",
                "store",
                "shop",
                "market",
            ]
            if any(indicator in line_lower for indicator in business_indicators):
                return line

            # If it's a reasonable length and has letters, it might be the merchant
            if 5 <= len(line) <= 50 and re.search(r"[a-zA-Z]", line):
                # Additional check - skip if it contains common non-merchant words
                non_merchant_words = [
                    "address",
                    "phone",
                    "tel:",
                    "vat",
                    "reg",
                    "no.",
                    "site",
                    "id",
                ]
                if not any(word in line_lower for word in non_merchant_words):
                    return line

        return None

    def extract_total_amount(self, text):
        """Extract total amount from receipt text"""
        lines = text.split("\n")

        # Look for VAT breakdown lines first (most accurate for UK receipts)
        for line in lines:
            # Pattern: "20.00% 64.91 12.98 77.89" - last number is VAT-inclusive total
            vat_breakdown_match = re.search(
                r"(\d+\.?\d*)%\s+(\d+[.,]\d{2})\s+(\d+[.,]\d{2})\s+(\d+[.,]\d{2})", line
            )
            if vat_breakdown_match:
                # Fourth number is the VAT-inclusive total
                total_amount = vat_breakdown_match.group(4).replace(",", ".")
                try:
                    return float(total_amount)
                except ValueError:
                    continue

        # First approach: Look for lines with "TOTAL" and currency
        for line in lines:
            line_clean = line.strip().lower()
            if "total" in line_clean and "subtotal" not in line_clean:
                # Look for currency amounts in the line
                currency_matches = re.findall(r"[\$£€]\s*(\d+[.,]\d{2})", line)
                if currency_matches:
                    try:
                        amount_str = currency_matches[-1].replace(",", ".")
                        return float(amount_str)
                    except ValueError:
                        continue

        # Second approach: Look for payment method lines (VISA, CARD, etc.)
        # which often show the total amount
        payment_keywords = ["visa", "mastercard", "card", "cash", "paid"]
        for line in lines:
            line_clean = line.strip().lower()
            for keyword in payment_keywords:
                if keyword in line_clean:
                    currency_matches = re.findall(r"[\$£€]\s*(\d+[.,]\d{2})", line)
                    if currency_matches:
                        try:
                            amount_str = currency_matches[-1].replace(",", ".")
                            return float(amount_str)
                        except ValueError:
                            continue

        # Third approach: Look for the largest amount in the receipt
        # (often the total is the largest single amount)
        all_amounts = []
        for line in lines:
            currency_matches = re.findall(r"[\$£€]\s*(\d+[.,]\d{2})", line)
            for match in currency_matches:
                try:
                    amount_str = match.replace(",", ".")
                    amount = float(amount_str)
                    all_amounts.append(amount)
                except ValueError:
                    continue

        if all_amounts:
            # Return the largest amount (likely the total)
            return max(all_amounts)

        # Pattern-based approach as final fallback
        patterns = [
            r"(?<!sub)total[:\s]*[\$£€]?\s*(\d+[.,]\d{2})",
            r"grand\s*total[:\s]*[\$£€]?\s*(\d+[.,]\d{2})",
            r"final[:\s]*[\$£€]?\s*(\d+[.,]\d{2})",
            r"balance[:\s]*[\$£€]?\s*(\d+[.,]\d{2})",
        ]

        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE | re.MULTILINE)
            if matches:
                try:
                    amount_str = matches[-1].replace(",", ".")
                    return float(amount_str)
                except ValueError:
                    continue
        return None

    def extract_date(self, text):
        """Extract date from receipt text"""
        # Common date patterns - more comprehensive with DD-MM-YYYY support
        date_patterns = [
            r"date[:/\s]*(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})",  # DATE: DD/MM/YYYY
            r"(\d{1,2}[-/]\d{1,2}[-/]\d{4})",  # DD/MM/YYYY or MM/DD/YYYY
            r"(\d{4}[-/]\d{1,2}[-/]\d{1,2})",  # YYYY/MM/DD
            r"(\d{1,2}[-/]\d{1,2}[-/]\d{2})",  # DD/MM/YY or MM/DD/YY
            r"time:\s*(\d{1,2}[-/]\d{1,2}[-/]\d{4})",  # After "time:" keyword
        ]

        # First try to find dates in lines containing 'date' or 'time'
        lines = text.split("\n")
        for line in lines:
            line_lower = line.strip().lower()
            if "date" in line_lower or "time" in line_lower:
                # Look for date patterns in this line
                for pattern in date_patterns:
                    matches = re.findall(pattern, line, re.IGNORECASE)
                    if matches:
                        try:
                            date_str = matches[0]
                            # Clean up the date string
                            date_str = date_str.replace(",", "").strip()

                            # Try different date formats, prioritizing DD/MM/YYYY for European format
                            formats = [
                                "%d/%m/%Y",  # DD/MM/YYYY (European - try first)
                                "%d-%m-%Y",  # DD-MM-YYYY (European with dashes)
                                "%m/%d/%Y",  # MM/DD/YYYY (US format)
                                "%m-%d-%Y",  # MM-DD-YYYY (US with dashes)
                                "%Y-%m-%d",  # YYYY-MM-DD (ISO format)
                                "%d/%m/%y",  # DD/MM/YY (European 2-digit year)
                                "%d-%m-%y",  # DD-MM-YY (European 2-digit year)
                                "%m/%d/%y",  # MM/DD/YY (US 2-digit year)
                                "%m-%d-%y",  # MM-DD-YY (US 2-digit year)
                                "%y-%m-%d",  # YY-MM-DD
                            ]

                            for fmt in formats:
                                try:
                                    parsed_date = datetime.strptime(date_str, fmt)
                                    # Handle 2-digit years
                                    if parsed_date.year < 50:
                                        parsed_date = parsed_date.replace(
                                            year=parsed_date.year + 2000
                                        )
                                    elif parsed_date.year < 100:
                                        parsed_date = parsed_date.replace(
                                            year=parsed_date.year + 1900
                                        )
                                    return parsed_date.date()
                                except ValueError:
                                    continue
                        except Exception:
                            continue

        # Fallback: search entire text with DD/MM priority
        for pattern in date_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                try:
                    date_str = matches[0].replace(",", "").strip()
                    # Try DD/MM formats first for European receipts
                    formats = [
                        "%d/%m/%Y",
                        "%d-%m-%Y",
                        "%m/%d/%Y",
                        "%m-%d-%Y",
                        "%Y-%m-%d",
                    ]
                    for fmt in formats:
                        try:
                            return datetime.strptime(date_str, fmt).date()
                        except ValueError:
                            continue
                except Exception:
                    continue
        return None

    def extract_tax_amount(self, text):
        """Extract tax amount from receipt text"""

        # Look for VAT/tax patterns in lines
        lines = text.split("\n")

        # First approach: Look for lines with VAT breakdown (like "64.91 12.98 77.89")
        for line in lines:
            line_clean = line.strip().lower()

            # Look for lines with VAT rate and amounts (e.g., "20.00% 64.91 12.98 77.89")
            vat_breakdown_match = re.search(
                r"(\d+\.?\d*)%\s+(\d+[.,]\d{2})\s+(\d+[.,]\d{2})\s+(\d+[.,]\d{2})", line
            )
            if vat_breakdown_match:
                # Third number is usually the VAT amount
                vat_amount = vat_breakdown_match.group(3).replace(",", ".")
                try:
                    return float(vat_amount)
                except ValueError:
                    continue

            # Look for explicit VAT lines
            if "vat" in line_clean or "tax" in line_clean:
                # Find currency amounts in VAT lines
                currency_matches = re.findall(r"[\$£€]?\s*(\d+[.,]\d{2})", line)
                if currency_matches:
                    try:
                        # Handle both . and , as decimal separators
                        amount_str = currency_matches[-1].replace(",", ".")
                        return float(amount_str)
                    except ValueError:
                        continue

        # Fallback: Standard tax/VAT patterns
        patterns = [
            r"vat[:\s]*[\$£€]?\s*(\d+[.,]?\d*)",
            r"tax[:\s]*[\$£€]?\s*(\d+[.,]?\d*)",
            r"gst[:\s]*[\$£€]?\s*(\d+[.,]?\d*)",
        ]

        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                try:
                    # Handle both . and , as decimal separators
                    amount_str = matches[-1].replace(",", ".")
                    return float(amount_str)
                except ValueError:
                    continue
        return None

    def extract_items(self, text):
        """Extract individual items from receipt text"""
        items = []
        lines = text.split("\n")

        for line in lines:
            line = line.strip()
            # Look for lines with item name and price (support multiple currencies)
            # Pattern: item name followed by price
            price_match = re.search(r"[\$£€]?\s*(\d+[.,]\d{2})$", line)
            if price_match:
                try:
                    # Handle both . and , as decimal separators
                    price_str = price_match.group(1).replace(",", ".")
                    price = float(price_str)
                    # Extract item name (everything before the price)
                    item_name = re.sub(
                        r"\s*[\$£€]?\s*\d+[.,]\d{2}\s*$", "", line
                    ).strip()
                    if item_name and len(item_name) > 1:
                        items.append(
                            {
                                "name": item_name,
                                "price": price,
                                "quantity": 1,
                                "total": price,
                            }
                        )
                except ValueError:
                    continue

        return items

    def process_receipt(self, image_path):
        """Complete pipeline to process a receipt image"""
        try:
            # Extract text using OCR
            raw_text = self.extract_text(image_path)

            if not raw_text:
                return None

            # Parse the extracted text
            parsed_data = self.parse_receipt_data(raw_text)

            return parsed_data

        except Exception as e:
            print(f"Error processing receipt: {str(e)}")
            return None
