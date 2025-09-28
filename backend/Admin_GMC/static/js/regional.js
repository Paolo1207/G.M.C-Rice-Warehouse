/**
 * Regional Insights - Live Data Integration
 * Handles Chart.js rendering, debounced filters, and real-time data updates
 */

class RegionalInsights {
    constructor() {
        this.charts = {};
        this.filters = {
            product: 'all',
            category: 'all',
            branch: 'all'
        };
        this.debounceTimer = null;
        this.isLoading = false;
        
        this.init();
    }
    
    /**
     * Initialize the regional insights dashboard
     */
    async init() {
        try {
            // Load catalog data for filter options
            await this.loadCatalog();
            
            // Setup filter event listeners with debouncing
            this.setupFilters();
            
            // Load initial data
            await this.loadAllData();
            
            console.log('Regional Insights initialized successfully');
        } catch (error) {
            console.error('Failed to initialize Regional Insights:', error);
            this.showToast('Failed to initialize dashboard', 'error');
        }
    }
    
    /**
     * Load catalog data for filter dropdowns
     */
    async loadCatalog() {
        try {
            const response = await fetch('/admin/api/catalog');
            const data = await response.json();
            
            if (data.ok) {
                this.populateFilterOptions(data);
            } else {
                throw new Error(data.error || 'Failed to load catalog');
            }
        } catch (error) {
            console.error('Error loading catalog:', error);
            this.showToast('Failed to load filter options', 'error');
        }
    }
    
    /**
     * Populate filter dropdown options from catalog data
     */
    populateFilterOptions(catalog) {
        // Populate product filter
        const productSelect = document.getElementById('product-select');
        if (productSelect && catalog.products) {
            productSelect.innerHTML = '<option value="all">All Products</option>';
            catalog.products.forEach(product => {
                const option = document.createElement('option');
                option.value = product;
                option.textContent = product;
                productSelect.appendChild(option);
            });
        }
        
        // Populate category filter
        const categorySelect = document.getElementById('category-select');
        if (categorySelect && catalog.categories) {
            categorySelect.innerHTML = '<option value="all">All Categories</option>';
            catalog.categories.forEach(category => {
                const option = document.createElement('option');
                option.value = category;
                option.textContent = category;
                categorySelect.appendChild(option);
            });
        }
        
        // Populate branch filter
        const branchSelect = document.getElementById('region-select');
        if (branchSelect && catalog.branches) {
            branchSelect.innerHTML = '<option value="all">All Branches</option>';
            catalog.branches.forEach(branch => {
                const option = document.createElement('option');
                option.value = branch;
                option.textContent = branch;
                branchSelect.appendChild(option);
            });
        }
    }
    
    /**
     * Setup filter event listeners with debouncing
     */
    setupFilters() {
        const filterSelects = ['product-select', 'category-select', 'region-select'];
        
        filterSelects.forEach(selectId => {
            const select = document.getElementById(selectId);
            if (select) {
                select.addEventListener('change', (e) => {
                    this.handleFilterChange(selectId, e.target.value);
                });
            }
        });
    }
    
    /**
     * Handle filter changes with debouncing
     */
    handleFilterChange(selectId, value) {
        // Clear existing timer
        if (this.debounceTimer) {
            clearTimeout(this.debounceTimer);
        }
        
        // Update filter value
        const filterKey = selectId.replace('-select', '');
        if (filterKey === 'region') {
            this.filters.branch = value;
        } else {
            this.filters[filterKey] = value;
        }
        
        // Show loading state
        this.showLoadingState();
        
        // Debounce the API call
        this.debounceTimer = setTimeout(() => {
            this.loadAllData();
        }, 300);
    }
    
    /**
     * Load all regional data
     */
    async loadAllData() {
        if (this.isLoading) return;
        
        this.isLoading = true;
        
        try {
            // Load data in parallel
            const [stockData, salesData, forecastData, gapsData] = await Promise.all([
                this.loadStockData(),
                this.loadSalesData(),
                this.loadForecastData(),
                this.loadGapsData()
            ]);
            
            // Update charts and UI
            this.updateStockChart(stockData);
            this.updateSalesChart(salesData);
            this.updateForecastChart(forecastData);
            this.updateGapsList(gapsData);
            
            this.hideLoadingState();
            
        } catch (error) {
            console.error('Error loading regional data:', error);
            this.showToast('Failed to load regional data', 'error');
            this.hideLoadingState();
        } finally {
            this.isLoading = false;
        }
    }
    
    /**
     * Load stock data from API
     */
    async loadStockData() {
        const params = new URLSearchParams(this.filters);
        const response = await fetch(`/admin/api/regional/stock?${params}`);
        const data = await response.json();
        
        if (!data.ok) {
            throw new Error(data.error || 'Failed to load stock data');
        }
        
        return data;
    }
    
    /**
     * Load sales data from API
     */
    async loadSalesData() {
        const params = new URLSearchParams(this.filters);
        const response = await fetch(`/admin/api/regional/sales?${params}`);
        const data = await response.json();
        
        if (!data.ok) {
            throw new Error(data.error || 'Failed to load sales data');
        }
        
        return data;
    }
    
    /**
     * Load forecast data from API
     */
    async loadForecastData() {
        const params = new URLSearchParams(this.filters);
        const response = await fetch(`/admin/api/regional/forecast?${params}`);
        const data = await response.json();
        
        if (!data.ok) {
            throw new Error(data.error || 'Failed to load forecast data');
        }
        
        return data;
    }
    
    /**
     * Load gaps data from API
     */
    async loadGapsData() {
        const params = new URLSearchParams(this.filters);
        const response = await fetch(`/admin/api/regional/gaps?${params}`);
        const data = await response.json();
        
        if (!data.ok) {
            throw new Error(data.error || 'Failed to load gaps data');
        }
        
        return data;
    }
    
    /**
     * Update stock chart with new data
     */
    updateStockChart(data) {
        const ctx = document.getElementById('branchStockChart');
        if (!ctx) return;
        
        // Destroy existing chart
        if (this.charts.stock) {
            this.charts.stock.destroy();
        }
        
        // Clear any loading state
        const container = ctx.parentElement;
        if (container) {
            container.classList.remove('loading');
        }
        
        // Prepare chart data
        const labels = data.branches.map(b => b.branch_name);
        const stockData = data.branches.map(b => b.stock_kg);
        
        // Color palette for branches
        const colors = [
            '#2e7d32', '#3b82f6', '#f59e0b', '#8b5cf6', '#059669', '#dc2626',
            '#ef4444', '#f97316', '#eab308', '#22c55e', '#06b6d4', '#8b5cf6'
        ];
        
        this.charts.stock = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Stock (kg)',
                    data: stockData,
                    backgroundColor: colors.slice(0, labels.length),
                    borderWidth: 2,
                    borderRadius: 8,
                    borderSkipped: false
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                aspectRatio: 2,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        callbacks: {
                            afterLabel: (context) => {
                                const branch = data.branches[context.dataIndex];
                                return `Products: ${branch.product_count}`;
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Stock (kg)'
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Branch'
                        }
                    }
                }
            }
        });
    }
    
    /**
     * Update sales chart with new data
     */
    updateSalesChart(data) {
        const ctx = document.getElementById('salesPerformanceChart');
        if (!ctx) return;
        
        // Destroy existing chart
        if (this.charts.sales) {
            this.charts.sales.destroy();
        }
        
        // Clear any loading state
        const container = ctx.parentElement;
        if (container) {
            container.classList.remove('loading');
        }
        
        // Prepare chart data
        const months = data.months;
        const branchData = data.branch_data;
        
        // Color palette for branches
        const colors = [
            '#2e7d32', '#3b82f6', '#f59e0b', '#8b5cf6', '#059669', '#dc2626',
            '#ef4444', '#f97316', '#eab308', '#22c55e', '#06b6d4', '#8b5cf6'
        ];
        
        const datasets = Object.keys(branchData).map((branchName, index) => {
            const branchMonths = branchData[branchName];
            const salesData = months.map(month => {
                const monthData = branchMonths.find(m => m.month === month);
                return monthData ? monthData.sales_amount : 0;
            });
            
            return {
                label: branchName,
                data: salesData,
                borderColor: colors[index % colors.length],
                backgroundColor: colors[index % colors.length] + '20',
                borderWidth: 3,
                fill: true,
                tension: 0.4
            };
        });
        
        this.charts.sales = new Chart(ctx, {
            type: 'line',
            data: {
                labels: months,
                datasets: datasets
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                aspectRatio: 2,
                plugins: {
                    legend: {
                        position: 'top',
                        onClick: (e, legendItem, legend) => {
                            // Toggle dataset visibility
                            const index = legendItem.datasetIndex;
                            const chart = legend.chart;
                            const meta = chart.getDatasetMeta(index);
                            meta.hidden = meta.hidden === null ? !chart.data.datasets[index].hidden : null;
                            chart.update();
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Sales Amount (₱)'
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Month'
                        }
                    }
                }
            }
        });
    }
    
    /**
     * Update forecast chart with new data
     */
    updateForecastChart(data) {
        const ctx = document.getElementById('regionalForecastChart');
        if (!ctx) return;
        
        // Destroy existing chart
        if (this.charts.forecast) {
            this.charts.forecast.destroy();
        }
        
        // Clear any loading state
        const container = ctx.parentElement;
        if (container) {
            container.classList.remove('loading');
        }
        
        // Prepare chart data
        const months = data.months;
        const branchForecasts = data.branch_forecasts;
        
        // Color palette for branches
        const colors = [
            '#2e7d32', '#3b82f6', '#f59e0b', '#8b5cf6', '#059669', '#dc2626',
            '#ef4444', '#f97316', '#eab308', '#22c55e', '#06b6d4', '#8b5cf6'
        ];
        
        const datasets = Object.keys(branchForecasts).map((branchName, index) => {
            const branchMonths = branchForecasts[branchName];
            const demandData = months.map(month => {
                const monthData = branchMonths.find(m => m.month === month);
                return monthData ? monthData.avg_demand : 0;
            });
            
            return {
                label: branchName,
                data: demandData,
                borderColor: colors[index % colors.length],
                backgroundColor: colors[index % colors.length] + '20',
                borderWidth: 3,
                fill: true,
                tension: 0.4
            };
        });
        
        this.charts.forecast = new Chart(ctx, {
            type: 'line',
            data: {
                labels: months,
                datasets: datasets
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                aspectRatio: 2,
                plugins: {
                    legend: {
                        position: 'top',
                        onClick: (e, legendItem, legend) => {
                            // Toggle dataset visibility
                            const index = legendItem.datasetIndex;
                            const chart = legend.chart;
                            const meta = chart.getDatasetMeta(index);
                            meta.hidden = meta.hidden === null ? !chart.data.datasets[index].hidden : null;
                            chart.update();
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Predicted Demand (kg)'
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Month'
                        }
                    }
                }
            }
        });
    }
    
    /**
     * Update gaps list with new data
     */
    updateGapsList(data) {
        const gapsContainer = document.querySelector('.regional-gap-list');
        if (!gapsContainer) return;
        
        // Clear existing gaps
        gapsContainer.innerHTML = '';
        
        if (data.gaps.length === 0) {
            gapsContainer.innerHTML = '<div class="regional-gap-item info"><span>No gaps found for current filters</span></div>';
            return;
        }
        
        // Add gap items
        data.gaps.forEach(gap => {
            const gapItem = document.createElement('div');
            gapItem.className = `regional-gap-item ${gap.status}`;
            
            gapItem.innerHTML = `
                <span class="gap-branch">${gap.branch_name}</span>
                <span class="gap-product">${gap.product_name}</span>
                <span class="gap-status">${gap.gap_text}</span>
            `;
            
            gapsContainer.appendChild(gapItem);
        });
    }
    
    /**
     * Show loading state
     */
    showLoadingState() {
        // Add loading indicators to chart containers
        const chartContainers = document.querySelectorAll('.chart-container');
        chartContainers.forEach(container => {
            if (!container.querySelector('.loading-indicator')) {
                container.classList.add('loading');
                const loader = document.createElement('div');
                loader.className = 'loading-indicator';
                loader.innerHTML = '<div class="spinner"></div><span>Loading...</span>';
                container.appendChild(loader);
            }
        });
    }
    
    /**
     * Hide loading state
     */
    hideLoadingState() {
        const loaders = document.querySelectorAll('.loading-indicator');
        loaders.forEach(loader => loader.remove());
        
        // Remove loading class from chart containers
        const chartContainers = document.querySelectorAll('.chart-container');
        chartContainers.forEach(container => {
            container.classList.remove('loading');
        });
    }
    
    /**
     * Show toast notification
     */
    showToast(message, type = 'info') {
        // Create toast element
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.textContent = message;
        
        // Add to page
        document.body.appendChild(toast);
        
        // Show toast
        setTimeout(() => toast.classList.add('show'), 100);
        
        // Remove toast after 3 seconds
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }
    
    /**
     * Export regional data as CSV
     */
    async exportData() {
        try {
            const params = new URLSearchParams(this.filters);
            const response = await fetch(`/admin/api/regional/export?${params}`);
            
            if (response.ok) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `regional_insights_${new Date().toISOString().slice(0, 10)}.csv`;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                window.URL.revokeObjectURL(url);
                
                this.showToast('Data exported successfully', 'success');
            } else {
                throw new Error('Export failed');
            }
        } catch (error) {
            console.error('Export error:', error);
            this.showToast('Failed to export data', 'error');
        }
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.regionalInsights = new RegionalInsights();
    
    // Add export button event listener
    const exportBtn = document.getElementById('export-btn');
    if (exportBtn) {
        exportBtn.addEventListener('click', () => {
            window.regionalInsights.exportData();
        });
    }
});
