"""
Views for the scanner app - integrated with Smart Account Management
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from accounts.models import Transaction, Category
from .models import Receipt, ReceiptItem 
from accounts.models import Transaction, Category


@login_required
def scanner_home(request):
    """Scanner home page - shows recent receipts and quick actions"""
    recent_receipts = Receipt.objects.filter(user=request.user)[:5]
    context = {
        'recent_receipts': recent_receipts,
        'total_receipts': Receipt.objects.filter(user=request.user).count(),
        'completed_receipts': Receipt.objects.filter(user=request.user, status='completed').count(),
    }
    return render(request, 'scanner/scanner_home.html', context)

@login_required
def upload_receipt(request):
    """Upload and process receipt with OCR"""
    if request.method == 'POST':
        if 'receipt_image' in request.FILES:
            image_file = request.FILES['receipt_image']
            
            try:
                # Create receipt instance
                receipt = Receipt.objects.create(
                    user=request.user,
                    image=image_file,
                    original_filename=image_file.name,
                    status='processing'
                )
                
                try:
                    # Try OCR processing
                    from .ocr_service import ReceiptOCRService
                    ocr_service = ReceiptOCRService()
                    result = ocr_service.process_receipt(receipt.image.path)
                    
                    if result:
                        # Convert date object to string for JSON storage
                        if result.get('date') and hasattr(result['date'], 'strftime'):
                            result['date'] = result['date'].strftime('%Y-%m-%d')
                        
                        # Update receipt with OCR results
                        receipt.raw_text = result.get('raw_text', '')
                        receipt.parsed_data = result  # Now safe for JSON
                        receipt.merchant_name = result.get('merchant_name')
                        receipt.total_amount = result.get('total_amount')
                        
                        # Handle date field separately
                        if result.get('date'):
                            from datetime import datetime
                            try:
                                if isinstance(result['date'], str):
                                    receipt.date = datetime.strptime(result['date'], '%Y-%m-%d').date()
                                else:
                                    receipt.date = result['date']
                            except:
                                receipt.date = None
                        
                        receipt.tax_amount = result.get('tax_amount')
                        receipt.status = 'completed'
                        receipt.save()
                        
                        # Create receipt items
                        items = result.get('items', [])
                        for item_data in items:
                            ReceiptItem.objects.create(
                                receipt=receipt,
                                name=item_data.get('name', ''),
                                quantity=item_data.get('quantity', 1),
                                price=item_data.get('price', 0),
                                total=item_data.get('total', 0),
                            )
                        
                        messages.success(request, f'Receipt processed with OCR! Found: {receipt.merchant_name or "Unknown merchant"}')
                    else:
                        receipt.status = 'failed'
                        receipt.save()
                        messages.warning(request, 'OCR processing failed, but receipt saved.')
                        
                except Exception as ocr_error:
                    receipt.status = 'failed'
                    receipt.save()
                    messages.warning(request, f'OCR error: {str(ocr_error)}. Receipt saved without processing.')
                
                return redirect('scanner:receipt_detail', receipt_id=receipt.id)
                    
            except Exception as e:
                messages.error(request, f'Error uploading receipt: {str(e)}')
                return redirect('scanner:upload_receipt')
        else:
            messages.error(request, 'Please select a receipt image to upload.')
    
    return render(request, 'scanner/upload_receipt.html')


@login_required
def receipt_history(request):
    """Receipt history view - shows all user's receipts"""
    receipts = Receipt.objects.filter(user=request.user).order_by('-created_at')
    context = {
        'receipts': receipts,
    }
    return render(request, 'scanner/receipt_history.html', context)


@login_required
def receipt_detail(request, receipt_id):
    """View individual receipt details"""
    receipt = get_object_or_404(Receipt, id=receipt_id, user=request.user)
    context = {
        'receipt': receipt,
        'items': receipt.items.all(),
    }
    return render(request, 'scanner/receipt_detail.html', context)

@login_required
def create_transaction_from_receipt(request, receipt_id):
    """Convert a receipt to a transaction"""
    receipt = get_object_or_404(Receipt, id=receipt_id, user=request.user)
    
    # Check if receipt is ready for transaction creation
    if receipt.status != 'completed':
        messages.error(request, "This receipt hasn't been processed yet. Please wait for OCR processing to complete.")
        return redirect('scanner:receipt_detail', receipt_id=receipt_id)
    
    if not receipt.total_amount:
        messages.error(request, "No amount detected in this receipt. Please add the transaction manually.")
        return redirect('accounts:add_transaction')
    
    try:
        # Check if transaction already exists for this receipt
        existing_transaction = Transaction.objects.filter(
            notes__contains=f"receipt #{receipt.id}"
        ).first()
        
        if existing_transaction:
            messages.warning(request, "A transaction has already been created from this receipt.")
            return redirect('accounts:transaction_list')
        
        # Import the models we need
        from accounts.models import Category, Category_type, Account
        
        # Get or create the "Expense" category type
        expense_type, created = Category_type.objects.get_or_create(name='expense')
        
        # Try to find or create a category for receipts
        category, created = Category.objects.get_or_create(
            name='Scanned Receipt',
            user=request.user,
            category_type=expense_type,
            defaults={
                'color': '#dc3545',  # Red color for expenses
                'icon': 'fas fa-receipt',
                'description': 'Auto-created category for scanned receipts'
            }
        )
        
        # Get user's first account (or create logic for account selection)
        account = Account.objects.filter(user=request.user, is_active=True).first()
        
        if not account:
            messages.error(request, "No active account found. Please create an account first.")
            return redirect('accounts:account_list')
        
        # Prepare transaction description
        description = f"Receipt from {receipt.merchant_name or 'Unknown Merchant'}"
        if receipt.date:
            description += f" on {receipt.date.strftime('%d/%m/%Y')}"
        
        # Prepare transaction notes
        notes_parts = [f"Auto-created from scanned receipt #{receipt.id}"]
        
        if receipt.tax_amount:
            notes_parts.append(f"Tax: £{receipt.tax_amount}")
        
        if receipt.items.exists():
            item_count = receipt.items.count()
            notes_parts.append(f"Items: {item_count}")
            
            # Add first few items to notes
            items = receipt.items.all()[:3]
            item_names = [item.name for item in items if item.name]
            if item_names:
                notes_parts.append(f"Items: {', '.join(item_names)}")
        
        notes = ". ".join(notes_parts)
        
        # Create transaction from receipt
        transaction = Transaction.objects.create(
            user=request.user,
            account=account,
            category=category,
            description=description,
            amount=receipt.total_amount,
            transaction_type='expense',
            payment_methods='other',  # Since it's from a receipt
            date=receipt.date or receipt.created_at,
            notes=notes
        )
        
        # Success message with details
        success_msg = f"✅ Transaction created successfully! Amount: £{receipt.total_amount}"
        if receipt.merchant_name:
            success_msg += f" from {receipt.merchant_name}"
        
        messages.success(request, success_msg)
        return redirect('accounts:transaction_list')
        
    except Exception as e:
        messages.error(request, f"Error creating transaction: {str(e)}")
        return redirect('scanner:receipt_detail', receipt_id=receipt_id)


   
@login_required
def scanner_status(request):
    """API endpoint to check scanner status"""
    return JsonResponse({
        'scanner_available': False,  # Set to False until OCR is working
        'message': 'Scanner functionality coming soon!'
    })