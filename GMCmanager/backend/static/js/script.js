// Navigation handling
document.addEventListener('DOMContentLoaded', function() {
    // Handle navigation clicks
    const navLinks = document.querySelectorAll('.nav-section a');
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href').substring(1);
            loadPage(targetId);
            
            // Update active state
            navLinks.forEach(l => l.classList.remove('active'));
            this.classList.add('active');
        });
    });

    // Load dashboard by default
    loadPage('dashboard');
});

// Page loading function
function loadPage(pageId) {
    const mainContent = document.querySelector('.main-content');
    fetch(`${pageId}.html`)
        .then(response => response.text())
        .then(html => {
            mainContent.innerHTML = html;
            // Initialize page-specific scripts
            if (window[`init${pageId.charAt(0).toUpperCase() + pageId.slice(1)}`]) {
                window[`init${pageId.charAt(0).toUpperCase() + pageId.slice(1)}`]();
            }
        })
        .catch(error => {
            console.error('Error loading page:', error);
            mainContent.innerHTML = '<div class="error">Error loading page content</div>';
        });
}

// Common utility functions
function formatDate(date) {
    return new Date(date).toLocaleDateString();
}

function formatNumber(number) {
    return new Intl.NumberFormat().format(number);
}

// Export functions
function exportToCSV(data, filename) {
    const csvContent = "data:text/csv;charset=utf-8," + data;
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", filename);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

function exportToPDF(elementId, filename) {
    const element = document.getElementById(elementId);
    html2pdf().from(element).save(filename);
}

// Form validation
function validateForm(formId) {
    const form = document.getElementById(formId);
    if (!form) return false;

    const inputs = form.querySelectorAll('input[required], select[required]');
    let isValid = true;

    inputs.forEach(input => {
        if (!input.value.trim()) {
            isValid = false;
            input.classList.add('error');
        } else {
            input.classList.remove('error');
        }
    });

    return isValid;
}

// Notification handling
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.remove();
    }, 3000);
}

// Chart initialization helper
function initChart(canvasId, type, data, options) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    return new Chart(ctx, {
        type: type,
        data: data,
        options: options
    });
}

// Password strength checker
function checkPasswordStrength(password) {
    let strength = 0;
    
    if (password.length >= 8) strength++;
    if (password.match(/[a-z]+/)) strength++;
    if (password.match(/[A-Z]+/)) strength++;
    if (password.match(/[0-9]+/)) strength++;
    if (password.match(/[^a-zA-Z0-9]+/)) strength++;
    
    return strength;
}

// Session handling
function logout() {
    if (confirm('Are you sure you want to logout?')) {
        // Clear session data
        sessionStorage.clear();
        // Redirect to login page
        window.location.href = 'login.html';
    }
}

// Data fetching helper
async function fetchData(endpoint) {
    try {
        const response = await fetch(endpoint);
        if (!response.ok) throw new Error('Network response was not ok');
        return await response.json();
    } catch (error) {
        console.error('Error fetching data:', error);
        showNotification('Error loading data', 'error');
        return null;
    }
} 