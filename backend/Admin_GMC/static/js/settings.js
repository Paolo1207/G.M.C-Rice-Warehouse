// settings.js - Admin Settings functionality
document.addEventListener('DOMContentLoaded', function() {
    initializeSettings();
});

let currentUser = null;
let csrfToken = null;

async function initializeSettings() {
    try {
        // Get CSRF token
        csrfToken = getCookie('csrf_token') || getCSRFFromMeta();
        
        // Load current user profile
        await loadUserProfile();
        
        // Setup event listeners
        setupEventListeners();
        
        // Setup password strength meter
        setupPasswordStrengthMeter();
        
        // Setup show/hide password toggles
        setupPasswordToggles();
        
    } catch (error) {
        console.error('Error initializing settings:', error);
        showToast('Failed to load settings', 'error');
    }
}

async function loadUserProfile() {
    try {
        const response = await fetch('/admin/api/me', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            currentUser = data.user;
            prefillProfileForm(data.user);
        } else if (response.status === 401) {
            showToast('Please log in to access settings', 'error');
            setTimeout(() => window.location.href = '/admin-login', 2000);
        } else {
            throw new Error('Failed to load profile');
        }
    } catch (error) {
        console.error('Error loading profile:', error);
        showToast('Failed to load user profile', 'error');
    }
}

function prefillProfileForm(user) {
    // Prefill profile form
    const nameInput = document.querySelector('input[type="text"]');
    const emailInput = document.querySelector('input[type="email"]');
    const resetEmailInput = document.getElementById('reset_email');
    
    if (nameInput) nameInput.value = user.name || '';
    if (emailInput) emailInput.value = user.email || '';
    
    // Auto-populate the reset email field with current user's email
    if (resetEmailInput) {
        resetEmailInput.value = user.email || '';
    }
}

function setupEventListeners() {
    // Profile form submission
    const profileForm = document.querySelector('.profile-form');
    if (profileForm) {
        profileForm.addEventListener('submit', handleProfileUpdate);
    }
    
    // Password form submission
    const passwordForm = document.querySelector('.password-form');
    if (passwordForm) {
        passwordForm.addEventListener('submit', handlePasswordChange);
    }
    
    // Reset password form submission
    const resetForm = document.querySelector('.reset-form');
    if (resetForm) {
        resetForm.addEventListener('submit', handlePasswordReset);
    }
}

async function handleProfileUpdate(event) {
    event.preventDefault();
    
    const formData = new FormData(event.target);
    const name = formData.get('name') || document.querySelector('input[type="text"]').value;
    const email = formData.get('email') || document.querySelector('input[type="email"]').value;
    
    // Validate email
    if (!isValidEmail(email)) {
        showFieldError('email', 'Please enter a valid email address');
        return;
    }
    
    const saveBtn = event.target.querySelector('.save-profile-btn');
    setButtonLoading(saveBtn, true);
    
    try {
        const response = await fetch('/admin/api/users/me', {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({
                name: name,
                email: email
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            if (data.requires_verification) {
                showToast(data.message, 'info');
                // Show verification notice with demo link if available
                showVerificationNotice(data.message, data.demo_link);
            } else {
                showToast('Profile updated successfully!', 'success');
            }
            clearFieldErrors();
        } else {
            handleApiError(data, response.status);
        }
    } catch (error) {
        console.error('Error updating profile:', error);
        showToast('Failed to update profile', 'error');
    } finally {
        setButtonLoading(saveBtn, false);
    }
}

async function handlePasswordChange(event) {
    event.preventDefault();
    
    const formData = new FormData(event.target);
    const currentPassword = formData.get('current_password') || 
        document.querySelector('input[type="password"]').value;
    const newPassword = formData.get('new_password') || 
        document.querySelectorAll('input[type="password"]')[1].value;
    const confirmPassword = formData.get('confirm_password') || 
        document.querySelectorAll('input[type="password"]')[2].value;
    
    // Validate passwords
    if (!currentPassword) {
        showFieldError('current_password', 'Current password is required');
        return;
    }
    
    if (!newPassword) {
        showFieldError('new_password', 'New password is required');
        return;
    }
    
    if (newPassword !== confirmPassword) {
        showFieldError('confirm_password', 'Passwords do not match');
        return;
    }
    
    if (newPassword.length < 8) {
        showFieldError('new_password', 'Password must be at least 8 characters');
        return;
    }
    
    const updateBtn = event.target.querySelector('.update-password-btn');
    setButtonLoading(updateBtn, true);
    
    try {
        const response = await fetch('/admin/api/auth/change_password', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({
                current_password: currentPassword,
                new_password: newPassword,
                confirm_password: confirmPassword
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showToast('Password changed successfully!', 'success');
            event.target.reset();
            clearFieldErrors();
        } else {
            handleApiError(data, response.status);
        }
    } catch (error) {
        console.error('Error changing password:', error);
        showToast('Failed to change password', 'error');
    } finally {
        setButtonLoading(updateBtn, false);
    }
}

async function handlePasswordReset(event) {
    event.preventDefault();
    
    const email = document.getElementById('reset_email').value;
    
    if (!email) {
        showToast('Email address is required', 'error');
        return;
    }
    
    const resetBtn = event.target.querySelector('.send-reset-btn');
    setButtonLoading(resetBtn, true);
    
    try {
        const response = await fetch('/admin/api/auth/reset', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({
                email: email
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            if (data.demo_link) {
                // Show demo link modal
                showPasswordResetDemo(data.message, data.demo_link);
            } else {
                showToast('Password reset link sent to your email!', 'success');
            }
        } else {
            handleApiError(data, response.status);
        }
    } catch (error) {
        console.error('Error sending reset link:', error);
        showToast('Failed to send reset link', 'error');
    } finally {
        setButtonLoading(resetBtn, false);
    }
}

function setupPasswordStrengthMeter() {
    const newPasswordInput = document.querySelectorAll('input[type="password"]')[1];
    const strengthBar = document.querySelector('.strength-bar');
    const strengthLabel = document.querySelector('.strength-label');
    
    if (newPasswordInput && strengthBar && strengthLabel) {
        newPasswordInput.addEventListener('input', function() {
            const password = this.value;
            const strength = calculatePasswordStrength(password);
            
            // Update strength bar
            strengthBar.style.width = strength.percentage + '%';
            strengthBar.style.backgroundColor = strength.color;
            strengthLabel.textContent = strength.label;
            strengthLabel.style.color = strength.color;
        });
    }
}

function calculatePasswordStrength(password) {
    let score = 0;
    let feedback = [];
    
    if (password.length >= 8) score += 1;
    else feedback.push('at least 8 characters');
    
    if (/[a-z]/.test(password)) score += 1;
    else feedback.push('lowercase letter');
    
    if (/[A-Z]/.test(password)) score += 1;
    else feedback.push('uppercase letter');
    
    if (/[0-9]/.test(password)) score += 1;
    else feedback.push('number');
    
    if (/[^A-Za-z0-9]/.test(password)) score += 1;
    else feedback.push('special character');
    
    if (score <= 2) {
        return { percentage: 25, color: '#f44336', label: 'Weak' };
    } else if (score <= 3) {
        return { percentage: 50, color: '#ff9800', label: 'Fair' };
    } else if (score <= 4) {
        return { percentage: 75, color: '#2196f3', label: 'Good' };
    } else {
        return { percentage: 100, color: '#4caf50', label: 'Strong' };
    }
}

function setupPasswordToggles() {
    const passwordInputs = document.querySelectorAll('input[type="password"]');
    
    // SVG icons for eye (show) and eye-slash (hide)
    const eyeIcon = `
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
            <circle cx="12" cy="12" r="3" fill="currentColor"></circle>
            <circle cx="12" cy="12" r="1" fill="white"></circle>
        </svg>
    `;
    const eyeSlashIcon = `
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
            <circle cx="12" cy="12" r="3" fill="currentColor"></circle>
            <circle cx="12" cy="12" r="1" fill="white"></circle>
            <line x1="1" y1="1" x2="23" y2="23" stroke="currentColor" stroke-width="2.5"></line>
        </svg>
    `;
    
    passwordInputs.forEach((input, index) => {
        const wrapper = input.parentElement;
        
        // Only add toggle if not already added
        if (wrapper.querySelector('.password-toggle')) {
            return;
        }
        
        const toggle = document.createElement('button');
        toggle.type = 'button';
        toggle.className = 'password-toggle';
        toggle.innerHTML = eyeIcon;
        toggle.setAttribute('aria-label', 'Toggle password visibility');
        
        wrapper.style.position = 'relative';
        wrapper.appendChild(toggle);
        
        toggle.addEventListener('click', function(e) {
            e.preventDefault();
            if (input.type === 'password') {
                input.type = 'text';
                toggle.innerHTML = eyeSlashIcon;
                toggle.setAttribute('aria-label', 'Hide password');
            } else {
                input.type = 'password';
                toggle.innerHTML = eyeIcon;
                toggle.setAttribute('aria-label', 'Show password');
            }
        });
    });
}

function setButtonLoading(button, loading) {
    if (loading) {
        button.disabled = true;
        button.dataset.originalText = button.textContent;
        button.innerHTML = '<span class="spinner"></span> Saving...';
        button.style.opacity = '0.7';
    } else {
        button.disabled = false;
        button.textContent = button.dataset.originalText || button.textContent;
        button.style.opacity = '1';
    }
}

function showFieldError(fieldName, message) {
    const field = document.querySelector(`[name="${fieldName}"]`) || 
                  document.querySelector(`#${fieldName}`) ||
                  document.querySelector(`input[type="${fieldName}"]`);
    
    if (field) {
        field.style.borderColor = '#f44336';
        field.style.backgroundColor = '#ffebee';
        
        // Remove existing error message
        const existingError = field.parentElement.querySelector('.field-error');
        if (existingError) existingError.remove();
        
        // Add new error message
        const errorDiv = document.createElement('div');
        errorDiv.className = 'field-error';
        errorDiv.style.cssText = 'color: #f44336; font-size: 0.85rem; margin-top: 0.25rem;';
        errorDiv.textContent = message;
        field.parentElement.appendChild(errorDiv);
    }
}

function clearFieldErrors() {
    const errorElements = document.querySelectorAll('.field-error');
    errorElements.forEach(el => el.remove());
    
    const inputs = document.querySelectorAll('input');
    inputs.forEach(input => {
        input.style.borderColor = '';
        input.style.backgroundColor = '';
    });
}

function handleApiError(data, status) {
    let message = 'An error occurred';
    
    if (status === 400) {
        message = data.error || 'Invalid request';
    } else if (status === 401) {
        message = 'Please log in to continue';
        setTimeout(() => window.location.href = '/login', 2000);
    } else if (status === 409) {
        message = data.error || 'Conflict with existing data';
    } else if (status === 422) {
        message = data.error || 'Validation error';
    } else {
        message = data.error || 'Server error';
    }
    
    showToast(message, 'error');
}

function showToast(message, type = 'info') {
    // Remove existing toasts
    const existingToasts = document.querySelectorAll('.toast');
    existingToasts.forEach(toast => toast.remove());
    
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 12px 20px;
        border-radius: 6px;
        color: white;
        font-weight: 500;
        z-index: 10000;
        max-width: 400px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        animation: slideIn 0.3s ease-out;
    `;
    
    if (type === 'success') {
        toast.style.backgroundColor = '#4caf50';
    } else if (type === 'error') {
        toast.style.backgroundColor = '#f44336';
    } else {
        toast.style.backgroundColor = '#2196f3';
    }
    
    toast.textContent = message;
    document.body.appendChild(toast);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        toast.style.animation = 'slideOut 0.3s ease-in';
        setTimeout(() => toast.remove(), 300);
    }, 5000);
}

function isValidEmail(email) {
    const pattern = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    return pattern.test(email);
}

function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
    return null;
}

function getCSRFFromMeta() {
    const meta = document.querySelector('meta[name="csrf-token"]');
    return meta ? meta.getAttribute('content') : null;
}

function showPasswordResetDemo(message, demoLink) {
    // Create modal for password reset demo
    const modal = document.createElement('div');
    modal.id = 'passwordResetDemoModal';
    modal.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        background: rgba(0,0,0,0.5);
        z-index: 1000;
        display: flex;
        align-items: center;
        justify-content: center;
    `;
    
    modal.innerHTML = `
        <div style="background: white; padding: 30px; border-radius: 8px; max-width: 500px; text-align: center;">
            <div style="background: #fff3cd; border: 1px solid #ffeaa7; border-radius: 8px; padding: 20px; margin-bottom: 20px;">
                <div style="display: flex; align-items: center; justify-content: center; margin-bottom: 15px;">
                    <div style="background: #ff9800; color: white; border-radius: 50%; width: 40px; height: 40px; display: flex; align-items: center; justify-content: center; margin-right: 10px;">
                        <svg width="20" height="20" fill="currentColor" viewBox="0 0 24 24">
                            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
                        </svg>
                    </div>
                    <h3 style="margin: 0; color: #856404;">Password Reset Link</h3>
                </div>
                <p style="margin: 0; color: #856404; font-size: 14px;">${message}</p>
                <div style="background: #e3f2fd; border: 1px solid #2196f3; border-radius: 4px; padding: 15px; margin-top: 15px;">
                    <p style="margin: 0 0 10px 0; color: #1976d2; font-weight: bold;">Demo Mode:</p>
                    <p style="margin: 0 0 15px 0; color: #1976d2; font-size: 14px;">Since email service is not configured, click the link below to reset your password:</p>
                    <a href="${demoLink}" style="background: #2196f3; color: white; padding: 10px 20px; text-decoration: none; border-radius: 4px; display: inline-block;">Click to Reset Password</a>
                </div>
            </div>
            <button onclick="closePasswordResetDemo()" style="background: #2e7d32; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer;">Got it!</button>
        </div>
    `;
    
    document.body.appendChild(modal);
}

function closePasswordResetDemo() {
    const modal = document.getElementById('passwordResetDemoModal');
    if (modal) {
        modal.remove();
    }
}

function showVerificationNotice(message, demoLink = null) {
    // Create verification notice modal
    const modal = document.createElement('div');
    modal.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        background: rgba(0,0,0,0.5);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 10000;
    `;
    
    const isDemo = demoLink !== null;
    const icon = isDemo ? '🔗' : '📧';
    const title = isDemo ? 'Demo Verification Link' : 'Email Verification Required';
    const bgColor = isDemo ? '#fff3e0' : '#e3f2fd';
    const textColor = isDemo ? '#f57c00' : '#1976d2';
    
    modal.innerHTML = `
        <div style="background: white; padding: 30px; border-radius: 10px; max-width: 500px; margin: 20px; box-shadow: 0 4px 20px rgba(0,0,0,0.3);">
            <div style="text-align: center; margin-bottom: 20px;">
                <div style="background: ${bgColor}; color: ${textColor}; padding: 15px; border-radius: 50%; width: 60px; height: 60px; margin: 0 auto 15px; display: flex; align-items: center; justify-content: center; font-size: 24px;">
                    ${icon}
                </div>
                <h2 style="color: ${textColor}; margin: 0;">${title}</h2>
            </div>
            
            <p style="color: #666; line-height: 1.6; margin-bottom: 20px;">${message}</p>
            
            ${isDemo ? `
                <div style="background: #f0f8ff; border: 1px solid #b3d9ff; padding: 15px; border-radius: 6px; margin: 20px 0;">
                    <p style="margin: 0; color: #1976d2; font-weight: 500;">
                        <strong>Demo Mode:</strong>
                    </p>
                    <p style="margin: 10px 0 0 0; color: #666;">
                        Since email service is not configured, click the link below to verify your email change:
                    </p>
                    <div style="margin: 15px 0;">
                        <a href="${demoLink}" target="_blank" 
                           style="background: #2e7d32; color: white; padding: 10px 15px; text-decoration: none; border-radius: 4px; display: inline-block; font-weight: 500;">
                            🔗 Click to Verify Email
                        </a>
                    </div>
                </div>
            ` : `
                <div style="background: #f0f8ff; border: 1px solid #b3d9ff; padding: 15px; border-radius: 6px; margin: 20px 0;">
                    <p style="margin: 0; color: #1976d2; font-weight: 500;">
                        <strong>Next Steps:</strong>
                    </p>
                    <ol style="margin: 10px 0 0 0; padding-left: 20px; color: #666;">
                        <li>Check your new email inbox</li>
                        <li>Look for an email from GMC System</li>
                        <li>Click the verification link in the email</li>
                        <li>Your email will be updated after verification</li>
                    </ol>
                </div>
            `}
            
            <div style="text-align: center;">
                <button onclick="this.closest('.verification-modal').remove()" 
                        style="background: #2e7d32; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; font-weight: 500;">
                    Got it!
                </button>
            </div>
        </div>
    `;
    
    modal.className = 'verification-modal';
    document.body.appendChild(modal);
    
    // Auto-close after 15 seconds (longer for demo)
    setTimeout(() => {
        if (modal.parentNode) {
            modal.remove();
        }
    }, isDemo ? 15000 : 10000);
}

// Add CSS for animations and readonly styling
const style = document.createElement('style');
style.textContent = `
    /* Readonly email field styling */
    #reset_email {
        background-color: #f5f5f5 !important;
        cursor: not-allowed !important;
        color: #666 !important;
        border: 1px solid #ddd !important;
    }
    
    #reset_email:focus {
        outline: none !important;
        border-color: #ddd !important;
        box-shadow: none !important;
    }
    
    @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    @keyframes slideOut {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
    
    .spinner {
        display: inline-block;
        width: 12px;
        height: 12px;
        border: 2px solid #ffffff;
        border-radius: 50%;
        border-top-color: transparent;
        animation: spin 1s ease-in-out infinite;
        margin-right: 8px;
    }
    
    @keyframes spin {
        to { transform: rotate(360deg); }
    }
`;
document.head.appendChild(style);
