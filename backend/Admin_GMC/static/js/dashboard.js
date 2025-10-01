// Dashboard.js - Real-time dashboard functionality
document.addEventListener('DOMContentLoaded', function() {
    loadDashboardStats();
    loadRecentActivity();
    initializeCharts();
    
    // Refresh data every 30 seconds
    setInterval(loadDashboardStats, 30000);
});

async function loadDashboardStats() {
    try {
        const response = await fetch('/admin/api/dashboard/kpis');
        const data = await response.json();
        
        if (data.ok) {
            updateDashboardCards(data.kpis);
            updateSalesChart(data.recent_sales);
        } else {
            console.error('Failed to load dashboard stats:', data.error);
        }
    } catch (error) {
        console.error('Error loading dashboard stats:', error);
    }
}

function updateDashboardCards(stats) {
    // Update Today's Sales
    const todaySalesElement = document.querySelector('.dashboard-card:nth-child(1) .card-value');
    if (todaySalesElement) {
        todaySalesElement.textContent = `₱${(stats.today_sales || 0).toLocaleString()}`;
    }
    
    // Update This Month Sales
    const monthSalesElement = document.querySelector('.dashboard-card:nth-child(2) .card-value');
    if (monthSalesElement) {
        monthSalesElement.textContent = `₱${(stats.month_sales || 0).toLocaleString()}`;
    }
    
    // Update Low Stock Items
    const lowStockElement = document.querySelector('.dashboard-card:nth-child(3) .card-value');
    if (lowStockElement) {
        lowStockElement.textContent = stats.low_stock_count || 0;
    }
    
    // Update Forecast Accuracy
    const forecastAccuracyElement = document.querySelector('.dashboard-card:nth-child(4) .card-value');
    if (forecastAccuracyElement) {
        forecastAccuracyElement.textContent = `${(stats.forecast_accuracy || 0).toFixed(1)}%`;
    }
}

function updateSalesChart(salesData) {
    const ctx = document.getElementById('salesChart');
    if (!ctx) return;
    
    const labels = salesData.map(item => {
        const date = new Date(item.date);
        return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
    });
    
    const data = salesData.map(item => item.amount);
    
    if (window.salesChart) {
        window.salesChart.destroy();
    }
    
    window.salesChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Daily Sales (₱)',
                data: data,
                borderColor: '#2e7d32',
                backgroundColor: 'rgba(46, 125, 50, 0.1)',
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return '₱' + value.toLocaleString();
                        }
                    }
                }
            }
        }
    });
}

async function loadRecentActivity() {
    try {
        // Load recent sales
        const salesResponse = await fetch('/api/sales?page=1&page_size=5');
        const salesData = await salesResponse.json();
        
        if (salesResponse.ok) {
            updateRecentSales(salesData.data);
        }
        
        // Load recent notifications
        const notificationsResponse = await fetch('/api/notifications');
        const notificationsData = await notificationsResponse.json();
        
        if (notificationsResponse.ok) {
            updateRecentNotifications(notificationsData.data.slice(0, 3));
        }
    } catch (error) {
        console.error('Error loading recent activity:', error);
    }
}

function updateRecentSales(sales) {
    const salesContainer = document.querySelector('.recent-sales-list');
    if (!salesContainer) return;
    
    salesContainer.innerHTML = '';
    
    sales.forEach(sale => {
        const saleElement = document.createElement('div');
        saleElement.className = 'recent-sale-item';
        saleElement.innerHTML = `
            <div class="sale-info">
                <div class="sale-customer">${sale.customer_name || 'Walk-in Customer'}</div>
                <div class="sale-details">${sale.rice_variant} - ${sale.quantity_kg}kg</div>
            </div>
            <div class="sale-amount">₱${sale.total_amount.toLocaleString()}</div>
        `;
        salesContainer.appendChild(saleElement);
    });
}

function updateRecentNotifications(notifications) {
    const notificationsContainer = document.querySelector('.recent-notifications');
    if (!notificationsContainer) return;
    
    notificationsContainer.innerHTML = '';
    
    notifications.forEach(notification => {
        const notificationElement = document.createElement('div');
        notificationElement.className = `notification-item ${notification.type.toLowerCase()}`;
        notificationElement.innerHTML = `
            <div class="notification-icon">
                ${getNotificationIcon(notification.type)}
            </div>
            <div class="notification-content">
                <div class="notification-title">${notification.title}</div>
                <div class="notification-message">${notification.message}</div>
            </div>
        `;
        notificationsContainer.appendChild(notificationElement);
    });
}

function getNotificationIcon(type) {
    const icons = {
        'Info': '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 16v-4"/><path d="M12 8h.01"/></svg>',
        'Warning': '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>',
        'Error': '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>',
        'Success': '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22,4 12,14.01 9,11.01"/></svg>'
    };
    return icons[type] || icons['Info'];
}

function initializeCharts() {
    // Initialize any additional charts here
    console.log('Charts initialized');
}

// Search functionality
document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.querySelector('.dashboard-search input');
    const searchBtn = document.querySelector('.search-btn');
    
    if (searchInput && searchBtn) {
        searchBtn.addEventListener('click', performSearch);
        searchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                performSearch();
            }
        });
    }
});

function performSearch() {
    const searchInput = document.querySelector('.dashboard-search input');
    const query = searchInput.value.trim();
    
    if (query) {
        // For now, just show an alert. You can implement actual search later
        alert(`Searching for: ${query}`);
        // You can redirect to search results page or show results in a modal
    }
}
