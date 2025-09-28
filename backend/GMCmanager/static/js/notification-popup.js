/**
 * Global Notification Popup System for Manager
 * Shows real-time notifications when admin sends messages
 */

class ManagerNotificationSystem {
    constructor() {
        this.branchId = null;
        this.branchName = null;
        this.checkInterval = null;
        this.lastCheckTime = null;
        this.isInitialized = false;
        
        this.init();
    }

    async init() {
        if (this.isInitialized) return;
        
        // Track page load time for popup logic
        sessionStorage.setItem('pageLoadTime', Date.now().toString());
        
        // Check if this is a new login session (no existing session data)
        const hasExistingSession = sessionStorage.getItem('notificationSessionStarted');
        if (!hasExistingSession) {
            sessionStorage.setItem('notificationSessionStarted', 'true');
            // For new sessions, don't show popup immediately - wait for user to navigate
            sessionStorage.setItem('skipInitialPopup', 'true');
        }
        
        // Get manager's branch info
        await this.loadManagerBranch();
        
        // Start checking for notifications
        this.startPolling();
        
        this.isInitialized = true;
    }

    async loadManagerBranch() {
        try {
            const urlParams = new URLSearchParams(window.location.search);
            this.branchId = urlParams.get('branch') || null;
            this.branchName = urlParams.get('branch_name') || null;
            
            // If no branch in URL, get from API
            if (!this.branchId) {
                const response = await fetch('/manager/api/branches');
                const data = await response.json();
                if (data.ok && data.branches && data.branches.length > 0) {
                    this.branchId = data.branches[0].id;
                    this.branchName = data.branches[0].name;
                }
            }
            
            // Store branch info for later use
            this.currentBranchId = this.branchId;
            this.currentBranchName = this.branchName;
        } catch (error) {
            console.error('Error loading manager branch:', error);
        }
    }

    startPolling() {
        // Check every 30 seconds for new notifications
        this.checkInterval = setInterval(() => {
            this.checkForNewNotifications();
        }, 30000);
        
        // Check immediately on page load, but with a delay to avoid showing on fresh login
        setTimeout(() => this.checkForNewNotifications(), 5000);
    }

    async checkForNewNotifications() {
        try {
            const response = await fetch('/manager/api/notifications/unread-count');
            const data = await response.json();
            
            if (data.ok && data.unread_count > 0) {
                // Check if we've already shown a popup for this session
                const lastPopupTime = sessionStorage.getItem('lastNotificationPopup');
                const currentTime = Date.now();
                const pageLoadTime = sessionStorage.getItem('pageLoadTime');
                
                // Only show popup if:
                // 1. We haven't shown one in this session, OR
                // 2. It's been more than 2 minutes since last popup, OR
                // 3. The unread count has increased (NEW NOTIFICATIONS), OR
                // 4. This is a fresh page load and we haven't shown popup yet
                // BUT NOT if this is the initial login popup (skipInitialPopup is set)
                const lastUnreadCount = parseInt(sessionStorage.getItem('lastUnreadCount') || '0');
                const isFreshPageLoad = !pageLoadTime || (currentTime - parseInt(pageLoadTime)) < 10000; // 10 seconds
                const skipInitialPopup = sessionStorage.getItem('skipInitialPopup') === 'true';
                
                // Most important: show popup if unread count increased (new notifications)
                const hasNewNotifications = data.unread_count > lastUnreadCount;
                
                // Debug logging
                console.log('Notification check:', {
                    currentUnread: data.unread_count,
                    lastUnread: lastUnreadCount,
                    hasNewNotifications,
                    lastPopupTime: lastPopupTime ? new Date(parseInt(lastPopupTime)).toLocaleTimeString() : 'never',
                    timeSinceLastPopup: lastPopupTime ? (currentTime - parseInt(lastPopupTime)) / 1000 : 'N/A',
                    skipInitialPopup,
                    isFreshPageLoad
                });
                
                const shouldShowPopup = hasNewNotifications || // NEW NOTIFICATIONS - always show
                                      !lastPopupTime || 
                                      (currentTime - parseInt(lastPopupTime)) > 120000 || // 2 minutes (reduced from 5)
                                      (isFreshPageLoad && !lastPopupTime && !skipInitialPopup);
                
                // Clear the skip flag after first check
                if (skipInitialPopup) {
                    sessionStorage.removeItem('skipInitialPopup');
                }
                
                if (shouldShowPopup) {
                    console.log('Showing notification popup for', data.unread_count, 'unread notifications');
                    this.showNotificationPopup(data.unread_count);
                    
                    // Store the popup time and unread count
                    sessionStorage.setItem('lastNotificationPopup', currentTime.toString());
                    sessionStorage.setItem('lastUnreadCount', data.unread_count.toString());
                } else {
                    console.log('Not showing popup - conditions not met');
                }
            } else {
                // No unread notifications, clear the stored data
                sessionStorage.removeItem('lastNotificationPopup');
                sessionStorage.removeItem('lastUnreadCount');
            }
        } catch (error) {
            console.error('Error checking for new notifications:', error);
        }
    }

    showNotificationPopup(count) {
        // Don't show if already on notifications page
        if (window.location.pathname.includes('/notifications')) {
            return;
        }

        // Don't show if popup already exists
        if (document.querySelector('.manager-notification-popup')) {
            return;
        }

        // Create popup element
        const popup = document.createElement('div');
        popup.className = 'manager-notification-popup';
        popup.innerHTML = `
            <div class="popup-content">
                <div class="popup-icon">
                    <i class="fas fa-bell"></i>
                </div>
                <div class="popup-text">
                    <h4>New Notification${count > 1 ? 's' : ''}</h4>
                    <p>You have ${count} new notification${count > 1 ? 's' : ''} from Admin</p>
                </div>
                <button class="popup-close" onclick="managerNotificationSystem.closePopup(this)">
                    <i class="fas fa-times"></i>
                </button>
            </div>
            <div class="popup-actions">
                <button class="btn primary" onclick="managerNotificationSystem.goToNotifications()">View Notifications</button>
                <button class="btn secondary" onclick="managerNotificationSystem.closePopup(this)">Dismiss</button>
            </div>
        `;
        
        // Add to page
        document.body.appendChild(popup);
        
        // Auto-remove after 10 seconds
        setTimeout(() => {
            if (popup.parentNode) {
                popup.remove();
            }
        }, 10000);
    }

    closePopup(element) {
        const popup = element.closest('.manager-notification-popup');
        if (popup) {
            popup.remove();
        }
    }

    goToNotifications() {
        // Clear popup tracking since user is going to view notifications
        sessionStorage.removeItem('lastNotificationPopup');
        sessionStorage.removeItem('lastUnreadCount');
        
        // Preserve branch parameters when navigating to notifications
        let notificationsUrl = '/manager/notifications';
        
        // Use stored branch info or get from current URL
        const branchId = this.currentBranchId || new URLSearchParams(window.location.search).get('branch');
        const branchName = this.currentBranchName || new URLSearchParams(window.location.search).get('branch_name');
        
        if (branchId && branchName) {
            notificationsUrl += `?branch=${branchId}&branch_name=${encodeURIComponent(branchName)}`;
        }
        
        window.location.href = notificationsUrl;
    }

    destroy() {
        if (this.checkInterval) {
            clearInterval(this.checkInterval);
        }
    }
}

// Initialize global notification system
let managerNotificationSystem = null;

document.addEventListener('DOMContentLoaded', () => {
    managerNotificationSystem = new ManagerNotificationSystem();
});

// Clean up on page unload
window.addEventListener('beforeunload', () => {
    if (managerNotificationSystem) {
        managerNotificationSystem.destroy();
    }
});

// Clear session data when user logs out (if there's a logout event)
window.addEventListener('storage', (e) => {
    if (e.key === 'logout' && e.newValue === 'true') {
        sessionStorage.removeItem('lastNotificationPopup');
        sessionStorage.removeItem('lastUnreadCount');
        sessionStorage.removeItem('notificationSessionStarted');
        sessionStorage.removeItem('skipInitialPopup');
        sessionStorage.removeItem('pageLoadTime');
    }
});

// Helper function to clear notification session data (for testing)
window.clearNotificationSession = function() {
    sessionStorage.removeItem('lastNotificationPopup');
    sessionStorage.removeItem('lastUnreadCount');
    sessionStorage.removeItem('notificationSessionStarted');
    sessionStorage.removeItem('skipInitialPopup');
    sessionStorage.removeItem('pageLoadTime');
    console.log('Notification session data cleared. Popup will show on next check.');
};

// Helper function to manually trigger notification check (for testing)
window.triggerNotificationCheck = function() {
    if (managerNotificationSystem) {
        console.log('Manually triggering notification check...');
        managerNotificationSystem.checkForNewNotifications();
    } else {
        console.log('Notification system not initialized');
    }
};

// Helper function to check current notification state (for debugging)
window.checkNotificationState = async function() {
    try {
        const response = await fetch('/manager/api/notifications/unread-count');
        const data = await response.json();
        console.log('Current notification state:', data);
        
        const sessionData = {
            lastPopupTime: sessionStorage.getItem('lastNotificationPopup'),
            lastUnreadCount: sessionStorage.getItem('lastUnreadCount'),
            notificationSessionStarted: sessionStorage.getItem('notificationSessionStarted'),
            skipInitialPopup: sessionStorage.getItem('skipInitialPopup'),
            pageLoadTime: sessionStorage.getItem('pageLoadTime')
        };
        console.log('Session data:', sessionData);
        
        return { apiData: data, sessionData };
    } catch (error) {
        console.error('Error checking notification state:', error);
        return { error: error.message };
    }
};
