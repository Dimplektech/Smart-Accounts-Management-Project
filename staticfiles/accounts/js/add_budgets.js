// accounts/static/accounts/js/add_budget.js

document.addEventListener('DOMContentLoaded', function() {
    console.log('🎯 Budget Form Loading...');
    
    initializeBudgetForm();
    setupBudgetPreview();
    setupDateValidation();
    setupBudgetTips();
    
    console.log('✅ Budget Form Ready!');
});

function initializeBudgetForm() {
    const form = document.getElementById('budgetForm');
    const amountInput = document.querySelector('input[name="amount"]');
    const categorySelect = document.querySelector('select[name="category"]');
    const startDateInput = document.querySelector('input[name="start_date"]');
    const endDateInput = document.querySelector('input[name="end_date"]');
    
    // Add slide-in animation
    const card = document.querySelector('.budget-card');
    if (card) {
        card.classList.add('slide-in');
    }
    
    // Set default dates
    if (startDateInput && !startDateInput.value) {
        startDateInput.value = new Date().toISOString().split('T')[0];
    }
    
    if (endDateInput && !endDateInput.value) {
        const nextMonth = new Date();
        nextMonth.setMonth(nextMonth.getMonth() + 1);
        endDateInput.value = nextMonth.toISOString().split('T')[0];
    }
    
    // Event listeners
    if (amountInput) {
        amountInput.addEventListener('input', updateBudgetPreview);
        amountInput.addEventListener('blur', formatAmountInput);
    }
    
    if (categorySelect) {
        categorySelect.addEventListener('change', updateBudgetPreview);
    }
    
    if (startDateInput) {
        startDateInput.addEventListener('change', updateBudgetTimeline);
    }
    
    if (endDateInput) {
        endDateInput.addEventListener('change', updateBudgetTimeline);
    }
    
    // Initial preview update
    updateBudgetPreview();
    updateBudgetTimeline();
}

function setupBudgetPreview() {
    const previewContainer = document.createElement('div');
    previewContainer.className = 'budget-progress-preview';
    previewContainer.innerHTML = `
        <h6><i class="fas fa-target me-2"></i>Budget Preview</h6>
        <div class="d-flex justify-content-between mb-2">
            <span class="fw-bold" id="previewBudgetName">Budget Name</span>
            <span class="fw-bold text-warning" id="previewBudgetAmount">$0.00</span>
        </div>
        <div class="progress-preview-bar">
            <div class="progress-preview-fill" id="previewProgressFill" style="width: 0%"></div>
        </div>
        <div class="d-flex justify-content-between mt-2">
            <small class="text-muted">Spent: $0.00</small>
            <small class="text-muted" id="previewPercentage">0%</small>
        </div>
        <div class="budget-timeline">
            <div class="timeline-point"></div>
            <div class="timeline-line" id="timelineLine"></div>
            <div class="timeline-point"></div>
        </div>
        <div class="d-flex justify-content-between mt-2">
            <small id="previewStartDate">Start Date</small>
            <small id="previewEndDate">End Date</small>
        </div>
    `;
    
    const formBody = document.querySelector('.budget-body');
    if (formBody) {
        formBody.appendChild(previewContainer);
    }
}

function updateBudgetPreview() {
    const nameInput = document.querySelector('input[name="name"]');
    const amountInput = document.querySelector('input[name="amount"]');
    const categorySelect = document.querySelector('select[name="category"]');
    const preview = document.querySelector('.budget-progress-preview');
    
    if (!preview) return;
    
    const previewName = document.getElementById('previewBudgetName');
    const previewAmount = document.getElementById('previewBudgetAmount');
    
    // Update preview content
    if (previewName && nameInput) {
        previewName.textContent = nameInput.value || 'Budget Name';
    }
    
    if (previewAmount && amountInput) {
        const amount = parseFloat(amountInput.value) || 0;
        previewAmount.textContent = `$${amount.toLocaleString('en-US', {minimumFractionDigits: 2})}`;
    }
    
    // Show/hide preview
    if (nameInput && nameInput.value.trim() && amountInput && amountInput.value) {
        preview.classList.add('active');
    } else {
        preview.classList.remove('active');
    }
    
    // Simulate progress (for demo)
    const progressFill = document.getElementById('previewProgressFill');
    const percentage = document.getElementById('previewPercentage');
    if (progressFill && percentage) {
        const randomProgress = Math.floor(Math.random() * 60); // 0-60% for demo
        progressFill.style.width = `${randomProgress}%`;
        percentage.textContent = `${randomProgress}%`;
    }
}


function updateBudgetTimeline() {
    const startDateInput = document.querySelector('input[name="start_date"]');
    const endDateInput = document.querySelector('input[name="end_date"]');
    const previewStartDate = document.getElementById('previewStartDate');
    const previewEndDate = document.getElementById('previewEndDate');
    const timelineLine = document.getElementById('timelineLine');
    
    if (previewStartDate && startDateInput && startDateInput.value) {
        const startDate = new Date(startDateInput.value);
        previewStartDate.textContent = startDate.toLocaleDateString('en-US', {month: 'short', day: 'numeric'});
    }
    
    if (previewEndDate && endDateInput && endDateInput.value) {
        const endDate = new Date(endDateInput.value);
        previewEndDate.textContent = endDate.toLocaleDateString('en-US', {month: 'short', day: 'numeric'});
    }
    
    // Animate timeline
    if (timelineLine && startDateInput && endDateInput && startDateInput.value && endDateInput.value) {
        const now = new Date();
        const start = new Date(startDateInput.value);
        const end = new Date(endDateInput.value);
        
        if (now >= start && now <= end) {
            const progress = ((now - start) / (end - start)) * 100;
            timelineLine.style.background = `linear-gradient(90deg, #f59e0b 0%, #f59e0b ${progress}%, #e2e8f0 ${progress}%, #e2e8f0 100%)`;
            timelineLine.classList.add('active');
        } else {
            timelineLine.classList.remove('active');
        }
    }
}

function setupDateValidation() {
    const startDateInput = document.querySelector('input[name="start_date"]');
    const endDateInput = document.querySelector('input[name="end_date"]');
    
    if (startDateInput) {
        startDateInput.addEventListener('change', function() {
            if (endDateInput && this.value) {
                endDateInput.min = this.value;
                if (endDateInput.value && endDateInput.value < this.value) {
                    endDateInput.value = this.value;
                }
            }
            updateBudgetTimeline();
        });
    }
    
    if (endDateInput) {
        endDateInput.addEventListener('change', function() {
            if (startDateInput && this.value) {
                startDateInput.// accounts/static/accounts/js/add_budget.js

document.addEventListener('DOMContentLoaded', function() {
    console.log('🎯 Budget Form Loading...');
    
    initializeBudgetForm();
    setupBudgetPreview();
    setupDateValidation();
    setupBudgetTips();
    
    console.log('✅ Budget Form Ready!');
});

function initializeBudgetForm() {
    const form = document.getElementById('budgetForm');
    const amountInput = document.querySelector('input[name="amount"]');
    const categorySelect = document.querySelector('select[name="category"]');
    const startDateInput = document.querySelector('input[name="start_date"]');
    const endDateInput = document.querySelector('input[name="end_date"]');
    
    // Add slide-in animation
    const card = document.querySelector('.budget-card');
    if (card) {
        card.classList.add('slide-in');
    }
    
    // Set default dates
    if (startDateInput && !startDateInput.value) {
        startDateInput.value = new Date().toISOString().split('T')[0];
    }
    
    if (endDateInput && !endDateInput.value) {
        const nextMonth = new Date();
        nextMonth.setMonth(nextMonth.getMonth() + 1);
        endDateInput.value = nextMonth.toISOString().split('T')[0];
    }
    
    // Event listeners
    if (amountInput) {
        amountInput.addEventListener('input', updateBudgetPreview);
        amountInput.addEventListener('blur', formatAmountInput);
    }
    
    if (categorySelect) {
        categorySelect.addEventListener('change', updateBudgetPreview);
    }
    
    if (startDateInput) {
        startDateInput.addEventListener('change', updateBudgetTimeline);
    }
    
    if (endDateInput) {
        endDateInput.addEventListener('change', updateBudgetTimeline);
    }
    
    // Initial preview update
    updateBudgetPreview();
    updateBudgetTimeline();
}

function setupBudgetPreview() {
    const previewContainer = document.createElement('div');
    previewContainer.className = 'budget-progress-preview';
    previewContainer.innerHTML = `
        <h6><i class="fas fa-target me-2"></i>Budget Preview</h6>
        <div class="d-flex justify-content-between mb-2">
            <span class="fw-bold" id="previewBudgetName">Budget Name</span>
            <span class="fw-bold text-warning" id="previewBudgetAmount">$0.00</span>
        </div>
        <div class="progress-preview-bar">
            <div class="progress-preview-fill" id="previewProgressFill" style="width: 0%"></div>
        </div>
        <div class="d-flex justify-content-between mt-2">
            <small class="text-muted">Spent: $0.00</small>
            <small class="text-muted" id="previewPercentage">0%</small>
        </div>
        <div class="budget-timeline">
            <div class="timeline-point"></div>
            <div class="timeline-line" id="timelineLine"></div>
            <div class="timeline-point"></div>
        </div>
        <div class="d-flex justify-content-between mt-2">
            <small id="previewStartDate">Start Date</small>
            <small id="previewEndDate">End Date</small>
        </div>
    `;
    
    const formBody = document.querySelector('.budget-body');
    if (formBody) {
        formBody.appendChild(previewContainer);
    }
}

function updateBudgetPreview() {
    const nameInput = document.querySelector('input[name="name"]');
    const amountInput = document.querySelector('input[name="amount"]');
    const categorySelect = document.querySelector('select[name="category"]');
    const preview = document.querySelector('.budget-progress-preview');
    
    if (!preview) return;
    
    const previewName = document.getElementById('previewBudgetName');
    const previewAmount = document.getElementById('previewBudgetAmount');
    
    // Update preview content
    if (previewName && nameInput) {
        previewName.textContent = nameInput.value || 'Budget Name';
    }
    
    if (previewAmount && amountInput) {
        const amount = parseFloat(amountInput.value) || 0;
        previewAmount.textContent = `$${amount.toLocaleString('en-US', {minimumFractionDigits: 2})}`;
    }
    
    // Show/hide preview
    if (nameInput && nameInput.value.trim() && amountInput && amountInput.value) {
        preview.classList.add('active');
    } else {
        preview.classList.remove('active');
    }
    
    // Simulate progress (for demo)
    const progressFill = document.getElementById('previewProgressFill');
    const percentage = document.getElementById('previewPercentage');
    if (progressFill && percentage) {
        const randomProgress = Math.floor(Math.random() * 60); // 0-60% for demo
        progressFill.style.width = `${randomProgress}%`;
        percentage.textContent = `${randomProgress}%`;
    }
}

function updateBudgetTimeline() {
    const startDateInput = document.querySelector('input[name="start_date"]');
    const endDateInput = document.querySelector('input[name="end_date"]');
    const previewStartDate = document.getElementById('previewStartDate');
    const previewEndDate = document.getElementById('previewEndDate');
    const timelineLine = document.getElementById('timelineLine');
    
    if (previewStartDate && startDateInput && startDateInput.value) {
        const startDate = new Date(startDateInput.value);
        previewStartDate.textContent = startDate.toLocaleDateString('en-US', {month: 'short', day: 'numeric'});
    }
    
    if (previewEndDate && endDateInput && endDateInput.value) {
        const endDate = new Date(endDateInput.value);
        previewEndDate.textContent = endDate.toLocaleDateString('en-US', {month: 'short', day: 'numeric'});
    }
    
    // Animate timeline
    if (timelineLine && startDateInput && endDateInput && startDateInput.value && endDateInput.value) {
        const now = new Date();
        const start = new Date(startDateInput.value);
        const end = new Date(endDateInput.value);
        
        if (now >= start && now <= end) {
            const progress = ((now - start) / (end - start)) * 100;
            timelineLine.style.background = `linear-gradient(90deg, #f59e0b 0%, #f59e0b ${progress}%, #e2e8f0 ${progress}%, #e2e8f0 100%)`;
            timelineLine.classList.add('active');
        } else {
            timelineLine.classList.remove('active');
        }
    }
}

function setupDateValidation() {
    const startDateInput = document.querySelector('input[name="start_date"]');
    const endDateInput = document.querySelector('input[name="end_date"]');
    
    if (startDateInput) {
        startDateInput.addEventListener('change', function() {
            if (endDateInput && this.value) {
                endDateInput.min = this.value;
                if (endDateInput.value && endDateInput.value < this.value) {
                    endDateInput.value = this.value;
                }
            }
            updateBudgetTimeline();
});