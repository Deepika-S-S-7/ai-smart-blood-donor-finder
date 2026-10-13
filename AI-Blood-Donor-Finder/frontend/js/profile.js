/**
 * User & Donor Profile Controller
 */

document.addEventListener('DOMContentLoaded', () => {
  initProfilePage();
});

async function initProfilePage() {
  const profilePage = document.getElementById('profile-page');
  if (!profilePage) return;

  if (!requireAuth()) return;

  await loadProfileData();
  setupProfileForm();
  setupDonationDateForm();
  setupPasswordForm();
}

async function loadProfileData() {
  try {
    const res = await apiRequest('/auth/me');
    if (res.success && res.user) {
      const u = res.user;
      
      // Fill header badge
      const nameHeader = document.getElementById('profile-header-name');
      const emailHeader = document.getElementById('profile-header-email');
      const roleHeader = document.getElementById('profile-header-role');
      if (nameHeader) nameHeader.textContent = u.name;
      if (emailHeader) emailHeader.textContent = u.email;
      if (roleHeader) roleHeader.textContent = u.role.toUpperCase();

      // Form values
      const nameInput = document.getElementById('prof-name');
      const emailInput = document.getElementById('prof-email');
      const phoneInput = document.getElementById('prof-phone');
      const cityInput = document.getElementById('prof-city');
      const areaInput = document.getElementById('prof-area');

      if (nameInput) nameInput.value = u.name || '';
      if (emailInput) emailInput.value = u.email || '';
      if (phoneInput) phoneInput.value = u.phone || '';
      if (cityInput) cityInput.value = u.city || '';
      if (areaInput) areaInput.value = u.area || '';

      // Donor-specific fields
      const donorSection = document.getElementById('donor-profile-section');
      if (u.role === 'donor' && u.donor_profile) {
        if (donorSection) donorSection.style.display = 'block';
        const dp = u.donor_profile;

        const ageInput = document.getElementById('prof-age');
        const addressInput = document.getElementById('prof-address');
        const bgDisplay = document.getElementById('prof-blood-group');
        const totalDisplay = document.getElementById('prof-total-donations');
        const lastDateInput = document.getElementById('prof-last-date');

        if (ageInput) ageInput.value = dp.age || '';
        if (addressInput) addressInput.value = dp.address || '';
        if (bgDisplay) bgDisplay.textContent = dp.blood_group || '';
        if (totalDisplay) totalDisplay.textContent = dp.total_donations || 0;
        if (lastDateInput && dp.last_donation_date) lastDateInput.value = dp.last_donation_date.slice(0, 10);
      } else {
        if (donorSection) donorSection.style.display = 'none';
      }
    }
  } catch (err) {
    showToast('Error', 'Failed to load profile data', 'error');
  }
}

function setupProfileForm() {
  const form = document.getElementById('profile-details-form');
  if (!form) return;

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const { user } = getSession();

    const name = document.getElementById('prof-name')?.value?.trim();
    const phone = document.getElementById('prof-phone')?.value?.trim();
    const city = document.getElementById('prof-city')?.value?.trim();
    const area = document.getElementById('prof-area')?.value?.trim();
    const age = document.getElementById('prof-age')?.value;

    if (!name || !isValidName(name)) {
      showToast('Invalid Name', 'Numbers are not allowed in name. Please use letters only.', 'warning');
      document.getElementById('prof-name')?.focus();
      return;
    }

    showLoading('Updating profile information...');

    try {
      const payload = {
        name,
        phone,
        city,
        area,
        address,
        age: age ? parseInt(age, 10) : 25
      };

      const endpoint = user.role === 'donor' ? '/donors/profile' : '/auth/me';
      const res = await apiRequest('/donors/profile', {
        method: 'PUT',
        body: payload
      });

      hideLoading();
      showToast('Profile Updated', res.message || 'Details saved successfully.', 'success');

      // Update local storage user name
      user.name = name;
      localStorage.setItem('user', JSON.stringify(user));
      updateNavAuthUI();
    } catch (err) {
      hideLoading();
      showToast('Update Failed', err.message || 'Could not update profile', 'error');
    }
  });
}

function setupDonationDateForm() {
  const form = document.getElementById('donation-date-form');
  if (!form) return;

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const dateVal = document.getElementById('prof-last-date')?.value;
    if (!dateVal) return showToast('Date Required', 'Please select a donation date', 'warning');

    showLoading('Recording blood donation...');

    try {
      const res = await apiRequest('/donors/donation-date', {
        method: 'PUT',
        body: { last_donation_date: dateVal }
      });
      hideLoading();
      showToast('Donation Recorded', res.message || 'Thank you for donating!', 'success');
      loadProfileData();
    } catch (err) {
      hideLoading();
      showToast('Error', err.message || 'Could not update date', 'error');
    }
  });
}

function setupPasswordForm() {
  const form = document.getElementById('change-password-form');
  if (!form) return;

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const oldPassword = document.getElementById('pwd-old')?.value;
    const newPassword = document.getElementById('pwd-new')?.value;
    const confirmPassword = document.getElementById('pwd-confirm')?.value;

    if (!oldPassword || !newPassword) {
      return showToast('Fields Required', 'Please fill in all password fields.', 'warning');
    }

    if (newPassword !== confirmPassword) {
      return showToast('Mismatch', 'New passwords do not match.', 'error');
    }

    showLoading('Updating security credentials...');

    try {
      const res = await apiRequest('/auth/change-password', {
        method: 'PUT',
        body: {
          old_password: oldPassword,
          new_password: newPassword
        }
      });
      hideLoading();
      form.reset();
      showToast('Password Changed', res.message || 'Password updated successfully.', 'success');
    } catch (err) {
      hideLoading();
      showToast('Error', err.message || 'Could not change password', 'error');
    }
  });
}
