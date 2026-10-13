/**
 * Blood Request & Emergency Flow Controller
 */

document.addEventListener('DOMContentLoaded', () => {
  initEmergencyRequestForm();
  initMyRequestsPage();
});

/**
 * Emergency Blood Request Form Handler
 */
function initEmergencyRequestForm() {
  const form = document.getElementById('emergency-request-form');
  if (!form) return;

  // Set default required date to today
  const dateInput = document.getElementById('req-date');
  if (dateInput) {
    const today = new Date().toISOString().split('T')[0];
    dateInput.value = today;
    dateInput.min = today;
  }

  form.addEventListener('submit', async (e) => {
    e.preventDefault();

    const patientName = document.getElementById('req-patient-name')?.value?.trim();
    const bloodGroup = document.getElementById('req-blood-group')?.value;
    const hospitalName = document.getElementById('req-hospital-name')?.value?.trim();
    const hospitalLocation = document.getElementById('req-hospital-loc')?.value?.trim();
    const city = document.getElementById('req-city')?.value?.trim();
    const area = document.getElementById('req-area')?.value?.trim();
    const contactNumber = document.getElementById('req-contact')?.value?.trim();
    const units = parseInt(document.getElementById('req-units')?.value || '1', 10);
    const urgency = document.getElementById('req-urgency')?.value || 'Emergency';
    const requiredDate = document.getElementById('req-date')?.value;
    const additionalInfo = document.getElementById('req-info')?.value?.trim();

    // Validations
    if (!patientName || !isValidName(patientName)) {
      showToast('Invalid Patient Name', 'Numbers are not allowed in patient name. Please use letters only.', 'warning');
      document.getElementById('req-patient-name')?.focus();
      return;
    }
    if (!bloodGroup) return showToast('Field Required', 'Please select blood group.', 'warning');
    if (!hospitalName) return showToast('Field Required', 'Please specify hospital name.', 'warning');
    if (!city || !area) return showToast('Field Required', 'Please provide city and area.', 'warning');
    if (!contactNumber || contactNumber.length < 10) return showToast('Field Required', 'Please provide a valid 10-digit contact number.', 'warning');

    showLoading('Submitting blood requirement & matching nearby donors...');

    try {
      const payload = {
        patient_name: patientName,
        blood_group: bloodGroup,
        hospital_name: hospitalName,
        hospital_location: hospitalLocation,
        city: city,
        area: area,
        contact_number: contactNumber,
        required_units: units,
        urgency: urgency,
        required_date: requiredDate,
        additional_information: additionalInfo
      };

      const res = await apiRequest('/requests', {
        method: 'POST',
        body: payload
      });

      hideLoading();

      if (res.success) {
        showSuccessModal(res);
      } else {
        showToast('Submission Failed', res.message || 'Error creating request', 'error');
      }
    } catch (err) {
      hideLoading();
      showToast('Error', err.message || 'Unable to submit request.', 'error');
    }
  });
}

function showSuccessModal(response) {
  const modal = document.getElementById('emergency-success-modal');
  if (!modal) return;

  const idSpan = document.getElementById('success-req-id');
  const countSpan = document.getElementById('success-match-count');
  const searchBtn = document.getElementById('btn-view-matches');

  if (idSpan) idSpan.textContent = response.request_id;
  if (countSpan) countSpan.textContent = response.matching_donors_count || 0;

  if (searchBtn && response.data) {
    searchBtn.href = `/search.html?blood_group=${encodeURIComponent(response.data.blood_group)}&city=${encodeURIComponent(response.data.city)}`;
  }

  modal.classList.add('active');
}

/**
 * My Requests Page Handler (Dual Tabs: Seeker Outgoing vs Donor Incoming)
 */
async function initMyRequestsPage() {
  const container = document.getElementById('my-requests-page');
  if (!container) return;

  if (!requireAuth()) return;

  const { user } = getSession();
  const isDonor = user && user.role === 'donor';

  // If user is donor, show incoming requests tab
  const incomingTabBtn = document.getElementById('tab-incoming-btn');
  if (incomingTabBtn) {
    incomingTabBtn.style.display = isDonor ? 'block' : 'none';
  }

  setupTabs();
  loadSeekerRequests();
  if (isDonor) {
    loadIncomingDonorRequests();
  }
}

function setupTabs() {
  const tabSeeker = document.getElementById('tab-seeker-btn');
  const tabIncoming = document.getElementById('tab-incoming-btn');
  const viewSeeker = document.getElementById('view-seeker-requests');
  const viewIncoming = document.getElementById('view-incoming-requests');

  if (tabSeeker && tabIncoming) {
    tabSeeker.addEventListener('click', () => {
      tabSeeker.classList.add('active');
      tabIncoming.classList.remove('active');
      if (viewSeeker) viewSeeker.style.display = 'block';
      if (viewIncoming) viewIncoming.style.display = 'none';
    });

    tabIncoming.addEventListener('click', () => {
      tabIncoming.classList.add('active');
      tabSeeker.classList.remove('active');
      if (viewSeeker) viewSeeker.style.display = 'none';
      if (viewIncoming) viewIncoming.style.display = 'block';
    });
  }
}

/**
 * Loads requests sent by current seeker
 */
async function loadSeekerRequests() {
  const tableBody = document.getElementById('seeker-requests-tbody');
  if (!tableBody) return;

  try {
    const res = await apiRequest('/donor-requests/my-requests');
    if (res.success && res.requests && res.requests.length > 0) {
      tableBody.innerHTML = res.requests.map(r => `
        <tr>
          <td><strong>${r.request_id || 'DIRECT'}</strong></td>
          <td>${r.donor_name} <br><small class="text-muted">${r.donor_blood_group} | ${r.donor_city}</small></td>
          <td>${r.patient_name || 'Direct Request'}</td>
          <td>${r.hospital_name || 'N/A'}</td>
          <td>${r.match_score}%</td>
          <td><span class="badge-status ${r.status.toLowerCase()}">${r.status}</span></td>
          <td><small class="text-muted">${r.created_at ? r.created_at.slice(0, 10) : ''}</small></td>
        </tr>
      `).join('');
    } else {
      tableBody.innerHTML = `<tr><td colspan="7" style="text-align: center; color: var(--text-muted); padding: 32px;">No sent blood requests found. Use Search to find compatible donors.</td></tr>`;
    }
  } catch (err) {
    tableBody.innerHTML = `<tr><td colspan="7" style="text-align: center; color: var(--danger); padding: 24px;">Failed to load requests: ${err.message}</td></tr>`;
  }
}

/**
 * Loads requests received by the logged-in donor
 */
async function loadIncomingDonorRequests() {
  const tableBody = document.getElementById('incoming-requests-tbody');
  if (!tableBody) return;

  try {
    const res = await apiRequest('/donor-requests/incoming');
    if (res.success && res.incoming_requests && res.incoming_requests.length > 0) {
      tableBody.innerHTML = res.incoming_requests.map(r => `
        <tr>
          <td><strong>#${r.id}</strong></td>
          <td>
            <strong>${r.requester_name}</strong><br>
            <small class="text-muted">📞 ${r.requester_phone}</small>
          </td>
          <td>
            <strong>${r.patient_name || 'Urgent Patient'}</strong><br>
            <small class="text-muted">${r.hospital_name}, ${r.city}</small>
          </td>
          <td><span class="badge-status ${r.urgency ? r.urgency.toLowerCase() : 'normal'}">${r.urgency || 'Normal'}</span></td>
          <td><span class="badge-status ${r.status.toLowerCase()}">${r.status}</span></td>
          <td>
            ${r.status === 'Pending' ? `
              <div style="display: flex; gap: 8px;">
                <button class="btn btn-primary btn-sm accept-btn" data-id="${r.id}">Accept</button>
                <button class="btn btn-outline btn-sm reject-btn" data-id="${r.id}" style="border-color: var(--danger); color: var(--danger);">Decline</button>
              </div>
            ` : `<small class="text-muted">Action taken (${r.status})</small>`}
          </td>
        </tr>
      `).join('');

      // Wire up Accept/Reject
      tableBody.querySelectorAll('.accept-btn').forEach(btn => {
        btn.addEventListener('click', () => updateIncomingStatus(btn.getAttribute('data-id'), 'Accepted'));
      });
      tableBody.querySelectorAll('.reject-btn').forEach(btn => {
        btn.addEventListener('click', () => updateIncomingStatus(btn.getAttribute('data-id'), 'Rejected'));
      });

    } else {
      tableBody.innerHTML = `<tr><td colspan="6" style="text-align: center; color: var(--text-muted); padding: 32px;">No incoming blood requests at the moment.</td></tr>`;
    }
  } catch (err) {
    tableBody.innerHTML = `<tr><td colspan="6" style="text-align: center; color: var(--danger); padding: 24px;">Failed to load incoming requests.</td></tr>`;
  }
}

async function updateIncomingStatus(requestId, newStatus) {
  showLoading(`Marking request as ${newStatus}...`);
  try {
    const res = await apiRequest(`/donor-requests/${requestId}/status`, {
      method: 'PUT',
      body: { status: newStatus }
    });
    hideLoading();
    showToast('Updated', res.message || `Request ${newStatus}`, 'success');
    loadIncomingDonorRequests();
  } catch (err) {
    hideLoading();
    showToast('Update Failed', err.message || 'Could not update status', 'error');
  }
}
