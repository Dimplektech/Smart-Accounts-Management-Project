// accounts/static/accounts/js/add_transaction.js

document.addEventListener('DOMContentLoaded', function() {
    console.log('💰 Transaction Form Loading...');
    
    initializeTransactionForm();
    setupFormValidation();
    setupKeyboardShortcuts();
    
    console.log('✅ Transaction Form Ready!');
});

function initializeTransactionForm() {
    const form = document.getElementById('transactionForm');
    const transactionTypeSelect = document.querySelector('select[name="transaction_type"]');
    const amountInput = document.querySelector('input[name="amount"]');
    const dateInput = document.querySelector('input[name="date"]');
    
    // Set today's date as default
    if (dateInput && !dateInput.value) {
        dateInput.value = new Date().toISOString().split('T')[0];
    }
    
    // Add slide-in animation
    const card = document.querySelector('.transaction-card');
    if (card) {
        card.classList.add('slide-in');
    }
    
    // Transaction type change handler
    if (transactionTypeSelect) {
        transactionTypeSelect.addEventListener('change', handleTransactionTypeChange);
        // Trigger on page load if value exists
        if (transactionTypeSelect.value) {
            handleTransactionTypeChange.call(transactionTypeSelect);
        }
    }
    
    // Amount input formatting
    if (amountInput) {
        amountInput.addEventListener('blur', formatAmountInput);
        amountInput.addEventListener('input', updateAmountIndicator);
    }
    
    // Form submission handler
    if (form) {
        form.addEventListener('submit', handleFormSubmission);
    }
}

function handleTransactionTypeChange() {
    const transactionType = this.value;
    const submitBtn = document.querySelector('button[type="submit"]');
    const card = document.querySelector('.transaction-card');
    const amountGroup = document.querySelector('.amount-input-group');
    const amountIndicator = document.querySelector('.amount-indicator');
    
    // Remove existing type classes
    card.classList.remove('transaction-type-income', 'transaction-type-expense', 'transaction-type-transfer');
    
    // Update submit button and styling based on type
    switch(transactionType) {
        case 'income':
            submitBtn.className = 'btn btn-success-transaction';
            submitBtn.innerHTML = '<i class="fas fa-save me-1"></i>Save Income';
            card.classList.add('transaction-type-income');
            if (amountIndicator) {
                amountIndicator.className = 'amount-indicator income';
                amountIndicator.innerHTML = '💰';
            }
            break;
            
        case 'expense':
            submitBtn.className = 'btn btn-danger-transaction';
            submitBtn.innerHTML = '<i class="fas fa-save me-1"></i>Save Expense';
            card.classList.add('transaction-type-expense');
            if (amountIndicator) {
                amountIndicator.className = 'amount-indicator expense';
                amountIndicator.innerHTML = '💸';
            }
            break;
            
        case 'transfer':
            submitBtn.className = 'btn btn-info-transaction';
            submitBtn.innerHTML = '<i class="fas fa-save me-1"></i>Save Transfer';
            card.classList.add('transaction-type-transfer');
            if (amountIndicator) {
                amountIndicator.className = 'amount-indicator transfer';
                amountIndicator.innerHTML = '🔄';
            }
            break;
            
        default:
            submitBtn.className = 'btn btn-primary-transaction';
            submitBtn.innerHTML = '<i class="fas fa-save me-1"></i>Save Transaction';
            if (amountIndicator) {
                amountIndicator.className = 'amount-indicator';
                amountIndicator.innerHTML = '💵';
            }
    }
}

function formatAmountInput() {
    if (this.value && !isNaN(this.value)) {
        this.value = parseFloat(this.value).toFixed(2);
    }
}

function updateAmountIndicator() {
    const amountIndicator = document.querySelector('.amount-indicator');
    const amount = parseFloat(this.value);
    
    if (amountIndicator && !isNaN(amount)) {
        amountIndicator.style.opacity = amount > 0 ? '1' : '0.7';
        amountIndicator.style.transform = amount > 0 ? 'translateY(-50%) scale(1.1)' : 'translateY(-50%) scale(1)';
    }
}

function setupFormValidation() {
    const form = document.getElementById('transactionForm');
    const inputs = form.querySelectorAll('input[required], select[required]');
    
    inputs.forEach(input => {
        input.addEventListener('blur', validateField);
        input.addEventListener('input', clearValidationState);
    });
}

function validateField() {
    const field = this;
    const value = field.value.trim();
    
    // Remove existing validation classes
    field.classList.remove('is-valid', 'is-invalid');
    
    // Remove existing feedback
    const existingFeedback = field.parentNode.querySelector('.invalid-feedback, .valid-feedback');
    if (existingFeedback) {
        existingFeedback.remove();
    }
    
    // Validate based on field type
    let isValid = true;
    let message = '';
    
    if (field.hasAttribute('required') && !value) {
        isValid = false;
        message = 'This field is required.';
    } else if (field.type === 'number' && value) {
        const num = parseFloat(value);
        if (isNaN(num) || num <= 0) {
            isValid = false;
            message = 'Please enter a valid positive number.';
        }
    } else if (field.type === 'date' && value) {
        const date = new Date(value);
        const today = new Date();
        today.setHours(23, 59, 59, 999); // End of today
        
        if (date > today) {
            isValid = false;
            message = 'Date cannot be in the future.';
        }
    }
    
    // Apply validation styling
    if (value) { // Only show validation if field has content
        field.classList.add(isValid ? 'is-valid' : 'is-invalid');
        
        // Add feedback message
        const feedback = document.createElement('div');
        feedback.className = isValid ? 'valid-feedback' : 'invalid-feedback';
        feedback.textContent = isValid ? 'Looks good!' : message;
        field.parentNode.appendChild(feedback);
    }
}

function clearValidationState() {
    this.classList.remove('is-valid', 'is-invalid');
    const feedback = this.parentNode.querySelector('.invalid-feedback, .valid-feedback');
    if (feedback) {
        feedback.remove();
    }
}

function handleFormSubmission(e) {
    const submitBtn = document.querySelector('button[type="submit"]');
    const form = e.target;
    
    // Validate all required fields
    const requiredFields = form.querySelectorAll('input[required], select[required]');
    let isFormValid = true;
    
    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            isFormValid = false;
            field.classList.add('is-invalid');
            
            // Add error message if not exists
            if (!field.parentNode.querySelector('.invalid-feedback')) {
                const feedback = document.createElement('div');
                feedback.className = 'invalid-feedback';
                feedback.textContent = 'This field is required.';
                field.parentNode.appendChild(feedback);
            }
        }
    });
    
    if (!isFormValid) {
        e.preventDefault();
        showNotification('Please fill in all required fields.', 'danger');
        return;
    }
    
    // Show loading state
    submitBtn.disabled = true;
    submitBtn.classList.add('btn-loading');
    
    // Show success message
    showNotification('Saving transaction...', 'info');
    
    // Re-enable after timeout (fallback)
    setTimeout(() => {
        submitBtn.disabled = false;
        submitBtn.classList.remove('btn-loading');
    }, 5000);
}

function resetForm() {
    const form = document.getElementById('transactionForm');
    const submitBtn = document.querySelector('button[type="submit"]');
    const card = document.querySelector('.transaction-card');
    
    // Reset form
    form.reset();
    
    // Reset date to today
    const dateInput = document.querySelector('input[name="date"]');
    if (dateInput) {
        dateInput.value = new Date().toISOString().split('T')[0];
    }
    
    // Reset validation states
    form.querySelectorAll('.is-valid, .is-invalid').forEach(field => {
        field.classList.remove('is-valid', 'is-invalid');
    });
    
    form.querySelectorAll('.invalid-feedback, .valid-feedback').forEach(feedback => {
        feedback.remove();
    });
    
    // Reset button styling
    submitBtn.className = 'btn btn-primary-transaction';
    submitBtn.innerHTML = '<i class="fas fa-save me-1"></i>Save Transaction';
    
    // Reset card styling
    card.classList.remove('transaction-type-income', 'transaction-type-expense', 'transaction-type-transfer');
    
    showNotification('Form reset successfully!', 'success');
}

function setupKeyboardShortcuts() {
    document.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + Enter to submit
        if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
            e.preventDefault();
            const form = document.getElementById('transactionForm');
            form.dispatchEvent(new Event('submit'));
        }
        
        // Ctrl/Cmd + R to reset
        if ((e.ctrlKey || e.metaKey) && e.key === 'r') {
            e.preventDefault();
            resetForm();
        }
        
        // Escape to cancel
        if (e.key === 'Escape') {
            e.preventDefault();
            const cancelBtn = document.querySelector('a[href*="dashboard"]');
            if (cancelBtn) {
                cancelBtn.click();
            }
        }
    });
}

function showNotification(message, type = 'info') {
    // Remove existing notifications
    document.querySelectorAll('.notification').forEach(n => n.remove());
    
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} notification`;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 9999;
        min-width: 300px;
        opacity: 0;
        transform: translateX(100%);
        transition: all 0.3s ease;
        border-radius: 12px;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    `;
    
    notification.innerHTML = `
        <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'danger' ? 'exclamation-triangle' : 'info-circle'} me-2"></i>
        ${message}
    `;
    
    document.body.appendChild(notification);
    
    // Animate in
    setTimeout(() => {
        notification.style.opacity = '1';
        notification.style.transform = 'translateX(0)';
    }, 100);
    
    // Auto remove
    setTimeout(() => {
        notification.style.opacity = '0';
        notification.style.transform = 'translateX(100%)';
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    }, 4000);
}

// Global functions for buttons
window.resetForm = resetForm;

console.log('💰 Transaction Form JavaScript Loaded');
console.log('Keyboard Shortcuts: Ctrl+Enter (Submit), Ctrl+R (Reset), Escape (Cancel)');