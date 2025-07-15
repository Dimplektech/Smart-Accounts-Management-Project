// accounts/static/accounts/js/base.js

document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Smart Account Management Base Loading...');
    
    initializeBaseComponents();
    setupGlobalEventListeners();
    setupAccessibility();
    fixDropdownIssues();
    console.log('✅ Base Components Ready!');

    // Show and manages messages if any
    var toastElList = [].slice.call(document.querySelectorAll('.toast'));
    toastElList.forEach(function (toastEl) {
      var toast = new bootstrap.Toast(toastEl);
      toast.show();
    });

    // Global utility functions
    window.showGlobalNotification = showGlobalNotification;
    window.showKeyboardShortcutsHelp = showKeyboardShortcutsHelp;

    console.log('🚀 Base JavaScript Loaded');
    console.log('Keyboard Shortcuts: Alt+D (Dashboard), Alt+T (Transaction), Alt+A (Account), Ctrl+/ (Help)');
});

function initializeBaseComponents() {
    // Auto-dismiss alerts after 5 seconds
    setupAutoAlerts();
    
    // Initialize tooltips
    initializeTooltips();
    
    // Setup smooth scrolling
    setupSmoothScrolling();
    
    // Add loading states to forms
    setupFormLoadingStates();
}

function setupAutoAlerts() {
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    
    alerts.forEach(alert => {
        // Add auto-dismiss timer
        setTimeout(() => {
            if (alert.parentNode) {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            }
        }, 5000);
        
        // Add slide-in animation
        alert.style.opacity = '0';
        alert.style.transform = 'translateY(-20px)';
        
        setTimeout(() => {
            alert.style.transition = 'all 0.4s ease';
            alert.style.opacity = '1';
            alert.style.transform = 'translateY(0)';
        }, 100);
    });
}

function initializeTooltips() {
    // Initialize Bootstrap tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

function setupSmoothScrolling() {
    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            const targetId = this.getAttribute('href');
            if (targetId === '#') return;
            
            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                e.preventDefault();
                targetElement.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

function setupFormLoadingStates() {
    // Add loading states to all forms
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', function() {
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn && !submitBtn.disabled) {
                const originalText = submitBtn.innerHTML;
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Processing...';
                
                // Re-enable after 10 seconds (fallback)
                setTimeout(() => {
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = originalText;
                }, 10000);
            }
        });
    });
}

function setupGlobalEventListeners() {
    // Global keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + / for help (can be implemented later)
        if ((e.ctrlKey || e.metaKey) && e.key === '/') {
            e.preventDefault();
            showKeyboardShortcutsHelp();
        }
        
        // Alt + D for Dashboard
        if (e.altKey && e.key === 'd') {
            e.preventDefault();
            const dashboardLink = document.querySelector('a[href*="dashboard"]');
            if (dashboardLink) dashboardLink.click();
        }
        
        // Alt + T for Add Transaction
        if (e.altKey && e.key === 't') {
            e.preventDefault();
            const transactionLink = document.querySelector('a[href*="add_transaction"]');
            if (transactionLink) transactionLink.click();
        }
        
        // Alt + A for Add Account
        if (e.altKey && e.key === 'a') {
            e.preventDefault();
            const accountLink = document.querySelector('a[href*="add_account"]');
            if (accountLink) accountLink.click();
        }
    });
    
    // Back to top functionality
    setupBackToTop();
    
    // Network status monitoring
    setupNetworkMonitoring();
}

function setupBackToTop() {
    // Create back to top button
    const backToTopBtn = document.createElement('button');
    backToTopBtn.innerHTML = '<i class="fas fa-arrow-up"></i>';
    backToTopBtn.className = 'btn btn-primary position-fixed';
    backToTopBtn.style.cssText = `
        bottom: 20px;
        right: 20px;
        z-index: 1000;
        border-radius: 50%;
        width: 50px;
        height: 50px;
        opacity: 0;
        visibility: hidden;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
    `;
    backToTopBtn.setAttribute('aria-label', 'Back to top');
    
    document.body.appendChild(backToTopBtn);
    
    // Show/hide based on scroll position
    window.addEventListener('scroll', function() {
        if (window.pageYOffset > 300) {
            backToTopBtn.style.opacity = '1';
            backToTopBtn.style.visibility = 'visible';
        } else {
            backToTopBtn.style.opacity = '0';
            backToTopBtn.style.visibility = 'hidden';
        }
    });
    
    // Scroll to top on click
    backToTopBtn.addEventListener('click', function() {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });
}

function setupNetworkMonitoring() {
    // Monitor network status
    function updateNetworkStatus() {
        if (!navigator.onLine) {
            showGlobalNotification('You are currently offline. Some features may not work.', 'warning', true);
        }
    }
    
    window.addEventListener('online', () => {
        showGlobalNotification('Connection restored!', 'success');
    });
    
    window.addEventListener('offline', updateNetworkStatus);
    
    // Initial check
    updateNetworkStatus();
}

function setupAccessibility() {
    // Skip to main content link
    const skipLink = document.createElement('a');
    skipLink.href = '#main-content';
    skipLink.textContent = 'Skip to main content';
    skipLink.className = 'visually-hidden-focusable btn btn-primary position-absolute';
    skipLink.style.cssText = 'top: 10px; left: 10px; z-index: 9999;';
    
    document.body.insertBefore(skipLink, document.body.firstChild);
    
    // Add main content ID if not exists
    const main = document.querySelector('main');
    if (main && !main.id) {
        main.id = 'main-content';
    }
    
    // Focus management for modals
    document.addEventListener('shown.bs.modal', function(e) {
        const modal = e.target;
        const focusableElements = modal.querySelectorAll('button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])');
        if (focusableElements.length > 0) {
            focusableElements[0].focus();
        }
    });
}

// Utility Functions
function showGlobalNotification(message, type = 'info', persistent = false) {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} ${persistent ? 'alert-permanent' : ''} position-fixed`;
    notification.style.cssText = `
        top: 20px;
        right: 20px;
        z-index: 9999;
        min-width: 300px;
        opacity: 0;
        transform: translateX(100%);
        transition: all 0.3s ease;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    `;
    
    notification.innerHTML = `
        <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'danger' ? 'exclamation-triangle' : type === 'warning' ? 'exclamation-circle' : 'info-circle'} me-2"></i>
        ${message}
        ${!persistent ? '<button type="button" class="btn-close" aria-label="Close"></button>' : ''}
    `;
    
    document.body.appendChild(notification);
    
    // Animate in
    setTimeout(() => {
        notification.style.opacity = '1';
        notification.style.transform = 'translateX(0)';
    }, 100);
    
    // Add close functionality
    const closeBtn = notification.querySelector('.btn-close');
    if (closeBtn) {
        closeBtn.addEventListener('click', () => {
            notification.style.opacity = '0';
            notification.style.transform = 'translateX(100%)';
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        });
    }
    
    // Auto remove if not persistent
    if (!persistent) {
        setTimeout(() => {
            if (notification.parentNode) {
                notification.style.opacity = '0';
                notification.style.transform = 'translateX(100%)';
                setTimeout(() => {
                    if (notification.parentNode) {
                        notification.parentNode.removeChild(notification);
                    }
                }, 300);
            }
        }, 5000);
    }
}

function showKeyboardShortcutsHelp() {
    const shortcuts = [
        { keys: 'Alt + D', description: 'Go to Dashboard' },
        { keys: 'Alt + T', description: 'Add Transaction' },
        { keys: 'Alt + A', description: 'Add Account' },
        { keys: 'Ctrl + /', description: 'Show this help' },
        { keys: 'Escape', description: 'Close modals/forms' }
    ];
    
    let helpText = '<h6><i class="fas fa-keyboard me-2"></i>Keyboard Shortcuts</h6><ul class="list-unstyled mb-0">';
    shortcuts.forEach(shortcut => {
        helpText += `<li class="mb-1"><kbd>${shortcut.keys}</kbd> - ${shortcut.description}</li>`;
    });
    helpText += '</ul>';
    
    showGlobalNotification(helpText, 'info', false);
}

// Fix dropdown issues in Bootstrap 5
function fixDropdownIssues() {
    // Fix Bootstrap dropdown toggle issues
    const dropdownToggles = document.querySelectorAll('.dropdown-toggle');
    
    dropdownToggles.forEach(toggle => {
        // Prevent default click behavior that might interfere
        toggle.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            const dropdown = bootstrap.Dropdown.getOrCreateInstance(this);
            const isShown = this.getAttribute('aria-expanded') === 'true';
            
            // Close all other dropdowns first
            closeAllDropdowns(this);
            
            // Toggle current dropdown
            if (isShown) {
                dropdown.hide();
            } else {
                dropdown.show();
            }
        });
        
        // Handle keyboard navigation
        toggle.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                this.click();
            }
        });
    });
    
    // Handle dropdown item clicks
    const dropdownItems = document.querySelectorAll('.dropdown-item');
    dropdownItems.forEach(item => {
        item.addEventListener('click', function(e) {
            // Only prevent default if it's a placeholder link
            if (this.getAttribute('href') === '#') {
                e.preventDefault();
            }
            
            // Close the dropdown after selection
            const dropdown = this.closest('.dropdown');
            if (dropdown) {
                const toggle = dropdown.querySelector('.dropdown-toggle');
                if (toggle) {
                    const bsDropdown = bootstrap.Dropdown.getInstance(toggle);
                    if (bsDropdown) {
                        bsDropdown.hide();
                    }
                }
            }
        });
    });
    
    // Handle outside clicks
    document.addEventListener('click', function(e) {
        if (!e.target.closest('.dropdown')) {
            closeAllDropdowns();
        }
    });
    
    // Handle escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            closeAllDropdowns();
        }
    });
}

function closeAllDropdowns(except = null) {
    const dropdowns = document.querySelectorAll('.dropdown-toggle');
    dropdowns.forEach(dropdown => {
        if (dropdown !== except) {
            const bsDropdown = bootstrap.Dropdown.getInstance(dropdown);
            if (bsDropdown) {
                bsDropdown.hide();
            }
        }
    });
}
