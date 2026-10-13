/**
 * Authentication & Session Management Module
 */

function saveSession(token, user) {
  localStorage.setItem('token', token);
  localStorage.setItem('user', JSON.stringify(user));
}

function getSession() {
  const token = localStorage.getItem('token');
  const userStr = localStorage.getItem('user');
  let user = null;
  if (userStr) {
    try {
      user = JSON.parse(userStr);
    } catch (e) {
      user = null;
    }
  }
  return { token, user };
}

function clearSession() {
  localStorage.removeItem('token');
  localStorage.removeItem('user');
}

function handleLogout() {
  apiRequest('/auth/logout', { method: 'POST' }).catch(() => {});
  clearSession();
  showToast('Logged Out', 'You have been signed out successfully.', 'info');
  setTimeout(() => {
    window.location.href = '/login.html';
  }, 500);
}

/**
 * Route protection guard
 */
function requireAuth(allowedRoles = null) {
  const { token, user } = getSession();
  if (!token || !user) {
    showToast('Login Required', 'Please sign in to access this page.', 'warning');
    setTimeout(() => {
      window.location.href = `/login.html?redirect=${encodeURIComponent(window.location.pathname)}`;
    }, 600);
    return false;
  }

  if (allowedRoles) {
    const roles = Array.isArray(allowedRoles) ? allowedRoles : [allowedRoles];
    if (!roles.includes(user.role)) {
      showToast('Access Denied', 'You do not have permission to view this page.', 'error');
      setTimeout(() => {
        window.location.href = user.role === 'admin' ? '/admin.html' : '/dashboard.html';
      }, 800);
      return false;
    }
  }
  return true;
}

/**
 * Dynamically updates header navigation bar based on auth state
 */
function updateNavAuthUI() {
  const { token, user } = getSession();
  const navActions = document.getElementById('nav-actions');
  const navLinks = document.getElementById('nav-links');

  if (!navActions) return;

  if (token && user) {
    // Determine portal link
    let portalLink = '/dashboard.html';
    let portalName = 'Dashboard';
    if (user.role === 'admin') {
      portalLink = '/admin.html';
      portalName = 'Admin Portal';
    }

    navActions.innerHTML = `
      <div class="user-menu-wrap">
        <a href="${portalLink}" class="user-badge" title="Go to ${portalName}">
          <span>👤</span> ${user.name.split(' ')[0]} (${user.role.toUpperCase()})
        </a>
        <button id="logout-btn" class="btn btn-outline btn-sm">Sign Out</button>
      </div>
    `;

    document.getElementById('logout-btn')?.addEventListener('click', handleLogout);

    // If nav-links element exists, ensure Dashboard and My Requests are available
    if (navLinks && !document.getElementById('nav-dyn-dash')) {
      const dashItem = document.createElement('li');
      dashItem.id = 'nav-dyn-dash';
      dashItem.innerHTML = `<a href="${portalLink}" class="nav-link">${portalName}</a>`;
      navLinks.appendChild(dashItem);

      if (user.role !== 'admin') {
        const reqItem = document.createElement('li');
        reqItem.id = 'nav-dyn-reqs';
        reqItem.innerHTML = `<a href="/my-requests.html" class="nav-link">My Requests</a>`;
        navLinks.appendChild(reqItem);
      }
    }
  } else {
    navActions.innerHTML = `
      <a href="/login.html" class="btn btn-outline btn-sm">Sign In</a>
      <a href="/register.html" class="btn btn-primary btn-sm">Get Started</a>
    `;
  }
}

// Auto-run nav UI updater on DOMContentLoaded
document.addEventListener('DOMContentLoaded', () => {
  updateNavAuthUI();
});
