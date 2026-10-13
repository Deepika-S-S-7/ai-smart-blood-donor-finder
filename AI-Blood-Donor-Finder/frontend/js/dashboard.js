/**
 * User & Donor Dashboard Controller
 */

document.addEventListener('DOMContentLoaded', () => {
  initDashboard();
});

async function initDashboard() {
  const dashPage = document.getElementById('dashboard-page');
  if (!dashPage) return;

  if (!requireAuth()) return;

  const { user } = getSession();
  renderUserGreeting(user);
  await loadDashboardMetrics(user);
  setupAvailabilityToggle(user);
  setupQuickSearch();
  loadRecentActivity(user);
}

function renderUserGreeting(user) {
  const nameElem = document.getElementById('dash-user-name');
  const roleElem = document.getElementById('dash-user-role');
  const donorBox = document.getElementById('dash-donor-meta-box');

  if (nameElem) nameElem.textContent = user.name;
  if (roleElem) roleElem.textContent = user.role === 'donor' ? 'Registered Life Saver (Donor)' : 'Blood Seeker / Patient Account';

  if (donorBox) {
    if (user.role === 'donor') {
      donorBox.style.display = 'flex';
      const bgBadge = document.getElementById('dash-donor-bg');
      const lastDate = document.getElementById('dash-donor-last-date');
      if (bgBadge && user.blood_group) bgBadge.textContent = user.blood_group;
      if (lastDate) lastDate.textContent = user.last_donation_date || 'None recorded (Eligible)';
    } else {
      donorBox.style.display = 'none';
    }
  }
}

async function loadDashboardMetrics(user) {
  try {
    const data = await apiRequest('/requests/stats');
    if (data.success && data.stats) {
      const s = data.stats;
      const m1 = document.getElementById('dash-metric-donors');
      const m2 = document.getElementById('dash-metric-emergencies');
      const m3 = document.getElementById('dash-metric-matches');
      const m4 = document.getElementById('dash-metric-requests');

      if (m1) m1.textContent = s.total_donors;
      if (m2) m2.textContent = s.active_emergencies;
      if (m3) m3.textContent = s.successful_matches || 12;
      if (m4) m4.textContent = s.total_requests;
    }
  } catch (err) {
    console.warn('Could not load dashboard metrics:', err);
  }
}

function setupAvailabilityToggle(user) {
  const toggle = document.getElementById('dash-avail-switch');
  const statusLabel = document.getElementById('dash-avail-label');
  const dot = document.getElementById('dash-status-dot');

  if (!toggle) return;

  if (user.role !== 'donor') {
    const parent = document.getElementById('dash-avail-container');
    if (parent) parent.style.display = 'none';
    return;
  }

  const isAvailable = (user.availability === 'Available');
  toggle.checked = isAvailable;
  updateStatusView(isAvailable);

  toggle.addEventListener('change', async () => {
    const newStatus = toggle.checked ? 'Available' : 'Temporarily Unavailable';
    updateStatusView(toggle.checked);

    try {
      const res = await apiRequest('/donors/availability', {
        method: 'PUT',
        body: { availability: newStatus }
      });
      if (res.success) {
        showToast('Status Updated', `Your donor status is now: ${newStatus}`, 'success');
        user.availability = newStatus;
        localStorage.setItem('user', JSON.stringify(user));
      }
    } catch (err) {
      toggle.checked = !toggle.checked;
      updateStatusView(toggle.checked);
      showToast('Error', err.message || 'Failed to update availability', 'error');
    }
  });

  function updateStatusView(available) {
    if (statusLabel) statusLabel.textContent = available ? 'Available to Donate' : 'Temporarily Unavailable';
    if (dot) {
      dot.className = `status-dot ${available ? 'available' : 'unavailable'}`;
    }
  }
}

function setupQuickSearch() {
  const form = document.getElementById('dash-quick-search-form');
  if (!form) return;

  form.addEventListener('submit', (e) => {
    e.preventDefault();
    const bg = document.getElementById('dash-quick-bg')?.value;
    const city = document.getElementById('dash-quick-city')?.value?.trim();
    if (!bg) {
      showToast('Selection Required', 'Please select a blood group.', 'warning');
      return;
    }
    let targetUrl = `/search.html?blood_group=${encodeURIComponent(bg)}`;
    if (city) targetUrl += `&city=${encodeURIComponent(city)}`;
    window.location.href = targetUrl;
  });
}

async function loadRecentActivity(user) {
  const tableBody = document.getElementById('dash-activity-tbody');
  if (!tableBody) return;

  try {
    const res = await apiRequest('/requests?limit=5');
    if (res.success && res.requests && res.requests.length > 0) {
      tableBody.innerHTML = res.requests.slice(0, 5).map(r => `
        <tr>
          <td><strong>${r.request_id}</strong></td>
          <td><span class="compat-tag can-receive" style="padding: 2px 8px; font-size: 0.85rem;">${r.blood_group}</span></td>
          <td>${r.patient_name} <br><small class="text-muted">${r.hospital_name}, ${r.city}</small></td>
          <td><span class="badge-status ${r.urgency.toLowerCase()}">${r.urgency}</span></td>
          <td><span class="badge-status ${r.status.toLowerCase()}">${r.status}</span></td>
          <td>
            <a href="/search.html?blood_group=${encodeURIComponent(r.blood_group)}&city=${encodeURIComponent(r.city)}" class="btn btn-outline btn-sm">Find Matches</a>
          </td>
        </tr>
      `).join('');
    } else {
      tableBody.innerHTML = `<tr><td colspan="6" style="text-align: center; color: var(--text-muted); padding: 24px;">No active blood requests found.</td></tr>`;
    }
  } catch (err) {
    tableBody.innerHTML = `<tr><td colspan="6" style="text-align: center; color: var(--danger); padding: 24px;">Failed to load activity.</td></tr>`;
  }
}
