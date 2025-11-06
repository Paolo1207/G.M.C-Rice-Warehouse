/**
 * Regional Insights - Live Data Integration
 * Handles Chart.js rendering, debounced filters, and real-time data updates
 */

class RegionalInsights {
    constructor() {
        this.charts = {};
        this.filters = {
            product: 'all',
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
        
        // Populate branch filter with correct order
        const branchSelect = document.getElementById('region-select');
        if (branchSelect && catalog.branches) {
            branchSelect.innerHTML = '<option value="all">All Branches</option>';
            
            // Define the correct order
            const branchOrder = ['Marawoy', 'Lipa', 'Malvar', 'Bulacnin', 'Boac', 'Sta. Cruz'];
            
            // Add branches in the correct order
            branchOrder.forEach(branchName => {
                if (catalog.branches.includes(branchName)) {
                    const option = document.createElement('option');
                    option.value = branchName;
                    option.textContent = branchName;
                    branchSelect.appendChild(option);
                }
            });
            
            // Add any remaining branches not in the predefined order
            catalog.branches.forEach(branch => {
                if (!branchOrder.includes(branch)) {
                    const option = document.createElement('option');
                    option.value = branch;
                    option.textContent = branch;
                    branchSelect.appendChild(option);
                }
            });
        }
    }
    
    /**
     * Setup filter event listeners with debouncing
     */
    setupFilters() {
        const filterSelects = ['product-select', 'region-select'];
        
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
    async handleFilterChange(selectId, value) {
        // Clear existing timer
        if (this.debounceTimer) {
            clearTimeout(this.debounceTimer);
        }
        
        // Update filter value
        const filterKey = selectId.replace('-select', '');
        if (filterKey === 'region') {
            this.filters.branch = value;
            // When branch changes, update product dropdown to show only products in that branch
            await this.updateProductsForBranch(value);
        } else {
            this.filters[filterKey] = value;
        }
        
        // Debug logging
        console.log('Filter changed:', selectId, 'Value:', value);
        console.log('Current filters:', this.filters);
        
        // Show loading state
        this.showLoadingState();
        
        // Debounce the API call
        this.debounceTimer = setTimeout(() => {
            this.loadAllData();
        }, 300);
    }
    
    /**
     * Update product dropdown based on selected branch
     */
    async updateProductsForBranch(branchName) {
        const productSelect = document.getElementById('product-select');
        if (!productSelect) return;
        
        // If "All Branches" is selected, show all products
        if (branchName === 'all') {
            // Reload all products from catalog
            try {
                const response = await fetch('/admin/api/catalog');
                const data = await response.json();
                if (data.ok && data.products) {
                    productSelect.innerHTML = '<option value="all">All Products</option>';
                    data.products.forEach(product => {
                        const option = document.createElement('option');
                        option.value = product;
                        option.textContent = product;
                        productSelect.appendChild(option);
                    });
                }
            } catch (error) {
                console.error('Error loading all products:', error);
            }
            return;
        }
        
        // Load products for the specific branch
        try {
            const response = await fetch(`/admin/api/products/branch?branch_name=${encodeURIComponent(branchName)}`);
            const data = await response.json();
            
            if (data.ok && data.items) {
                // Get unique product names from the branch's inventory
                const productNames = new Set();
                data.items.forEach(item => {
                    if (item.product_name) {
                        productNames.add(item.product_name);
                    }
                });
                
                // Update product dropdown
                productSelect.innerHTML = '<option value="all">All Products</option>';
                const sortedProducts = Array.from(productNames).sort();
                sortedProducts.forEach(productName => {
                    const option = document.createElement('option');
                    option.value = productName;
                    option.textContent = productName;
                    productSelect.appendChild(option);
                });
                
                // Reset product filter to "all" when branch changes
                productSelect.value = 'all';
                this.filters.product = 'all';
                
                console.log(`Updated product dropdown for branch "${branchName}": ${sortedProducts.length} products`);
            } else {
                console.error('Failed to load products for branch:', data.error);
                // Show empty state
                productSelect.innerHTML = '<option value="all">All Products</option>';
            }
        } catch (error) {
            console.error('Error loading products for branch:', error);
            // Show empty state on error
            productSelect.innerHTML = '<option value="all">All Products</option>';
        }
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
        
        // Debug logging
        console.log('updateGapsList - Current filters:', this.filters);
        console.log('Branch filter:', this.filters.branch, 'Product filter:', this.filters.product);
        console.log('Should show condensed view?', this.filters.branch === 'all' && this.filters.product === 'all');
        
        // Check if "All Branches" AND "All Products" are selected - show condensed view
        if (this.filters.branch === 'all' && this.filters.product === 'all') {
            console.log('Rendering condensed view');
            this.renderCondensedGapsView(data.gaps, gapsContainer);
        } else {
            console.log('Rendering detailed view');
            // Show detailed list for specific filters
            this.renderDetailedGapsView(data.gaps, gapsContainer);
        }
    }
    
    /**
     * Render condensed gaps view for "All Branches" filter
     */
    renderCondensedGapsView(gaps, container) {
        // Group gaps by branch and get top gaps per branch
        const branchGaps = {};
        
        gaps.forEach(gap => {
            if (!branchGaps[gap.branch_name]) {
                branchGaps[gap.branch_name] = [];
            }
            branchGaps[gap.branch_name].push(gap);
        });
        
        // Create branch selector buttons
        const branchSelector = document.createElement('div');
        branchSelector.className = 'branch-selector';
        branchSelector.style.cssText = 'margin-bottom: 16px; display: flex; gap: 8px; flex-wrap: wrap;';
        
        const branches = Object.keys(branchGaps);
        branches.forEach((branchName, index) => {
            const button = document.createElement('button');
            button.textContent = branchName;
            button.className = index === 0 ? 'branch-btn active' : 'branch-btn';
            button.style.cssText = `
                padding: 8px 16px;
                border: 2px solid #e0e0e0;
                border-radius: 20px;
                background: ${index === 0 ? '#2e7d32' : 'white'};
                color: ${index === 0 ? 'white' : '#374151'};
                cursor: pointer;
                font-weight: 500;
                transition: all 0.2s ease;
            `;
            
            button.addEventListener('click', () => {
                // Update active button
                branchSelector.querySelectorAll('.branch-btn').forEach(btn => {
                    btn.classList.remove('active');
                    btn.style.background = 'white';
                    btn.style.color = '#374151';
                });
                button.classList.add('active');
                button.style.background = '#2e7d32';
                button.style.color = 'white';
                
                // Debug logging
                console.log('Selected branch:', branchName);
                console.log('Gaps for this branch:', branchGaps[branchName]);
                
                // Show gaps for selected branch
                this.showGapsForBranch(branchGaps[branchName], container);
            });
            
            branchSelector.appendChild(button);
        });
        
        container.appendChild(branchSelector);
        
        // Show gaps for first branch by default
        if (branches.length > 0) {
            this.showGapsForBranch(branchGaps[branches[0]], container);
        }
    }
    
    /**
     * Show gaps for a specific branch
     */
    showGapsForBranch(branchGaps, container) {
        // Remove existing gap items (but keep branch selector)
        const existingGaps = container.querySelectorAll('.regional-gap-item');
        existingGaps.forEach(item => item.remove());
        
        if (branchGaps.length === 0) {
            const noGapsItem = document.createElement('div');
            noGapsItem.className = 'regional-gap-item info';
            noGapsItem.innerHTML = '<span>No gaps found for this branch</span>';
            container.appendChild(noGapsItem);
            return;
        }
        
        // Show top 5 gaps for the branch
        const topGaps = branchGaps.slice(0, 5);
        topGaps.forEach(gap => {
            const gapItem = document.createElement('div');
            gapItem.className = `regional-gap-item ${gap.status}`;
            
            gapItem.innerHTML = `
                <span class="gap-branch">${gap.branch_name}</span>
                <span class="gap-product">${gap.product_name}</span>
                <span class="gap-status">${gap.gap_text}</span>
            `;
            
            container.appendChild(gapItem);
        });
    }
    
    /**
     * Render detailed gaps view for specific branch
     */
    renderDetailedGapsView(gaps, container) {
        // Add gap items
        gaps.forEach(gap => {
            const gapItem = document.createElement('div');
            gapItem.className = `regional-gap-item ${gap.status}`;
            
            gapItem.innerHTML = `
                <span class="gap-branch">${gap.branch_name}</span>
                <span class="gap-product">${gap.product_name}</span>
                <span class="gap-status">${gap.gap_text}</span>
            `;
            
            container.appendChild(gapItem);
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
