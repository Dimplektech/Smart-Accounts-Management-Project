// accounts/static/accounts/js/add_account.js

document.addEventListener('DOMContentLoaded', function() {
    // Form preview functionality
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('accountForm');
    const formSummary = document.getElementById('formSummary');
    const nameField = document.getElementById('{{ form.name.id_for_label }}');
    const typeField = document.getElementById('{{ form.account_type.id_for_label }}');
    const balanceField = document.getElementById('{{ form.initial_balance.id_for_label }}');
    const bankField = document.getElementById('{{ form.bank_name.id_for_label }}');

    function updatePreview() {
        document.getElementById('summaryName').textContent = nameField.value || '-';
        document.getElementById('summaryType').textContent = typeField.options[typeField.selectedIndex].text || '-';
        document.getElementById('summaryBalance').textContent = balanceField.value ? `£${parseFloat(balanceField.value).toFixed(2)}` : '£0.00';
        document.getElementById('summaryBank').textContent = bankField.value || '-';
        
        // Show summary if any field has value
        if (nameField.value || typeField.value || balanceField.value || bankField.value) {
            formSummary.style.display = 'block';
        } else {
            formSummary.style.display = 'none';
        }
    }

    // Add event listeners
    [nameField, typeField, balanceField, bankField].forEach(field => {
        if (field) {
            field.addEventListener('input', updatePreview);
            field.addEventListener('change', updatePreview);
        }
    });
});

// Reset form function
function resetAccountForm() {
    document.getElementById('accountForm').reset();
    document.getElementById('formSummary').style.display = 'none';
    
    // Clear any error messages
    document.querySelectorAll('.text-danger').forEach(el => el.style.display = 'none');
}

    console.log('🏦 Account Form Loading...');
    
    initializeAccountForm();
    setupAccountTypeHandler();
    setupFormValidation();
    setupPreviewUpdates();
    setupKeyboardShortcuts();
    
    console.log('✅ Account Form Ready!');
});

function initializeAccountForm() {
    // Add slide-in animation
    const card = document.querySelector('.account-card');
    if (card) {
        card.classList.add('slide-in');
    }
    
    // Initialize character counter
    setupCharacterCounter();
    
    // Set focus on first input
    const firstInput = document.querySelector('#id_name');
    if (firstInput) {
        setTimeout(() => firstInput.focus(), 500);
    }
}

function setupAccountTypeHandler() {
    const accountTypeSelect = document.querySelector('#id_account_type');
    const typeDescription = document.getElementById('typeDescription');
    
    if (accountTypeSelect && typeDescription) {
        accountTypeSelect.addEventListener('change', function() {
            const selectedOption = this.options[this.selectedIndex];
            const icon = selectedOption.getAttribute('data-icon') || '🏦';
            const description = selectedOption.getAttribute('data-description') || '';
            
            if (description) {
                typeDescription.innerHTML = `
                    <i class="fas fa-lightbulb me-1"></i>
                    <span>${icon} ${description}</span>
                `;
                typeDescription.style.opacity = '1';
            } else {
                typeDescription.innerHTML = `
                    <i class="fas fa-lightbulb me-1"></i>
                    <span>Select an account type to see description</span>
                `;
                typeDescription.style.opacity = '0.7';
            }
            
            updateAccountPreview();
        });
    }
}

function setupCharacterCounter() {
    const textarea = document.querySelector('#id_description');
    const charCount = document.getElementById('charCount');
    
    if (textarea && charCount) {
        textarea.addEventListener('input', function() {
            const currentLength = this.value.length;
            charCount.textContent = currentLength;
            
            // Color coding
            if (currentLength > 400) {
                charCount.style.color = '#ef4444';
            } else if (currentLength > 300) {
                charCount.style.color = '#f59e0b';
            } else {
                charCount.style.color = '#6b7280';
            }
        });
        
        // Initial count
        charCount.textContent = textarea.value.length;
    }
}

function setupFormValidation() {
    const form = document.getElementById('accountForm');
    const inputs = form.querySelectorAll('input[required], select[required]');
    
    inputs.forEach(input => {
        input.addEventListener('blur', validateField);
        input.addEventListener('input', clearValidationState);
    });
    
    // Balance input specific validation
    const balanceInput = document.querySelector('#id_balance');
    if (balanceInput) {
        balanceInput.addEventListener('input', updateBalanceIndicator);
        balanceInput.addEventListener('blur', formatBalanceInput);
    }
    
    // Form submission handler
    form.addEventListener('submit', handleFormSubmission);
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
    
    // Validate based on field
    let isValid = true;
    let message = '';
    
    if (field.hasAttribute('required') && !value) {
        isValid = false;
        message = 'This field is required.';
    } else if (field.type === 'number' && value) {
        const num = parseFloat(value);
        if (isNaN(num)) {
            isValid = false;
            message = 'Please enter a valid number.';
        }
    } else if (field.id === 'id_name' && value.length > 0 && value.length < 3) {
        isValid = false;
        message = 'Account name must be at least 3 characters.';
    }
    
    // Apply validation styling
    if (value) {
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
    
    updateAccountPreview();
}

function updateBalanceIndicator() {
    const balanceIndicator = document.getElementById('balanceIndicator');
    const balance = parseFloat(this.value);
    
    if (balanceIndicator) {
        if (isNaN(balance) || balance === 0) {
            balanceIndicator.innerHTML = '💵';
            balanceIndicator.style.color = '#6b7280';
        } else if (balance > 0) {
            balanceIndicator.innerHTML = '💰';
            balanceIndicator.style.color = '#10b981';
            balanceIndicator.style.transform = 'translateY(-50%) scale(1.1)';
        } else {
            balanceIndicator.innerHTML = '⚠️';
            balanceIndicator.style.color = '#ef4444';
            balanceIndicator.style.transform = 'translateY(-50%) scale(1.1)';
        }
        
        setTimeout(() => {
            balanceIndicator.style.transform = 'translateY(-50%) scale(1)';
        }, 200);
    }
}

function formatBalanceInput() {
    if (this.value && !isNaN(this.value)) {
        this.value = parseFloat(this.value).toFixed(2);
    }
    updateAccountPreview();
}

function setupPreviewUpdates() {
    const nameInput = document.querySelector('#id_name');
    const typeSelect = document.querySelector('#id_account_type');
    const balanceInput = document.querySelector('#id_balance');
    
    [nameInput, typeSelect, balanceInput].forEach(input => {
        if (input) {
            input.addEventListener('input', updateAccountPreview);
        }
    });
}

function updateAccountPreview() {
    const previewCard = document.getElementById('accountPreview');
    const nameInput = document.querySelector('#id_name');
    const typeSelect = document.querySelector('#id_account_type');
    const balanceInput = document.querySelector('#id_balance');
    
    const previewIcon = document.getElementById('previewIcon');
    const previewName = document.getElementById('previewName');
    const previewType = document.getElementById('previewType');
    const previewBalance = document.getElementById('previewBalance');
    
    if (!previewCard || !nameInput || !typeSelect || !balanceInput) return;
    
    const name = nameInput.value.trim();
    const type = typeSelect.value;
    const balance = parseFloat(balanceInput.value) || 0;
    
    if (name || type || balance > 0) {
        // Show preview card
        previewCard.style.display = 'block';
        
        // Update content
        if (previewName) previewName.textContent = name || 'Account Name';
        if (previewType) previewType.textContent = type ? getAccountTypeLabel(type) : 'Account Type';
        if (previewBalance) {
            previewBalance.textContent = `$${balance.toLocaleString('en-US', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
            })}`;
            previewBalance.style.color = balance >= 0 ? '#10b981' : '#ef4444';
        }
        
        // Update icon
        if (previewIcon) {
            const iconMap = {
                'checking': '🏦',
                'savings': '💰',
                'credit': '💳',
                'investment': '📈',
                'loan': '🏠'
            };
            previewIcon.textContent = iconMap[type] || '🏦';
        }
    } else {
        previewCard.style.display = 'none';
    }
}

function getAccountTypeLabel(type) {
    const labels = {
        'checking': 'Checking Account',
        'savings': 'Savings Account',
        'credit': 'Credit Card',
        'investment': 'Investment Account',
        'loan': 'Loan Account'
    };
    return labels[type] || 'Account';
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
    
    showNotification('Creating account...', 'info');
    
    // Re-enable after timeout (fallback)
    setTimeout(() => {
        submitBtn.disabled = false;
        submitBtn.classList.remove('btn-loading');
    }, 5000);
}

function resetAccountForm() {
    const form = document.getElementById('accountForm');
    const submitBtn = document.querySelector('button[type="submit"]');
    const previewCard = document.getElementById('accountPreview');
    
    // Reset form
    form.reset();
    
    // Reset validation states
    form.querySelectorAll('.is-valid, .is-invalid').forEach(field => {
        field.classList.remove('is-valid', 'is-invalid');
    });
    
    form.querySelectorAll('.invalid-feedback, .valid-feedback').forEach(feedback => {
        feedback.remove();
    });
    
    // Reset character counter
    const charCount = document.getElementById('charCount');
    if (charCount) {
        charCount.textContent = '0';
        charCount.style.color = '#6b7280';
    }
    
    // Reset type description
    const typeDescription = document.getElementById('typeDescription');
    if (typeDescription) {
        typeDescription.innerHTML = `
            <i class="fas fa-lightbulb me-1"></i>
            <span>Select an account type to see description</span>
        `;
        typeDescription.style.opacity = '0.7';
    }
    
    // Hide preview
    if (previewCard) {
        previewCard.style.display = 'none';
    }
    
    // Reset balance indicator
    const balanceIndicator = document.getElementById('balanceIndicator');
    if (balanceIndicator) {
        balanceIndicator.innerHTML = '💵';
        balanceIndicator.style.color = '#6b7280';
        balanceIndicator.style.transform = 'translateY(-50%) scale(1)';
    }
    
    showNotification('Form reset successfully!', 'success');
}

function setupKeyboardShortcuts() {
    document.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + Enter to submit
        if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
            e.preventDefault();
            const form = document.getElementById('accountForm');
            form.dispatchEvent(new Event('submit'));
        }
        
        // Ctrl/Cmd + R to reset
        if ((e.ctrlKey || e.metaKey) && e.key === 'r') {
            e.preventDefault();
            resetAccountForm();
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

// Global functions
window.resetAccountForm = resetAccountForm;

console.log('🏦 Account Form JavaScript Loaded');
console.log('Keyboard Shortcuts: Ctrl+Enter (Submit), Ctrl+R (Reset), Escape (Cancel)');