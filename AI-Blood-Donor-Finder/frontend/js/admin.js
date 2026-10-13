/**
 * Admin Portal Management Controller
 */

document.addEventListener('DOMContentLoaded', () => {
  initAdminPortal();
});

async function initAdminPortal() {
  const adminPage = document.getElementById('admin-page');
  if (!adminPage) return;

  if (!requireAuth('admin')) return;

  setupAdminTabs();
  await loadAdminDashboard();
  loadAdminUsers();
  loadAdminDonors();
  loadAdminRequests();
  loadAdminLogs();
}

function setupAdminTabs() {
  const tabs = document.querySelectorAll('.admin-tab-btn');
  const sections = document.querySelectorAll('.admin-section');

  tabs.forEach(tab => {
    tab.addEventListener('click', () => {
      const target = tab.getAttribute('data-target');
      tabs.forEach(t => t.classList.remove('active'));
      sections.forEach(s => s.style.display = 'none');

      tab.classList.add('active');
      const targetSec = document.getElementById(target);
      if (targetSec) targetSec.style.display = 'block';
    });
  });
}

async function loadAdminDashboard() {
  try {
    const res = await apiRequest('/admin/dashboard');
    if (res.success && res.metrics) {
      const m = res.metrics;
      document.getElementById('admin-kpi-users').textContent = m.total_users;
      document.getElementById('admin-kpi-donors').textContent = m.total_donors;
      document.getElementById('admin-kpi-emergencies').textContent = m.active_emergencies;
      document.getElementById('admin-kpi-requests').textContent = m.total_requests;

      // Blood group chart/pill display
      const bgBox = document.getElementById('admin-bg-breakdown');
      if (bgBox && res.blood_groups) {
        bgBox.innerHTML = Object.entries(res.blood_groups).map(([bg, count]) => `
          <div style="background: #f8fafc; border: 1px solid var(--border); padding: 10px 16px; border-radius: var(--radius-md); text-align: center;">
            <strong style="color: var(--primary); font-size: 1.1rem;">${bg}</strong>
            <div style="font-size: 0.85rem; color: var(--text-muted);">${count} donors</div>
          </div>
        `).join('');
      }
    }
  } catch (err) {
    showToast('Error', 'Failed to load admin metrics', 'error');
  }
}

async function loadAdminUsers() {
  const tableBody = document.getElementById('admin-users-tbody');
  if (!tableBody) return;

  try {
    const res = await apiRequest('/admin/users');
    if (res.success && res.users) {
      tableBody.innerHTML = res.users.map(u => `
        <tr>
          <td>#${u.user_id}</td>
          <td><strong>${u.name}</strong></td>
          <td>${u.email}</td>
          <td>${u.phone}</td>
          <td><span class="badge-status ${u.role === 'admin' ? 'emergency' : 'pending'}">${u.role.toUpperCase()}</span></td>
          <td>
            <span class="badge-status ${u.is_active ? 'accepted' : 'rejected'}">
              ${u.is_active ? 'Active' : 'Disabled'}
            </span>
          </td>
          <td>
            <div style="display: flex; gap: 8px;">
              <button class="btn btn-outline btn-sm toggle-user-btn" data-id="${u.user_id}" data-active="${u.is_active}">
                ${u.is_active ? 'Deactivate' : 'Activate'}
              </button>
              ${u.role !== 'admin' ? `
                <button class="btn btn-outline btn-sm delete-user-btn" data-id="${u.user_id}" style="color: var(--danger); border-color: var(--danger);">
                  Delete
                </button>
              ` : ''}
            </div>
          </td>
        </tr>
      `).join('');

      // Wire events
      tableBody.querySelectorAll('.toggle-user-btn').forEach(btn => {
        btn.addEventListener('click', () => {
          const id = btn.getAttribute('data-id');
          const current = btn.getAttribute('data-active') === '1' || btn.getAttribute('data-active') === 'true';
          toggleUserStatus(id, !current);
        });
      });

      tableBody.querySelectorAll('.delete-user-btn').forEach(btn => {
        btn.addEventListener('click', () => {
          const id = btn.getAttribute('data-id');
          if (confirm('Are you sure you want to permanently delete this user account?')) {
            deleteUser(id);
          }
        });
      });
    }
  } catch (err) {
    tableBody.innerHTML = `<tr><td colspan="7" style="text-align: center; color: var(--danger);">Failed to load users.</td></tr>`;
  }
}

async function toggleUserStatus(userId, newActiveState) {
  showLoading('Updating account status...');
  try {
    const res = await apiRequest(`/admin/users/${userId}/status`, {
      method: 'PUT',
      body: { is_active: newActiveState }
    });
    hideLoading();
    showToast('Success', res.message, 'success');
    loadAdminUsers();
  } catch (err) {
    hideLoading();
    showToast('Error', err.message, 'error');
  }
}

async function deleteUser(userId) {
  showLoading('Deleting user...');
  try {
    const res = await apiRequest(`/admin/users/${userId}`, { method: 'DELETE' });
    hideLoading();
    showToast('Success', res.message, 'success');
    loadAdminUsers();
  } catch (err) {
    hideLoading();
    showToast('Error', err.message, 'error');
  }
}

async function loadAdminDonors() {
  const tableBody = document.getElementById('admin-donors-tbody');
  if (!tableBody) return;

  try {
    const res = await apiRequest('/admin/donors');
    if (res.success && res.donors) {
      tableBody.innerHTML = res.donors.map(d => `
        <tr>
          <td>#${d.donor_id}</td>
          <td><strong>${d.name}</strong> <br><small class="text-muted">${d.gender}, ${d.age}y</small></td>
          <td><span class="compat-tag can-receive" style="padding: 2px 8px;">${d.blood_group}</span></td>
          <td>${d.city} (${d.area})</td>
          <td>${d.phone}</td>
          <td><span class="badge-status ${d.availability === 'Available' ? 'accepted' : 'rejected'}">${d.availability}</span></td>
          <td>${d.last_donation_date || 'None'}</td>
          <td>
            <button class="btn btn-outline btn-sm delete-donor-btn" data-id="${d.donor_id}" style="color: var(--danger); border-color: var(--danger);">
              Remove
            </button>
          </td>
        </tr>
      `).join('');

      tableBody.querySelectorAll('.delete-donor-btn').forEach(btn => {
        btn.addEventListener('click', () => {
          const id = btn.getAttribute('data-id');
          if (confirm('Delete this donor profile?')) {
            deleteDonor(id);
          }
        });
      });
    }
  } catch (err) {
    tableBody.innerHTML = `<tr><td colspan="8" style="text-align: center; color: var(--danger);">Failed to load donors.</td></tr>`;
  }
}

async function deleteDonor(donorId) {
  showLoading('Removing donor...');
  try {
    const res = await apiRequest(`/admin/donors/${donorId}`, { method: 'DELETE' });
    hideLoading();
    showToast('Success', res.message, 'success');
    loadAdminDonors();
  } catch (err) {
    hideLoading();
    showToast('Error', err.message, 'error');
  }
}

async function loadAdminRequests() {
  const tableBody = document.getElementById('admin-requests-tbody');
  if (!tableBody) return;

  try {
    const res = await apiRequest('/admin/requests');
    if (res.success && res.requests) {
      tableBody.innerHTML = res.requests.map(r => `
        <tr>
          <td><strong>${r.request_id}</strong></td>
          <td>${r.patient_name}</td>
          <td><span class="compat-tag can-receive" style="padding: 2px 8px;">${r.blood_group}</span></td>
          <td>${r.hospital_name}, ${r.city}</td>
          <td><span class="badge-status ${r.urgency.toLowerCase()}">${r.urgency}</span></td>
          <td>
            <select class="form-control change-req-status" data-id="${r.request_id}" style="padding: 4px 8px; font-size: 0.85rem;">
              ${['Pending', 'Matching', 'Donors Found', 'Fulfilled', 'Cancelled'].map(s => `
                <option value="${s}" ${r.status === s ? 'selected' : ''}>${s}</option>
              `).join('')}
            </select>
          </td>
          <td><small class="text-muted">${r.required_date}</small></td>
        </tr>
      `).join('');

      tableBody.querySelectorAll('.change-req-status').forEach(sel => {
        sel.addEventListener('change', async (e) => {
          const reqId = sel.getAttribute('data-id');
          const newStatus = sel.value;
          try {
            await apiRequest(`/requests/${reqId}/status`, {
              method: 'PUT',
              body: { status: newStatus }
            });
            showToast('Updated', `Request ${reqId} marked as ${newStatus}`, 'success');
          } catch (err) {
            showToast('Error', err.message, 'error');
          }
        });
      });
    }
  } catch (err) {
    tableBody.innerHTML = `<tr><td colspan="7" style="text-align: center; color: var(--danger);">Failed to load requests.</td></tr>`;
  }
}

async function loadAdminLogs() {
  const tableBody = document.getElementById('admin-logs-tbody');
  if (!tableBody) return;

  try {
    const res = await apiRequest('/admin/logs');
    if (res.success && res.logs) {
      tableBody.innerHTML = res.logs.map(l => `
        <tr>
          <td>#${l.id}</td>
          <td><strong>${l.action}</strong></td>
          <td>${l.details}</td>
          <td><small class="text-muted">${l.created_at}</small></td>
        </tr>
      `).join('');
    }
  } catch (err) {
    tableBody.innerHTML = `<tr><td colspan="4" style="text-align: center; color: var(--danger);">Failed to load logs.</td></tr>`;
  }
}
