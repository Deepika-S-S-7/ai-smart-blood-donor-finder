/**
 * Intelligent Donor Search Controller
 */

let currentSearchResults = [];
let selectedDonorForRequest = null;

document.addEventListener('DOMContentLoaded', () => {
  initSearchPage();
});

async function initSearchPage() {
  await loadLocations();
  setupSearchForm();
  setupSortHandler();
  setupRequestModal();

  // Check URL parameters for pre-filled search
  const urlParams = new URLSearchParams(window.location.search);
  const bg = urlParams.get('blood_group');
  const city = urlParams.get('city');

  if (bg) {
    const bgSelect = document.getElementById('search-blood-group');
    if (bgSelect) bgSelect.value = bg;
  }
  if (city) {
    const cityInput = document.getElementById('search-city');
    if (cityInput) cityInput.value = city;
  }

  if (bg) {
    performSearch();
  }
}

/**
 * Loads distinct cities and areas for autocompletion
 */
async function loadLocations() {
  try {
    const data = await apiRequest('/search/locations');
    if (data.success) {
      const cityListElem = document.getElementById('city-datalist');
      if (cityListElem && data.cities) {
        cityListElem.innerHTML = data.cities.map(c => `<option value="${c}">`).join('');
      }
    }
  } catch (err) {
    console.warn('Could not load locations:', err);
  }
}

/**
 * Form submit listener
 */
function setupSearchForm() {
  const form = document.getElementById('donor-search-form');
  if (!form) return;

  form.addEventListener('submit', (e) => {
    e.preventDefault();
    performSearch();
  });
}

/**
 * Performs intelligent donor search via Flask REST API
 */
async function performSearch() {
  const bg = document.getElementById('search-blood-group')?.value;
  const city = document.getElementById('search-city')?.value?.trim();
  const area = document.getElementById('search-area')?.value?.trim();
  const availability = document.getElementById('search-avail')?.value || 'Available';
  const sortBy = document.getElementById('sort-by')?.value || 'score';

  if (!bg) {
    showToast('Selection Required', 'Please select a recipient blood group.', 'warning');
    return;
  }

  showLoading('Analyzing compatible donors & computing match scores...');
  const searchBtn = document.getElementById('search-submit-btn');
  if (searchBtn) searchBtn.disabled = true;

  try {
    const payload = {
      blood_group: bg,
      city: city || null,
      area: area || null,
      availability: availability,
      sort_by: sortBy
    };

    const data = await apiRequest('/search/donors', {
      method: 'POST',
      body: payload
    });

    hideLoading();
    if (searchBtn) searchBtn.disabled = false;

    if (data.success) {
      currentSearchResults = data.results || [];
      renderSearchResults(data);
    } else {
      showToast('Search Notice', data.message || 'No donors found.', 'info');
      renderEmptyState();
    }
  } catch (error) {
    hideLoading();
    if (searchBtn) searchBtn.disabled = false;
    showToast('Search Failed', error.message || 'Unable to connect to server.', 'error');
    renderEmptyState();
  }
}

/**
 * Renders ranked donor cards into DOM
 */
function renderSearchResults(searchResponse) {
  const container = document.getElementById('donor-results-grid');
  const countElem = document.getElementById('results-count-text');
  const criteriaElem = document.getElementById('criteria-banner');

  if (!container) return;

  const results = searchResponse.results || [];
  const criteria = searchResponse.search_criteria || {};
  const compGroups = searchResponse.compatible_donor_groups || [];

  if (countElem) {
    countElem.textContent = `${results.length} Compatible Donor(s) Found`;
  }

  if (criteriaElem) {
    criteriaElem.innerHTML = `
      <div style="background: #fff; padding: 14px 20px; border-radius: var(--radius-md); border: 1px solid var(--border); margin-bottom: 24px; font-size: 0.9rem;">
        <strong>Recipient Blood Group:</strong> <span style="color: var(--primary); font-weight: 800;">${criteria.recipient_blood_group}</span> &nbsp;|&nbsp; 
        <strong>Compatible RBC Donors:</strong> ${compGroups.map(g => `<span class="compat-tag can-receive" style="padding: 2px 8px; font-size: 0.8rem;">${g}</span>`).join(' ')} &nbsp;|&nbsp;
        <strong>Location Filter:</strong> ${criteria.city || 'Any City'}${criteria.area ? ' (' + criteria.area + ')' : ''}
      </div>
    `;
  }

  if (results.length === 0) {
    renderEmptyState();
    return;
  }

  container.innerHTML = results.map(donor => {
    const isOptimal = donor.match_score >= 85;
    const isAvail = donor.availability === 'Available';
    const b = donor.score_breakdown || {};

    return `
      <div class="donor-card ${isOptimal ? 'optimal-match' : ''}">
        <div>
          <div class="donor-card-top">
            <div class="donor-identity">
              <div class="donor-blood-badge">${donor.blood_group}</div>
              <div class="donor-name-box">
                <h3>${donor.name}</h3>
                <span>${donor.gender}, ${donor.age} yrs</span>
              </div>
            </div>
            <div class="match-score-badge">
              <div class="match-score-pill ${isOptimal ? 'optimal' : ''}">
                ${donor.match_score}%
              </div>
              <span class="match-score-label">Match Score</span>
            </div>
          </div>

          <div class="donor-info-list">
            <div class="donor-info-row">
              <span>📍</span>
              <span><strong>${donor.city}</strong>, ${donor.area}</span>
            </div>
            <div class="donor-info-row">
              <span>⏱</span>
              <span>${donor.last_donation_date ? 'Last donated: ' + donor.last_donation_date : 'First-time donor (Fully Eligible)'}</span>
            </div>
            <div class="donor-info-row">
              <span>🩸</span>
              <span>Compatibility: <strong>${donor.compatibility_type}</strong></span>
            </div>
            <div class="donor-info-row">
              <span>🩺</span>
              <span>Status: <strong style="color: ${isAvail ? 'var(--success)' : 'var(--warning)'};">${donor.availability}</strong></span>
            </div>
          </div>

          <div class="score-breakdown-bar">
            <div class="breakdown-row">
              <span>Compatibility (${b.compatibility?.score || 0}/50)</span>
              <span style="color: var(--text-muted); font-size: 0.75rem;">${b.compatibility?.detail || ''}</span>
            </div>
            <div class="breakdown-row">
              <span>Location (${b.location?.score || 0}/25)</span>
              <span style="color: var(--text-muted); font-size: 0.75rem;">${b.location?.detail || ''}</span>
            </div>
            <div class="breakdown-row">
              <span>Availability (${b.availability?.score || 0}/15)</span>
              <span style="color: var(--text-muted); font-size: 0.75rem;">${b.availability?.detail || ''}</span>
            </div>
            <div class="breakdown-row">
              <span>Recency (${b.recency?.score || 0}/10)</span>
              <span style="color: var(--text-muted); font-size: 0.75rem;">${b.recency?.detail || ''}</span>
            </div>
          </div>
        </div>

        <button class="btn btn-primary btn-sm open-request-btn" data-donor-id="${donor.donor_id}" data-donor-name="${donor.name}" data-score="${donor.match_score}" style="width: 100%; margin-top: 12px;">
          Send Blood Request
        </button>
      </div>
    `;
  }).join('');

  // Attach button events
  container.querySelectorAll('.open-request-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
      const donorId = btn.getAttribute('data-donor-id');
      const donorName = btn.getAttribute('data-donor-name');
      const score = btn.getAttribute('data-score');
      openRequestModal(donorId, donorName, score);
    });
  });
}

function renderEmptyState() {
  const container = document.getElementById('donor-results-grid');
  const countElem = document.getElementById('results-count-text');
  if (countElem) countElem.textContent = '0 Donors Found';
  if (!container) return;

  container.innerHTML = `
    <div class="empty-state-box" style="grid-column: 1 / -1;">
      <div class="empty-state-icon">🔍</div>
      <h3>No Compatible Donors Found</h3>
      <p>We couldn't find available compatible donors for this location and blood group criteria.</p>
      <div style="display: flex; gap: 12px; justify-content: center;">
        <button class="btn btn-outline" onclick="document.getElementById('search-city').value=''; performSearch();">
          Search All Cities
        </button>
        <a href="/emergency-request.html" class="btn btn-emergency">
          Create Emergency Request
        </a>
      </div>
    </div>
  `;
}

function setupSortHandler() {
  const sortSelect = document.getElementById('sort-by');
  if (sortSelect) {
    sortSelect.addEventListener('change', () => {
      performSearch();
    });
  }
}

/**
 * Modal to send request to a specific donor
 */
function setupRequestModal() {
  const modal = document.getElementById('donor-request-modal');
  const closeBtn = document.getElementById('modal-close-btn');
  const form = document.getElementById('send-donor-request-form');

  if (closeBtn) {
    closeBtn.addEventListener('click', () => {
      modal.classList.remove('active');
    });
  }

  if (form) {
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      const { token, user } = getSession();
      if (!token || !user) {
        showToast('Login Required', 'Please log in to send a blood request to this donor.', 'warning');
        setTimeout(() => { window.location.href = '/login.html'; }, 800);
        return;
      }

      const notes = document.getElementById('request-notes')?.value || 'Blood requirement request.';
      showLoading('Dispatching request to donor...');

      try {
        const payload = {
          donor_id: selectedDonorForRequest.id,
          match_score: selectedDonorForRequest.score,
          notes: notes
        };

        const res = await apiRequest('/donor-requests', {
          method: 'POST',
          body: payload
        });

        hideLoading();
        modal.classList.remove('active');
        showToast('Request Sent', res.message || 'The donor has been notified!', 'success');
      } catch (err) {
        hideLoading();
        showToast('Request Failed', err.message || 'Unable to send request.', 'error');
      }
    });
  }
}

function openRequestModal(donorId, donorName, score) {
  const modal = document.getElementById('donor-request-modal');
  const nameSpan = document.getElementById('modal-donor-name');
  selectedDonorForRequest = { id: donorId, name: donorName, score: score };

  if (nameSpan) nameSpan.textContent = donorName;
  if (modal) modal.classList.add('active');
}
