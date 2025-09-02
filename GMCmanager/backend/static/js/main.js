// Navigation handling
document.addEventListener('DOMContentLoaded', function() {
    try {
        // Handle navigation clicks
        const navLinks = document.querySelectorAll('.nav-section a');
        navLinks.forEach(link => {
            link.addEventListener('click', function(e) {
                e.preventDefault();
                const href = this.getAttribute('href');
                if (href.startsWith('#')) {
                    const targetId = href.substring(1);
                    loadPage(targetId);
                } else {
                    // Handle direct page links
                    window.location.href = href;
                }
                
                // Update active state
                navLinks.forEach(l => l.classList.remove('active'));
                this.classList.add('active');
            });
        });

        // Initialize current page
        const currentPage = window.location.pathname.split('/').pop().replace('.html', '');
        if (currentPage && currentPage !== 'index') {
            initializePage(currentPage);
        } else {
            // Load dashboard by default
            initializePage('dashboard');
        }
    } catch (error) {
        console.error('Error initializing navigation:', error);
        showNotification('Error initializing page', 'error');
    }
});

// Page initialization function
function initializePage(pageId) {
    try {
        // Initialize page-specific scripts
        if (window[`init${pageId.charAt(0).toUpperCase() + pageId.slice(1)}`]) {
            window[`init${pageId.charAt(0).toUpperCase() + pageId.slice(1)}`]();
        }
    } catch (error) {
        console.error(`Error initializing ${pageId}:`, error);
        showNotification(`Error initializing ${pageId}`, 'error');
    }
}

// Common utility functions
function formatDate(date) {
    try {
        return new Date(date).toLocaleDateString();
    } catch (error) {
        console.error('Error formatting date:', error);
        return date;
    }
}

function formatNumber(number) {
    try {
        return new Intl.NumberFormat().format(number);
    } catch (error) {
        console.error('Error formatting number:', error);
        return number;
    }
}

// Export functions
function exportToCSV(data, filename) {
    try {
        const csvContent = "data:text/csv;charset=utf-8," + data;
        const encodedUri = encodeURI(csvContent);
        const link = document.createElement("a");
        link.setAttribute("href", encodedUri);
        link.setAttribute("download", filename);
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        showNotification('File exported successfully', 'success');
    } catch (error) {
        console.error('Error exporting to CSV:', error);
        showNotification('Error exporting file', 'error');
    }
}

function exportToPDF(elementId, filename) {
    try {
        const element = document.getElementById(elementId);
        if (!element) throw new Error('Element not found');
        html2pdf().from(element).save(filename);
        showNotification('File exported successfully', 'success');
    } catch (error) {
        console.error('Error exporting to PDF:', error);
        showNotification('Error exporting file', 'error');
    }
}

// Form validation
function validateForm(formId) {
    try {
        const form = document.getElementById(formId);
        if (!form) return false;

        const inputs = form.querySelectorAll('input[required], select[required]');
        let isValid = true;

        inputs.forEach(input => {
            if (!input.value.trim()) {
                isValid = false;
                input.classList.add('error');
                showNotification(`Please fill in ${input.name || 'required field'}`, 'error');
            } else {
                input.classList.remove('error');
            }
        });

        return isValid;
    } catch (error) {
        console.error('Error validating form:', error);
        return false;
    }
}

// Notification handling
function showNotification(message, type = 'info') {
    try {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, 3000);
    } catch (error) {
        console.error('Error showing notification:', error);
    }
}

// Chart initialization helper
function initChart(canvasId, type, data, options) {
    try {
        const canvas = document.getElementById(canvasId);
        if (!canvas) throw new Error(`Canvas element ${canvasId} not found`);
        
        const ctx = canvas.getContext('2d');
        return new Chart(ctx, {
            type: type,
            data: data,
            options: options
        });
    } catch (error) {
        console.error('Error initializing chart:', error);
        showNotification('Error loading chart', 'error');
        return null;
    }
}

// Password strength checker
function checkPasswordStrength(password) {
    try {
        let strength = 0;
        
        if (password.length >= 8) strength++;
        if (password.match(/[a-z]+/)) strength++;
        if (password.match(/[A-Z]+/)) strength++;
        if (password.match(/[0-9]+/)) strength++;
        if (password.match(/[^a-zA-Z0-9]+/)) strength++;
        
        return strength;
    } catch (error) {
        console.error('Error checking password strength:', error);
        return 0;
    }
}

// Session handling
function logout() {
    try {
        if (confirm('Are you sure you want to logout?')) {
            // Clear session data
            sessionStorage.clear();
            // Redirect to login page
            window.location.href = 'login.html';
        }
    } catch (error) {
        console.error('Error during logout:', error);
        showNotification('Error during logout', 'error');
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

// Error handling for uncaught errors
window.addEventListener('error', function(event) {
    console.error('Uncaught error:', event.error);
    showNotification('An error occurred. Please try again.', 'error');
});

// Handle unhandled promise rejections
window.addEventListener('unhandledrejection', function(event) {
    console.error('Unhandled promise rejection:', event.reason);
    showNotification('An error occurred. Please try again.', 'error');
}); 