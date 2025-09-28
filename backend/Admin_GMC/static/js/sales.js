// Sales.js - Real-time sales functionality
document.addEventListener('DOMContentLoaded', function() {
    loadSalesData();
    loadBranches();
    initializeSalesCharts();
    
    // Set up event listeners
    setupEventListeners();
});

let currentSalesData = [];
let currentPage = 1;
let totalPages = 1;

async function loadSalesData(page = 1) {
    try {
        const response = await fetch(`/api/sales?page=${page}&page_size=20`);
        const data = await response.json();
        
        if (response.ok) {
            currentSalesData = data.data;
            currentPage = data.pagination.page;
            totalPages = Math.ceil(data.pagination.total / data.pagination.page_size);
            
            updateSalesTable(data.data);
            updatePagination();
        } else {
            console.error('Failed to load sales data:', data.error);
        }
    } catch (error) {
        console.error('Error loading sales data:', error);
    }
}

async function loadBranches() {
    try {
        const response = await fetch('/api/branches');
        const data = await response.json();
        
        if (response.ok) {
            populateBranchSelects(data.data);
        }
    } catch (error) {
        console.error('Error loading branches:', error);
    }
}

function populateBranchSelects(branches) {
    const branchSelects = document.querySelectorAll('select[data-branch-select]');
    
    branchSelects.forEach(select => {
        select.innerHTML = '<option value="">Select Branch</option>';
        branches.forEach(branch => {
            const option = document.createElement('option');
            option.value = branch.id;
            option.textContent = branch.name;
            select.appendChild(option);
        });
    });
}

function updateSalesTable(sales) {
    const tableBody = document.querySelector('.sales-table tbody');
    if (!tableBody) return;
    
    tableBody.innerHTML = '';
    
    sales.forEach(sale => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${sale.customer_name || 'Walk-in Customer'}</td>
            <td>${sale.rice_variant}</td>
            <td>${sale.quantity_kg} kg</td>
            <td>₱${sale.price_per_kg.toFixed(2)}</td>
            <td>₱${sale.total_amount.toLocaleString()}</td>
            <td>${formatDate(sale.sale_date)}</td>
            <td>
                <button class="btn-edit" onclick="editSale(${sale.id})">Edit</button>
                <button class="btn-delete" onclick="deleteSale(${sale.id})">Delete</button>
            </td>
        `;
        tableBody.appendChild(row);
    });
}

function updatePagination() {
    const paginationContainer = document.querySelector('.pagination');
    if (!paginationContainer) return;
    
    paginationContainer.innerHTML = '';
    
    // Previous button
    if (currentPage > 1) {
        const prevBtn = document.createElement('button');
        prevBtn.textContent = 'Previous';
        prevBtn.onclick = () => loadSalesData(currentPage - 1);
        paginationContainer.appendChild(prevBtn);
    }
    
    // Page numbers
    for (let i = 1; i <= totalPages; i++) {
        if (i === 1 || i === totalPages || (i >= currentPage - 2 && i <= currentPage + 2)) {
            const pageBtn = document.createElement('button');
            pageBtn.textContent = i;
            pageBtn.className = i === currentPage ? 'active' : '';
            pageBtn.onclick = () => loadSalesData(i);
            paginationContainer.appendChild(pageBtn);
        } else if (i === currentPage - 3 || i === currentPage + 3) {
            const ellipsis = document.createElement('span');
            ellipsis.textContent = '...';
            paginationContainer.appendChild(ellipsis);
        }
    }
    
    // Next button
    if (currentPage < totalPages) {
        const nextBtn = document.createElement('button');
        nextBtn.textContent = 'Next';
        nextBtn.onclick = () => loadSalesData(currentPage + 1);
        paginationContainer.appendChild(nextBtn);
    }
}

function setupEventListeners() {
    // Add new sale button
    const addSaleBtn = document.querySelector('.add-sale-btn');
    if (addSaleBtn) {
        addSaleBtn.addEventListener('click', showAddSaleModal);
    }
    
    // Filter changes
    const dateRangeSelect = document.querySelector('select[data-filter="date-range"]');
    if (dateRangeSelect) {
        dateRangeSelect.addEventListener('change', applyFilters);
    }
    
    const riceVariantSelect = document.querySelector('select[data-filter="rice-variant"]');
    if (riceVariantSelect) {
        riceVariantSelect.addEventListener('change', applyFilters);
    }
}

function showAddSaleModal() {
    // Create modal HTML
    const modalHTML = `
        <div class="modal-overlay" id="addSaleModal">
            <div class="modal-content">
                <div class="modal-header">
                    <h3>Add New Sale</h3>
                    <button class="modal-close" onclick="closeModal('addSaleModal')">&times;</button>
                </div>
                <div class="modal-body">
                    <form id="addSaleForm">
                        <div class="form-group">
                            <label for="branch_id">Branch:</label>
                            <select id="branch_id" required>
                                <option value="">Select Branch</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label for="rice_variant">Rice Variant:</label>
                            <select id="rice_variant" required>
                                <option value="">Select Rice Variant</option>
                                <option value="Crystal Dinorado">Crystal Dinorado</option>
                                <option value="Sinandomeng">Sinandomeng</option>
                                <option value="Jasmine">Jasmine</option>
                                <option value="Premium Rice">Premium Rice</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label for="quantity_kg">Quantity (kg):</label>
                            <input type="number" id="quantity_kg" min="1" required>
                        </div>
                        <div class="form-group">
                            <label for="price_per_kg">Price per kg (₱):</label>
                            <input type="number" id="price_per_kg" min="0" step="0.01" required>
                        </div>
                        <div class="form-group">
                            <label for="customer_name">Customer Name:</label>
                            <input type="text" id="customer_name" placeholder="Walk-in Customer">
                        </div>
                        <div class="form-group">
                            <label for="sale_date">Sale Date:</label>
                            <input type="date" id="sale_date" required>
                        </div>
                        <div class="form-actions">
                            <button type="button" onclick="closeModal('addSaleModal')">Cancel</button>
                            <button type="submit">Add Sale</button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', modalHTML);
    
    // Populate branch select
    populateBranchSelectsInModal();
    
    // Set default date to today
    document.getElementById('sale_date').value = new Date().toISOString().split('T')[0];
    
    // Handle form submission
    document.getElementById('addSaleForm').addEventListener('submit', handleAddSale);
}

async function populateBranchSelectsInModal() {
    try {
        const response = await fetch('/api/branches');
        const data = await response.json();
        
        if (response.ok) {
            const branchSelect = document.getElementById('branch_id');
            branchSelect.innerHTML = '<option value="">Select Branch</option>';
            data.data.forEach(branch => {
                const option = document.createElement('option');
                option.value = branch.id;
                option.textContent = branch.name;
                branchSelect.appendChild(option);
            });
        }
    } catch (error) {
        console.error('Error loading branches for modal:', error);
    }
}

async function handleAddSale(event) {
    event.preventDefault();
    
    const formData = {
        branch_id: parseInt(document.getElementById('branch_id').value),
        rice_variant: document.getElementById('rice_variant').value,
        quantity_kg: parseInt(document.getElementById('quantity_kg').value),
        price_per_kg: parseFloat(document.getElementById('price_per_kg').value),
        customer_name: document.getElementById('customer_name').value || null,
        sale_date: document.getElementById('sale_date').value
    };
    
    try {
        const response = await fetch('/api/sales', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });
        
        const result = await response.json();
        
        if (response.ok) {
            alert('Sale added successfully!');
            closeModal('addSaleModal');
            loadSalesData(currentPage); // Refresh the table
        } else {
            alert('Error adding sale: ' + result.error);
        }
    } catch (error) {
        console.error('Error adding sale:', error);
        alert('Error adding sale. Please try again.');
    }
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.remove();
    }
}

function editSale(saleId) {
    // Find the sale in current data
    const sale = currentSalesData.find(s => s.id === saleId);
    if (!sale) return;
    
    // For now, just show an alert. You can implement a full edit modal later
    alert(`Edit sale ${saleId}: ${sale.customer_name} - ${sale.rice_variant}`);
}

function deleteSale(saleId) {
    if (confirm('Are you sure you want to delete this sale?')) {
        // For now, just show an alert. You can implement actual deletion later
        alert(`Delete sale ${saleId}`);
    }
}

function applyFilters() {
    // For now, just reload the data. You can implement actual filtering later
    loadSalesData(1);
}

function initializeSalesCharts() {
    // Initialize sales analytics charts
    loadSalesAnalytics();
}

async function loadSalesAnalytics() {
    try {
        const response = await fetch('/api/analytics/sales?days=30');
        const data = await response.json();
        
        if (response.ok) {
            updateSalesAnalyticsChart(data.data);
        }
    } catch (error) {
        console.error('Error loading sales analytics:', error);
    }
}

function updateSalesAnalyticsChart(analyticsData) {
    const ctx = document.getElementById('salesAnalyticsChart');
    if (!ctx) return;
    
    const labels = Object.keys(analyticsData);
    const quantities = Object.values(analyticsData).map(item => item.total_quantity);
    const amounts = Object.values(analyticsData).map(item => item.total_amount);
    
    if (window.salesAnalyticsChart) {
        window.salesAnalyticsChart.destroy();
    }
    
    window.salesAnalyticsChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Total Quantity (kg)',
                data: quantities,
                backgroundColor: 'rgba(46, 125, 50, 0.8)',
                borderColor: '#2e7d32',
                borderWidth: 1
            }, {
                label: 'Total Amount (₱)',
                data: amounts,
                backgroundColor: 'rgba(76, 175, 80, 0.8)',
                borderColor: '#4caf50',
                borderWidth: 1,
                yAxisID: 'y1'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    type: 'linear',
                    display: true,
                    position: 'left',
                    title: {
                        display: true,
                        text: 'Quantity (kg)'
                    }
                },
                y1: {
                    type: 'linear',
                    display: true,
                    position: 'right',
                    title: {
                        display: true,
                        text: 'Amount (₱)'
                    },
                    grid: {
                        drawOnChartArea: false,
                    },
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

function formatDate(dateString) {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}
