/**
 * API Client & Global UI Utility Module
 * Handles Fetch API requests, JWT/session headers, toast alerts,
 * and loading animations for the AI Blood Donor Finder.
 */

const API_BASE_URL = '/api';

/**
 * Shows modern, animated toast notifications.
 * @param {string} title - Heading text
 * @param {string} message - Informative body text
 * @param {'success'|'error'|'warning'|'info'} type - Alert severity
 * @param {number} duration - Milliseconds before auto-dismiss
 */
function showToast(title, message, type = 'info', duration = 4000) {
  let container = document.getElementById('toast-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toast-container';
    document.body.appendChild(container);
  }

  const icons = {
    success: '✓',
    error: '✕',
    warning: '⚠',
    info: 'ℹ'
  };

  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  toast.innerHTML = `
    <div class="toast-icon">${icons[type] || 'ℹ'}</div>
    <div class="toast-body">
      <div class="toast-title">${title}</div>
      <div class="toast-msg">${message}</div>
    </div>
    <button class="toast-close" aria-label="Close">&times;</button>
  `;

  const closeBtn = toast.querySelector('.toast-close');
  closeBtn.addEventListener('click', () => removeToast(toast));

  container.appendChild(toast);

  const timer = setTimeout(() => {
    removeToast(toast);
  }, duration);

  function removeToast(elem) {
    clearTimeout(timer);
    elem.style.animation = 'toast-out 0.25s forwards';
    setTimeout(() => {
      if (elem.parentNode) elem.parentNode.removeChild(elem);
    }, 250);
  }
}

/**
 * Toggles global loading overlay.
 */
function showLoading(message = 'Processing request...') {
  let overlay = document.getElementById('loading-overlay');
  if (!overlay) {
    overlay = document.createElement('div');
    overlay.id = 'loading-overlay';
    overlay.className = 'loading-overlay';
    overlay.innerHTML = `
      <div class="spinner spinner-primary" style="width: 48px; height: 48px; border-width: 4px;"></div>
      <div id="loading-overlay-text" style="font-weight: 700; font-size: 1.1rem;">${message}</div>
    `;
    document.body.appendChild(overlay);
  } else {
    document.getElementById('loading-overlay-text').textContent = message;
  }
  overlay.classList.add('active');
}

function hideLoading() {
  const overlay = document.getElementById('loading-overlay');
  if (overlay) overlay.classList.remove('active');
}

/**
 * Universal wrapper for Fetch API calls with automatic headers,
 * JSON serialization, and error trapping.
 */
async function apiRequest(endpoint, options = {}) {
  const url = `${API_BASE_URL}${endpoint}`;
  const token = localStorage.getItem('token');

  const headers = {
    'Content-Type': 'application/json',
    ...(options.headers || {})
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const config = {
    ...options,
    headers
  };

  if (config.body && typeof config.body === 'object') {
    config.body = JSON.stringify(config.body);
  }

  try {
    const response = await fetch(url, config);
    const data = await response.json().catch(() => ({}));

    if (!response.ok) {
      // If unauthorized, notify session expiration
      if (response.status === 401 && !url.includes('/auth/login')) {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        showToast('Session Expired', 'Please log in again to continue.', 'warning');
      }
      throw new Error(data.message || `Request failed with status ${response.status}`);
    }

    return data;
  } catch (error) {
    throw error;
  }
}

/**
 * Validates a name string: must be at least 2 chars and contain NO numbers.
 */
function isValidName(name) {
  if (!name || name.trim().length < 2) return false;
  return !/[0-9]/.test(name) && /^[a-zA-Z\s.'-]+$/.test(name.trim());
}

/**
 * Real-time Name Input Sanitizer & Live Feedback
 * Automatically prevents numbers and displays "No numbers allowed" warning.
 */
function setupNameValidation(inputElem) {
  if (!inputElem || inputElem.dataset.nameValidationAttached) return;
  inputElem.dataset.nameValidationAttached = 'true';

  // Find or create inline feedback element
  let feedback = inputElem.parentElement.querySelector('.name-no-numbers-feedback');
  if (!feedback) {
    feedback = document.createElement('div');
    feedback.className = 'name-no-numbers-feedback';
    feedback.style.display = 'none';
    feedback.style.color = '#dc2626';
    feedback.style.fontSize = '0.82rem';
    feedback.style.fontWeight = '700';
    feedback.style.marginTop = '6px';
    feedback.style.alignItems = 'center';
    feedback.style.gap = '6px';
    feedback.innerHTML = `<span style="font-size: 1rem;">⚠️</span> <span>Numbers are not allowed in name. Letters only.</span>`;
    inputElem.parentElement.appendChild(feedback);
  }

  let warningTimer = null;

  function triggerWarning() {
    feedback.style.display = 'flex';
    inputElem.style.borderColor = '#dc2626';
    inputElem.style.boxShadow = '0 0 0 3px rgba(220, 38, 38, 0.15)';

    if (warningTimer) clearTimeout(warningTimer);
    warningTimer = setTimeout(() => {
      feedback.style.display = 'none';
      inputElem.style.borderColor = '';
      inputElem.style.boxShadow = '';
    }, 3000);

    if (typeof showToast === 'function') {
      showToast('No Numbers Allowed', 'Names can only contain letters and spaces (numbers not allowed).', 'warning', 2500);
    }
  }

  // 1. Prevent typing numbers on keydown/keypress
  inputElem.addEventListener('keydown', (e) => {
    // If typing digits 0-9 (top row or numpad)
    if ((e.key >= '0' && e.key <= '9') && !e.ctrlKey && !e.metaKey && !e.altKey) {
      e.preventDefault();
      triggerWarning();
    }
  });

  // 2. Filter out numbers on input event (handles paste, drag-and-drop, mobile keyboards)
  inputElem.addEventListener('input', () => {
    if (/[0-9]/.test(inputElem.value)) {
      inputElem.value = inputElem.value.replace(/[0-9]/g, '');
      triggerWarning();
    }
  });
}

// Auto-attach to all name input fields across any page when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
  const nameSelectors = [
    '#reg-name',
    '#d-name',
    '#req-patient-name',
    '#prof-name',
    '#contact-name',
    'input[name="name"]',
    'input[name="patient_name"]',
    'input[id*="patient-name"]',
    'input[id*="donor-name"]'
  ];

  document.querySelectorAll(nameSelectors.join(',')).forEach(input => {
    setupNameValidation(input);
  });
});

