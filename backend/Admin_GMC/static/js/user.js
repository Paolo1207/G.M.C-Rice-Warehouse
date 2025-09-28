// User.js - Real-time user management functionality
document.addEventListener('DOMContentLoaded', function() {
    loadUsers();
    setupEventListeners();
});

let currentUsers = [];

async function loadUsers() {
    try {
        const response = await fetch('/api/users');
        const data = await response.json();
        
        if (response.ok) {
            currentUsers = data.data;
            updateUserTable(data.data);
        } else {
            console.error('Failed to load users:', data.error);
        }
    } catch (error) {
        console.error('Error loading users:', error);
    }
}

function updateUserTable(users) {
    const tableBody = document.querySelector('.user-directory-table tbody');
    if (!tableBody) return;
    
    tableBody.innerHTML = '';
    
    users.forEach(user => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${user.name}</td>
            <td>${user.warehouse_id}</td>
            <td>${user.location}</td>
            <td>${user.contact_number}</td>
            <td><span class="role-badge ${user.role.toLowerCase()}">${user.role}</span></td>
            <td>
                <button class="btn-edit" onclick="editUser(${user.id})">Edit</button>
                <button class="btn-delete" onclick="deleteUser(${user.id})">Delete</button>
            </td>
        `;
        tableBody.appendChild(row);
    });
}

function setupEventListeners() {
    // Add new user button
    const addUserBtn = document.querySelector('.add-user-btn');
    if (addUserBtn) {
        addUserBtn.addEventListener('click', showAddUserModal);
    }
    
    // Search functionality
    const searchInput = document.querySelector('.user-filter-bar input');
    if (searchInput) {
        searchInput.addEventListener('input', performUserSearch);
    }
}

function showAddUserModal() {
    const modalHTML = `
        <div class="modal-overlay" id="addUserModal">
            <div class="modal-content">
                <div class="modal-header">
                    <h3>Add New User</h3>
                    <button class="modal-close" onclick="closeModal('addUserModal')">&times;</button>
                </div>
                <div class="modal-body">
                    <form id="addUserForm">
                        <div class="form-group">
                            <label for="name">Full Name:</label>
                            <input type="text" id="name" required>
                        </div>
                        <div class="form-group">
                            <label for="warehouse_id">Warehouse ID:</label>
                            <input type="text" id="warehouse_id" required>
                        </div>
                        <div class="form-group">
                            <label for="location">Location:</label>
                            <input type="text" id="location" required>
                        </div>
                        <div class="form-group">
                            <label for="contact_number">Contact Number:</label>
                            <input type="tel" id="contact_number" required>
                        </div>
                        <div class="form-group">
                            <label for="role">Role:</label>
                            <select id="role" required>
                                <option value="">Select Role</option>
                                <option value="Admin">Admin</option>
                                <option value="Manager">Manager</option>
                                <option value="Staff">Staff</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label for="email">Email:</label>
                            <input type="email" id="email">
                        </div>
                        <div class="form-actions">
                            <button type="button" onclick="closeModal('addUserModal')">Cancel</button>
                            <button type="submit">Add User</button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', modalHTML);
    
    // Handle form submission
    document.getElementById('addUserForm').addEventListener('submit', handleAddUser);
}

async function handleAddUser(event) {
    event.preventDefault();
    
    const formData = {
        name: document.getElementById('name').value,
        warehouse_id: document.getElementById('warehouse_id').value,
        location: document.getElementById('location').value,
        contact_number: document.getElementById('contact_number').value,
        role: document.getElementById('role').value,
        email: document.getElementById('email').value || null
    };
    
    try {
        const response = await fetch('/api/users', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });
        
        const result = await response.json();
        
        if (response.ok) {
            alert('User added successfully!');
            closeModal('addUserModal');
            loadUsers(); // Refresh the table
        } else {
            alert('Error adding user: ' + result.error);
        }
    } catch (error) {
        console.error('Error adding user:', error);
        alert('Error adding user. Please try again.');
    }
}

function editUser(userId) {
    const user = currentUsers.find(u => u.id === userId);
    if (!user) return;
    
    const modalHTML = `
        <div class="modal-overlay" id="editUserModal">
            <div class="modal-content">
                <div class="modal-header">
                    <h3>Edit User</h3>
                    <button class="modal-close" onclick="closeModal('editUserModal')">&times;</button>
                </div>
                <div class="modal-body">
                    <form id="editUserForm">
                        <input type="hidden" id="edit_user_id" value="${user.id}">
                        <div class="form-group">
                            <label for="edit_name">Full Name:</label>
                            <input type="text" id="edit_name" value="${user.name}" required>
                        </div>
                        <div class="form-group">
                            <label for="edit_warehouse_id">Warehouse ID:</label>
                            <input type="text" id="edit_warehouse_id" value="${user.warehouse_id}" required>
                        </div>
                        <div class="form-group">
                            <label for="edit_location">Location:</label>
                            <input type="text" id="edit_location" value="${user.location}" required>
                        </div>
                        <div class="form-group">
                            <label for="edit_contact_number">Contact Number:</label>
                            <input type="tel" id="edit_contact_number" value="${user.contact_number}" required>
                        </div>
                        <div class="form-group">
                            <label for="edit_role">Role:</label>
                            <select id="edit_role" required>
                                <option value="Admin" ${user.role === 'Admin' ? 'selected' : ''}>Admin</option>
                                <option value="Manager" ${user.role === 'Manager' ? 'selected' : ''}>Manager</option>
                                <option value="Staff" ${user.role === 'Staff' ? 'selected' : ''}>Staff</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label for="edit_email">Email:</label>
                            <input type="email" id="edit_email" value="${user.email || ''}">
                        </div>
                        <div class="form-actions">
                            <button type="button" onclick="closeModal('editUserModal')">Cancel</button>
                            <button type="submit">Update User</button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', modalHTML);
    
    // Handle form submission
    document.getElementById('editUserForm').addEventListener('submit', handleEditUser);
}

async function handleEditUser(event) {
    event.preventDefault();
    
    const userId = document.getElementById('edit_user_id').value;
    const formData = {
        name: document.getElementById('edit_name').value,
        warehouse_id: document.getElementById('edit_warehouse_id').value,
        location: document.getElementById('edit_location').value,
        contact_number: document.getElementById('edit_contact_number').value,
        role: document.getElementById('edit_role').value,
        email: document.getElementById('edit_email').value || null
    };
    
    try {
        const response = await fetch(`/api/users/${userId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });
        
        const result = await response.json();
        
        if (response.ok) {
            alert('User updated successfully!');
            closeModal('editUserModal');
            loadUsers(); // Refresh the table
        } else {
            alert('Error updating user: ' + result.error);
        }
    } catch (error) {
        console.error('Error updating user:', error);
        alert('Error updating user. Please try again.');
    }
}

function deleteUser(userId) {
    const user = currentUsers.find(u => u.id === userId);
    if (!user) return;
    
    if (confirm(`Are you sure you want to delete user "${user.name}"?`)) {
        // For now, just show an alert. You can implement actual deletion later
        alert(`Delete user ${userId}: ${user.name}`);
    }
}

function performUserSearch() {
    const searchInput = document.querySelector('.user-filter-bar input');
    const query = searchInput.value.toLowerCase().trim();
    
    if (!query) {
        updateUserTable(currentUsers);
        return;
    }
    
    const filteredUsers = currentUsers.filter(user => 
        user.name.toLowerCase().includes(query) ||
        user.warehouse_id.toLowerCase().includes(query) ||
        user.location.toLowerCase().includes(query) ||
        user.contact_number.includes(query) ||
        user.role.toLowerCase().includes(query)
    );
    
    updateUserTable(filteredUsers);
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.remove();
    }
}

// Add some CSS for role badges
const style = document.createElement('style');
style.textContent = `
    .role-badge {
        padding: 4px 8px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: 500;
        text-transform: uppercase;
    }
    
    .role-badge.admin {
        background-color: #ffebee;
        color: #c62828;
    }
    
    .role-badge.manager {
        background-color: #e8f5e8;
        color: #2e7d32;
    }
    
    .role-badge.staff {
        background-color: #e3f2fd;
        color: #1565c0;
    }
    
    .modal-overlay {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-color: rgba(0, 0, 0, 0.5);
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 1000;
    }
    
    .modal-content {
        background: white;
        border-radius: 8px;
        padding: 0;
        max-width: 500px;
        width: 90%;
        max-height: 90vh;
        overflow-y: auto;
    }
    
    .modal-header {
        padding: 20px;
        border-bottom: 1px solid #e0e0e0;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .modal-header h3 {
        margin: 0;
        color: #2e7d32;
    }
    
    .modal-close {
        background: none;
        border: none;
        font-size: 24px;
        cursor: pointer;
        color: #666;
    }
    
    .modal-body {
        padding: 20px;
    }
    
    .form-group {
        margin-bottom: 15px;
    }
    
    .form-group label {
        display: block;
        margin-bottom: 5px;
        font-weight: 500;
        color: #333;
    }
    
    .form-group input,
    .form-group select {
        width: 100%;
        padding: 8px 12px;
        border: 1px solid #ddd;
        border-radius: 4px;
        font-size: 14px;
    }
    
    .form-actions {
        display: flex;
        gap: 10px;
        justify-content: flex-end;
        margin-top: 20px;
    }
    
    .form-actions button {
        padding: 8px 16px;
        border: none;
        border-radius: 4px;
        cursor: pointer;
        font-size: 14px;
    }
    
    .form-actions button[type="button"] {
        background-color: #f5f5f5;
        color: #333;
    }
    
    .form-actions button[type="submit"] {
        background-color: #2e7d32;
        color: white;
    }
    
    .btn-edit,
    .btn-delete {
        padding: 4px 8px;
        border: none;
        border-radius: 4px;
        cursor: pointer;
        font-size: 12px;
        margin-right: 5px;
    }
    
    .btn-edit {
        background-color: #2196f3;
        color: white;
    }
    
    .btn-delete {
        background-color: #f44336;
        color: white;
    }
`;
document.head.appendChild(style);
