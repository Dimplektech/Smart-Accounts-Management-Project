// accounts/static/accounts/js/dashboard.js

document.addEventListener('DOMContentLoaded', function() {
    console.log('📊 Dashboard Loading...');
    
    initializeDashboard();
    initializeCharts();
    setupDashboardInteractions();
    updateDateTime();
    
    // Update time every minute
    setInterval(updateDateTime, 60000);
    
    console.log('✅ Dashboard Ready!');
});

function initializeDashboard() {
    // Animate stat cards with staggered effect
    animateStatCards();
    
    // Initialize data refresh
    setupDataRefresh();
    
    // Setup search functionality
    initializeSearch();
    
    // Animate counters
    animateCounters();
}

function animateStatCards() {
    const statCards = document.querySelectorAll('.stat-card');
    
    statCards.forEach((card, index) => {
        // Set initial state
        card.style.opacity = '0';
        card.style.transform = 'translateY(30px)';
        
        // Animate in with delay
        setTimeout(() => {
            card.style.transition = 'all 0.6s cubic-bezier(0.4, 0, 0.2, 1)';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, index * 150);
    });
}

function animateCounters() {
    const counters = document.querySelectorAll('[data-animate]');
    
    counters.forEach(counter => {
        const target = parseFloat(counter.textContent.replace(/[^\d.-]/g, ''));
        const duration = 2000; // 2 seconds
        const start = performance.now();
        const isMonetary = counter.textContent.includes('$');
        
        function updateCounter(currentTime) {
            const elapsed = currentTime - start;
            const progress = Math.min(elapsed / duration, 1);
            
            // Easing function
            const easeOutQuart = 1 - Math.pow(1 - progress, 4);
            const current = target * easeOutQuart;
            
            if (isMonetary) {
                counter.textContent = `$${current.toLocaleString('en-US', {
                    minimumFractionDigits: 2,
                    maximumFractionDigits: 2
                })}`;
            } else {
                counter.textContent = Math.floor(current).toLocaleString();
            }
            
            if (progress < 1) {
                requestAnimationFrame(updateCounter);
            }
        }
        
        // Start animation after a delay
        setTimeout(() => {
            counter.textContent = isMonetary ? '$0.00' : '0';
            requestAnimationFrame(updateCounter);
        }, 500);
    });
}

function initializeCharts() {
    if (typeof Chart === 'undefined') {
        console.warn('Chart.js not loaded');
        return;
    }
    
    // Set default Chart.js configuration
    Chart.defaults.font.family = "'Inter', sans-serif";
    Chart.defaults.color = '#6b7280';
    Chart.defaults.plugins.legend.labels.usePointStyle = true;
    
    initializeMonthlyChart();
    initializeCategoryChart();
}

function initializeMonthlyChart() {
    const ctx = document.getElementById('monthlyChart');
    if (!ctx) return;
    
    // Use real data from Django backend or fallback to sample data
    let chartData;
    if (window.dashboardData && window.dashboardData.monthlyData && window.dashboardData.monthlyData.length > 0) {
        const realData = window.dashboardData.monthlyData;
        chartData = {
            labels: realData.map(item => item.month),
            datasets: [
                {
                    label: 'Income',
                    data: realData.map(item => item.income),
                    borderColor: '#10b981',
                    backgroundColor: 'rgba(16, 185, 129, 0.1)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4,
                    pointBackgroundColor: '#10b981',
                    pointBorderColor: '#ffffff',
                    pointBorderWidth: 2,
                    pointRadius: 6,
                    pointHoverRadius: 8
                },
                {
                    label: 'Expenses',
                    data: realData.map(item => item.expenses),
                    borderColor: '#ef4444',
                    backgroundColor: 'rgba(239, 68, 68, 0.1)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4,
                    pointBackgroundColor: '#ef4444',
                    pointBorderColor: '#ffffff',
                    pointBorderWidth: 2,
                    pointRadius: 6,
                    pointHoverRadius: 8
                }
            ]
        };
    } else {
        // Fallback to sample data if no real data available
        chartData = {
            labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
            datasets: [
                {
                    label: 'Income',
                    data: [0, 0, 0, 0, 0, 0],
                    borderColor: '#10b981',
                    backgroundColor: 'rgba(16, 185, 129, 0.1)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4,
                    pointBackgroundColor: '#10b981',
                    pointBorderColor: '#ffffff',
                    pointBorderWidth: 2,
                    pointRadius: 6,
                    pointHoverRadius: 8
                },
                {
                    label: 'Expenses',
                    data: [0, 0, 0, 0, 0, 0],
                    borderColor: '#ef4444',
                    backgroundColor: 'rgba(239, 68, 68, 0.1)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4,
                    pointBackgroundColor: '#ef4444',
                    pointBorderColor: '#ffffff',
                    pointBorderWidth: 2,
                    pointRadius: 6,
                    pointHoverRadius: 8
                }
            ]
        };
    }
    
    new Chart(ctx, {
        type: 'line',
        data: chartData,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                intersect: false,
                mode: 'index'
            },
            plugins: {
                legend: {
                    position: 'top',
                    align: 'end',
                    labels: {
                        padding: 20,
                        font: {
                            weight: '600'
                        }
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleColor: 'white',
                    bodyColor: 'white',
                    borderColor: 'rgba(255, 255, 255, 0.1)',
                    borderWidth: 1,
                    cornerRadius: 8,
                    displayColors: true,
                    callbacks: {
                        label: function(context) {
                            return `${context.dataset.label}: $${context.parsed.y.toLocaleString()}`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    grid: {
                        display: false
                    },
                    border: {
                        display: false
                    },
                    ticks: {
                        font: {
                            weight: '500'
                        }
                    }
                },
                y: {
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)',
                        drawBorder: false
                    },
                    border: {
                        display: false
                    },
                    ticks: {
                        callback: function(value) {
                            return '$' + value.toLocaleString();
                        },
                        font: {
                            weight: '500'
                        }
                    }
                }
            },
            elements: {
                point: {
                    hoverBorderWidth: 3
                }
            }
        }
    });
}

function initializeCategoryChart() {
    const ctx = document.getElementById('categoryChart');
    if (!ctx) return;
    
    // Use real data from Django backend or fallback to sample data
    let chartData;
    if (window.dashboardData && window.dashboardData.categorySpending && window.dashboardData.categorySpending.length > 0) {
        const realData = window.dashboardData.categorySpending;
        const colors = [
            '#ef4444', '#f59e0b', '#10b981', '#06b6d4', '#8b5cf6', '#ec4899', '#f97316', '#84cc16'
        ];
        
        chartData = {
            labels: realData.map(item => item.category__name),
            datasets: [{
                data: realData.map(item => item.total),
                backgroundColor: colors.slice(0, realData.length),
                borderWidth: 0,
                hoverBorderWidth: 3,
                hoverBorderColor: '#ffffff'
            }]
        };
    } else {
        // Fallback to sample data if no real data available
        chartData = {
            labels: ['No Expenses Yet'],
            datasets: [{
                data: [1],
                backgroundColor: ['#e5e7eb'],
                borderWidth: 0,
                hoverBorderWidth: 3,
                hoverBorderColor: '#ffffff'
            }]
        };
    }
    
    new Chart(ctx, {
        type: 'doughnut',
        data: chartData,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '60%',
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        padding: 20,
                        usePointStyle: true,
                        pointStyle: 'circle',
                        font: {
                            weight: '500'
                        }
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleColor: 'white',
                    bodyColor: 'white',
                    borderColor: 'rgba(255, 255, 255, 0.1)',
                    borderWidth: 1,
                    cornerRadius: 8,
                    callbacks: {
                        label: function(context) {
                            if (context.label === 'No Expenses Yet') {
                                return 'No expenses recorded yet';
                            }
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = ((context.parsed / total) * 100).toFixed(1);
                            return `${context.label}: $${context.parsed.toLocaleString()} (${percentage}%)`;
                        }
                    }
                }
            }
        }
    });
}

function setupDashboardInteractions() {
    // Chart period controls
    setupChartControls();
    
    // Category period selector
    setupCategoryPeriodSelector();
    
    // Quick action buttons
    setupQuickActions();
    
    // Auto-refresh data
    setupAutoRefresh();
}

function setupChartControls() {
    const chartControls = document.querySelectorAll('.chart-controls .btn');
    
    chartControls.forEach(btn => {
        btn.addEventListener('click', function() {
            // Remove active class from all buttons
            chartControls.forEach(b => b.classList.remove('active'));
            
            // Add active class to clicked button
            this.classList.add('active');
            
            // Update chart data based on period
            const period = this.getAttribute('data-period');
            updateChartData(period);
        });
    });
}

function setupCategoryPeriodSelector() {
    const periodSelector = document.getElementById('categoryPeriod');
    if (periodSelector) {
        periodSelector.addEventListener('change', function() {
            updateCategoryChart(this.value);
        });
    }
}

function setupQuickActions() {
    // Add hover effects and analytics tracking
    document.querySelectorAll('.quick-actions .btn').forEach(btn => {
        btn.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-2px)';
        });
        
        btn.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
        
        btn.addEventListener('click', function() {
            // Track quick action usage
            console.log(`Quick action clicked: ${this.textContent.trim()}`);
        });
    });
}

function setupDataRefresh() {
    // Setup periodic data refresh (every 5 minutes)
    setInterval(() => {
        if (document.visibilityState === 'visible') {
            refreshDashboardData();
        }
    }, 5 * 60 * 1000);
    
    // Refresh when page becomes visible
    document.addEventListener('visibilitychange', () => {
        if (document.visibilityState === 'visible') {
            refreshDashboardData();
        }
    });
}

function setupAutoRefresh() {
    // Add refresh button to dashboard
    const refreshBtn = document.createElement('button');
    refreshBtn.className = 'btn btn-sm btn-outline-primary position-fixed';
    refreshBtn.style.cssText = `
        bottom: 80px;
        right: 20px;
        z-index: 1000;
        border-radius: 50%;
        width: 45px;
        height: 45px;
        opacity: 0.7;
        transition: all 0.3s ease;
    `;
    refreshBtn.innerHTML = '<i class="fas fa-sync-alt"></i>';
    refreshBtn.setAttribute('title', 'Refresh Dashboard');
    
    refreshBtn.addEventListener('click', function() {
        this.classList.add('fa-spin');
        refreshDashboardData().finally(() => {
            this.classList.remove('fa-spin');
        });
    });
    
    document.body.appendChild(refreshBtn);
}

function initializeSearch() {
    // Add search functionality for transactions and accounts
    const searchInputs = document.querySelectorAll('[data-search]');
    
    searchInputs.forEach(input => {
        let searchTimeout;
        
        input.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                const query = this.value.toLowerCase();
                const target = this.getAttribute('data-search');
                filterContent(target, query);
            }, 300);
        });
    });
}

function filterContent(target, query) {
    const items = document.querySelectorAll(`[data-filterable="${target}"]`);
    
    items.forEach(item => {
        const text = item.textContent.toLowerCase();
        const matches = text.includes(query);
        
        item.style.display = matches ? '' : 'none';
        
        if (matches && query) {
            item.classList.add('highlight');
        } else {
            item.classList.remove('highlight');
        }
    });
}

function updateDateTime() {
    const dateTimeElement = document.getElementById('currentDateTime');
    if (dateTimeElement) {
        const now = new Date();
        const options = {
            weekday: 'long',
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        };
        
        dateTimeElement.textContent = now.toLocaleDateString('en-US', options);
    }
}

function updateChartData(period) {
    // This would typically fetch new data from your backend
    console.log(`Updating chart data for period: ${period}`);
    
    // Show loading indicator
    showGlobalNotification('Updating chart data...', 'info');
    
    // Simulate API call
    setTimeout(() => {
        showGlobalNotification('Chart data updated!', 'success');
    }, 1000);
}

function updateCategoryChart(period) {
    console.log(`Updating category chart for period: ${period}`);
    
    // This would typically fetch new data and update the chart
    showGlobalNotification('Category data updated!', 'success');
}

function refreshDashboardData() {
    return new Promise((resolve) => {
        console.log('Refreshing dashboard data...');
        
        // Simulate API call
        setTimeout(() => {
            // Update counters
            animateCounters();
            
            // Update charts
            updateChartData('current');
            updateCategoryChart('month');
            
            console.log('Dashboard data refreshed');
            resolve();
        }, 1000);
    });
}

// Keyboard shortcuts specific to dashboard
document.addEventListener('keydown', function(e) {
    // R for refresh
    if (e.key === 'r' && !e.ctrlKey && !e.metaKey && !e.altKey) {
        if (document.activeElement.tagName !== 'INPUT') {
            e.preventDefault();
            refreshDashboardData();
        }
    }
});

console.log('📊 Dashboard JavaScript Loaded');
console.log('Dashboard Shortcuts: R (Refresh)');