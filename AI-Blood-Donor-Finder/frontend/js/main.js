/**
 * Global Interactivity & Landing Page Controllers
 */

document.addEventListener('DOMContentLoaded', () => {
  // 1. Mobile Menu Toggle
  const mobileToggle = document.getElementById('mobile-toggle');
  const navLinks = document.getElementById('nav-links');

  if (mobileToggle && navLinks) {
    mobileToggle.addEventListener('click', () => {
      navLinks.classList.toggle('show');
    });
  }

  // 2. Load Real-Time Platform Statistics
  loadPlatformStats();

  // 3. Initialize Interactive Blood Compatibility Widget if present
  initCompatibilityWidget();
});

/**
 * Loads dynamic statistics from backend and updates stat counters.
 */
async function loadPlatformStats() {
  const statDonors = document.getElementById('stat-total-donors');
  const statMatches = document.getElementById('stat-matches');
  const statEmergencies = document.getElementById('stat-emergencies');
  const statRequests = document.getElementById('stat-requests');

  // If page doesn't have stat elements, skip
  if (!statDonors && !statMatches) return;

  try {
    const data = await apiRequest('/requests/stats');
    if (data.success && data.stats) {
      if (statDonors) animateValue(statDonors, 0, data.stats.total_donors, 1000);
      if (statMatches) animateValue(statMatches, 0, data.stats.successful_matches || 12, 1000);
      if (statEmergencies) animateValue(statEmergencies, 0, data.stats.active_emergencies, 1000);
      if (statRequests) animateValue(statRequests, 0, data.stats.total_requests, 1000);
    }
  } catch (err) {
    console.warn('Could not fetch real-time statistics:', err);
  }
}

/**
 * Smooth counter animation for numbers.
 */
function animateValue(obj, start, end, duration) {
  if (!obj) return;
  if (start === end) {
    obj.textContent = end;
    return;
  }
  let startTimestamp = null;
  const step = (timestamp) => {
    if (!startTimestamp) startTimestamp = timestamp;
    const progress = Math.min((timestamp - startTimestamp) / duration, 1);
    obj.textContent = Math.floor(progress * (end - start) + start);
    if (progress < 1) {
      window.requestAnimationFrame(step);
    } else {
      obj.textContent = end;
    }
  };
  window.requestAnimationFrame(step);
}

/**
 * Interactive Blood Compatibility Widget
 */
async function initCompatibilityWidget() {
  const pillsContainer = document.getElementById('compat-pills');
  if (!pillsContainer) return;

  const receiveBox = document.getElementById('compat-receive-list');
  const donateBox = document.getElementById('compat-donate-list');
  const typeTitle = document.getElementById('compat-type-title');
  const noteBox = document.getElementById('compat-note');

  const bloodGroups = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'];
  let currentGroup = 'O-';

  // Render pills
  pillsContainer.innerHTML = '';
  bloodGroups.forEach((bg) => {
    const pill = document.createElement('button');
    pill.className = `blood-btn-pill ${bg === currentGroup ? 'active' : ''}`;
    pill.textContent = bg;
    pill.addEventListener('click', () => {
      pillsContainer.querySelectorAll('.blood-btn-pill').forEach(p => p.classList.remove('active'));
      pill.classList.add('active');
      currentGroup = bg;
      fetchCompatibility(bg);
    });
    pillsContainer.appendChild(pill);
  });

  async function fetchCompatibility(bg) {
    try {
      const data = await apiRequest(`/search/compatibility/${encodeURIComponent(bg)}`);
      if (data.success) {
        if (typeTitle) typeTitle.textContent = `Blood Group: ${data.blood_group}`;
        
        // Receive list
        if (receiveBox) {
          receiveBox.innerHTML = data.can_receive_from
            .map(g => `<span class="compat-tag can-receive">✓ ${g}</span>`)
            .join(' ');
        }

        // Donate list
        if (donateBox) {
          donateBox.innerHTML = data.can_donate_to
            .map(g => `<span class="compat-tag can-donate">➔ ${g}</span>`)
            .join(' ');
        }

        // Special notes
        if (noteBox) {
          if (data.is_universal_donor) {
            noteBox.innerHTML = `⭐ <strong>Universal Donor:</strong> O- blood can be administered to ANY emergency patient safely.`;
          } else if (data.is_universal_recipient) {
            noteBox.innerHTML = `🌟 <strong>Universal Recipient:</strong> AB+ individuals can receive red blood cells from all 8 blood types.`;
          } else {
            noteBox.innerHTML = `Standard red blood cell antigen compatibility rules applied.`;
          }
        }
      }
    } catch (err) {
      console.error('Error fetching compatibility:', err);
    }
  }

  // Load initial
  fetchCompatibility(currentGroup);
}
