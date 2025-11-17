document.addEventListener('DOMContentLoaded', () => {
    const branchInventoryModal = document.getElementById('branch-inventory-modal');
    const deleteConfirmModal = document.getElementById('delete-confirm-modal');
    const closeBtn = document.querySelector('.close-btn');
    const closeConfirmBtn = document.querySelector('.close-confirm-btn');
    const cancelDeleteBtn = document.getElementById('cancel-delete-btn');
    const branchesTableBody = document.querySelector('.branch-table tbody');
    const inventoryTableBody = document.querySelector('.inventory-table tbody');
    const modalTitle = document.querySelector('#branch-inventory-modal .modal-header h3');

    // Load branches into table
    async function loadBranches() {
        try {
            const res = await fetch('/api/branches');
            const json = await res.json();
            const branches = json.data || [];
            if (branchesTableBody) {
                branchesTableBody.innerHTML = branches.map(b => `
                    <tr>
                        <td>${escapeHtml(b.name)}</td>
                        <td>${escapeHtml(b.location)}</td>
                        <td>—</td>
                        <td class="${b.status === 'Operational' ? 'status-ok' : (b.status === 'Maintenance' ? 'status-warning' : 'status-danger')}">${escapeHtml(b.status)}</td>
                        <td>
                            <button class="table-action-btn view-btn" data-branch-id="${b.id}" data-branch-name="${escapeHtml(b.name)}">View</button>
                            <button class="table-action-btn edit-btn" data-branch-id="${b.id}">Edit</button>
                            <button class="table-action-btn delete-btn" data-branch-id="${b.id}">Delete</button>
                        </td>
                    </tr>
                `).join('');
                bindRowButtons();
            }
        } catch (e) {
            console.error('Failed to load branches', e);
        }
    }

    async function loadBranchInventory(branchId, branchName) {
        try {
            if (modalTitle && branchName) modalTitle.textContent = `${branchName} - Inventory`;
            const res = await fetch(`/api/branches/${branchId}/inventory?page=1&page_size=200`);
            const json = await res.json();
            const items = json.data || [];
            if (inventoryTableBody) {
                inventoryTableBody.innerHTML = items.map(it => `
                    <tr>
                        <td>${escapeHtml(it.rice_variant)}</td>
                        <td>${Number(it.stock_kg).toLocaleString()}</td>
                        <td>₱${Number(it.price).toFixed(2)}</td>
                        <td class="${it.availability === 'Available' ? 'status-ok' : (it.availability === 'Low Stock' ? 'status-warning' : 'status-danger')}">${escapeHtml(it.availability)}</td>
                        <td>${escapeHtml(it.batch_code || '—')}</td>
                        <td>
                            <button class="table-action-btn view-log-btn" data-item-id="${it.id}">View Log</button>
                            <button class="table-action-btn edit-item-btn" data-item-id="${it.id}">Edit</button>
                            <button class="table-action-btn delete-item-btn" data-item-id="${it.id}">Delete</button>
                        </td>
                    </tr>
                `).join('');
            }
            branchInventoryModal.style.display = 'block';
        } catch (e) {
            console.error('Failed to load inventory', e);
        }
    }

    function bindRowButtons() {
        document.querySelectorAll('.view-btn').forEach(button => {
            button.addEventListener('click', () => {
                const branchId = button.getAttribute('data-branch-id');
                const branchName = button.getAttribute('data-branch-name') || '';
                if (branchId) loadBranchInventory(branchId, branchName);
            });
        });
        document.querySelectorAll('.delete-btn, .delete-item-btn').forEach(button => {
            button.addEventListener('click', () => {
                deleteConfirmModal.style.display = 'block';
            });
        });
    }

    function escapeHtml(str) {
        return String(str ?? '').replace(/[&<>"']+/g, s => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[s]));
    }

    // Initial load
    loadBranches();

    // Close modals
    closeBtn.onclick = () => {
        branchInventoryModal.style.display = 'none';
    }
    closeConfirmBtn.onclick = () => {
        deleteConfirmModal.style.display = 'none';
    }
    cancelDeleteBtn.onclick = () => {
        deleteConfirmModal.style.display = 'none';
    }
    window.onclick = (event) => {
        if (event.target == branchInventoryModal) {
            branchInventoryModal.style.display = 'none';
        }
        if (event.target == deleteConfirmModal) {
            deleteConfirmModal.style.display = 'none';
        }
    }

    // Confirm delete action
    document.getElementById('confirm-delete-btn').addEventListener('click', () => {
        console.log('Item deleted');
        deleteConfirmModal.style.display = 'none';
        // Add actual deletion logic here
    });
}); 