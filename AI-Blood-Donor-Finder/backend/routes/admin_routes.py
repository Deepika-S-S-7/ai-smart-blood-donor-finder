"""
Administrative Management Routes
--------------------------------
Provides platform administration, user management, donor verification,
request oversight, audit logs, and message handling.
Restricted exclusively to users with the 'admin' role.
"""

from flask import Blueprint, request, jsonify
from .. import database as db
from ..routes.auth_routes import login_required
from ..utils.validation import sanitize_string, validate_email, validate_name

admin_bp = Blueprint('admin_bp', __name__, url_prefix='/api')


# ==========================================================
# 1. PUBLIC CONTACT SUBMISSION
# ==========================================================

@admin_bp.route('/contact', methods=['POST'])
def submit_contact_message():
    """Receives contact message from general public."""
    data = request.get_json() or {}
    name = sanitize_string(data.get('name'))
    email = sanitize_string(data.get('email')).lower()
    subject = sanitize_string(data.get('subject', 'General Inquiry'))
    message = sanitize_string(data.get('message'))

    valid_name, name_err = validate_name(name, "Your name")
    if not valid_name:
        return jsonify({'success': False, 'message': name_err}), 400

    if not validate_email(email):
        return jsonify({'success': False, 'message': 'Please enter a valid email address.'}), 400

    if not message or len(message) < 5:
        return jsonify({'success': False, 'message': 'Please enter a meaningful message.'}), 400

    msg_id = db.execute_query(
        "INSERT INTO contact_messages (name, email, subject, message) VALUES (%s, %s, %s, %s)",
        (name, email, subject, message)
    )

    return jsonify({
        'success': True,
        'message': 'Your message has been received! Our support team will get in touch shortly.',
        'message_id': msg_id
    }), 201


# ==========================================================
# 2. ADMIN DASHBOARD & METRICS
# ==========================================================

@admin_bp.route('/admin/dashboard', methods=['GET'])
@login_required(roles='admin')
def get_admin_dashboard():
    """Fetches high-level KPIs and platform health for the admin dashboard."""
    total_users = db.fetch_one("SELECT COUNT(*) AS count FROM users")['count']
    total_donors = db.fetch_one("SELECT COUNT(*) AS count FROM donors")['count']
    active_donors = db.fetch_one("SELECT COUNT(*) AS count FROM donors WHERE is_active = 1 AND availability = 'Available'")['count']
    total_requests = db.fetch_one("SELECT COUNT(*) AS count FROM blood_requests")['count']
    active_emergencies = db.fetch_one("SELECT COUNT(*) AS count FROM blood_requests WHERE urgency = 'Emergency' AND status IN ('Pending', 'Matching', 'Donors Found')")['count']
    successful_matches = db.fetch_one("SELECT COUNT(*) AS count FROM donor_requests WHERE status IN ('Accepted', 'Completed')")['count']

    # Blood group breakdown
    bg_breakdown = db.fetch_all("SELECT blood_group, COUNT(*) as count FROM donors GROUP BY blood_group ORDER BY blood_group")

    # Recent users
    recent_users = db.fetch_all("SELECT user_id, name, email, role, city, is_active, created_at FROM users ORDER BY created_at DESC LIMIT 6")
    for u in recent_users:
        if u.get('created_at'):
            u['created_at'] = str(u['created_at'])

    # Recent blood requests
    recent_requests = db.fetch_all("SELECT * FROM blood_requests ORDER BY created_at DESC LIMIT 6")
    for r in recent_requests:
        if r.get('created_at'):
            r['created_at'] = str(r['created_at'])
        if r.get('required_date'):
            r['required_date'] = str(r['required_date'])

    return jsonify({
        'success': True,
        'metrics': {
            'total_users': total_users,
            'total_donors': total_donors,
            'active_donors': active_donors,
            'total_requests': total_requests,
            'active_emergencies': active_emergencies,
            'successful_matches': successful_matches
        },
        'blood_groups': {row['blood_group']: row['count'] for row in bg_breakdown},
        'recent_users': recent_users,
        'recent_requests': recent_requests
    }), 200


# ==========================================================
# 3. MANAGE USERS
# ==========================================================

@admin_bp.route('/admin/users', methods=['GET'])
@login_required(roles='admin')
def admin_list_users():
    """Lists users with filtering by role and search."""
    role = request.args.get('role', '').strip()
    search = request.args.get('search', '').strip()

    sql = "SELECT user_id, name, email, phone, role, city, area, is_active, created_at FROM users WHERE 1=1"
    params = []

    if role:
        sql += " AND role = %s"
        params.append(role)
    if search:
        sql += " AND (LOWER(name) LIKE LOWER(%s) OR LOWER(email) LIKE LOWER(%s))"
        params.extend([f"%{search}%", f"%{search}%"])

    sql += " ORDER BY created_at DESC"
    users = db.fetch_all(sql, params)
    for u in users:
        if u.get('created_at'):
            u['created_at'] = str(u['created_at'])

    return jsonify({'success': True, 'count': len(users), 'users': users}), 200


@admin_bp.route('/admin/users/<int:user_id>/status', methods=['PUT'])
@login_required(roles='admin')
def admin_toggle_user_status(user_id: int):
    """Activates or deactivates a user account."""
    data = request.get_json() or {}
    is_active = 1 if data.get('is_active', True) else 0

    user = db.fetch_one("SELECT user_id, name, email FROM users WHERE user_id = %s", (user_id,))
    if not user:
        return jsonify({'success': False, 'message': 'User not found.'}), 404

    db.execute_query("UPDATE users SET is_active = %s WHERE user_id = %s", (is_active, user_id))
    # Also update donor table if donor
    db.execute_query("UPDATE donors SET is_active = %s WHERE user_id = %s", (is_active, user_id))

    status_str = "activated" if is_active else "deactivated"
    db.execute_query(
        "INSERT INTO admin_logs (admin_id, action, details) VALUES (%s, %s, %s)",
        (request.current_user['user_id'], 'USER_STATUS_CHANGE', f"User {user['email']} {status_str}.")
    )

    return jsonify({
        'success': True,
        'message': f"User account {status_str} successfully.",
        'is_active': bool(is_active)
    }), 200


@admin_bp.route('/admin/users/<int:user_id>', methods=['DELETE'])
@login_required(roles='admin')
def admin_delete_user(user_id: int):
    """Deletes a user account and associated profile."""
    if user_id == request.current_user['user_id']:
        return jsonify({'success': False, 'message': 'Cannot delete your own admin account.'}), 400

    user = db.fetch_one("SELECT email FROM users WHERE user_id = %s", (user_id,))
    if not user:
        return jsonify({'success': False, 'message': 'User not found.'}), 404

    db.execute_query("DELETE FROM users WHERE user_id = %s", (user_id,))
    db.execute_query(
        "INSERT INTO admin_logs (admin_id, action, details) VALUES (%s, %s, %s)",
        (request.current_user['user_id'], 'USER_DELETED', f"Deleted user {user['email']} (ID: {user_id}).")
    )

    return jsonify({'success': True, 'message': 'User deleted successfully.'}), 200


# ==========================================================
# 4. MANAGE DONORS
# ==========================================================

@admin_bp.route('/admin/donors', methods=['GET'])
@login_required(roles='admin')
def admin_list_donors():
    """Lists all donors with administrative details."""
    bg = request.args.get('blood_group', '').strip().upper()
    city = request.args.get('city', '').strip()

    sql = """
    SELECT d.donor_id, d.user_id, d.name, d.age, d.gender, d.blood_group,
           d.phone, d.email, d.city, d.area, d.address, d.availability,
           d.last_donation_date, d.total_donations, d.is_active, d.created_at
    FROM donors d
    WHERE 1=1
    """
    params = []

    if bg:
        sql += " AND d.blood_group = %s"
        params.append(bg)
    if city:
        sql += " AND LOWER(d.city) = LOWER(%s)"
        params.append(city)

    sql += " ORDER BY d.created_at DESC"
    donors = db.fetch_all(sql, params)
    for d in donors:
        if d.get('last_donation_date'):
            d['last_donation_date'] = str(d['last_donation_date'])
        if d.get('created_at'):
            d['created_at'] = str(d['created_at'])

    return jsonify({'success': True, 'count': len(donors), 'donors': donors}), 200


@admin_bp.route('/admin/donors/<int:donor_id>/status', methods=['PUT'])
@login_required(roles='admin')
def admin_toggle_donor_status(donor_id: int):
    """Toggles active state or changes availability for a donor."""
    data = request.get_json() or {}
    donor = db.fetch_one("SELECT donor_id, name, email FROM donors WHERE donor_id = %s", (donor_id,))
    if not donor:
        return jsonify({'success': False, 'message': 'Donor not found.'}), 404

    if 'is_active' in data:
        is_active = 1 if data.get('is_active') else 0
        db.execute_query("UPDATE donors SET is_active = %s WHERE donor_id = %s", (is_active, donor_id))

    if 'availability' in data:
        avail = sanitize_string(data.get('availability'))
        if avail in ['Available', 'Temporarily Unavailable']:
            db.execute_query("UPDATE donors SET availability = %s WHERE donor_id = %s", (avail, donor_id))

    return jsonify({'success': True, 'message': 'Donor status updated successfully.'}), 200


@admin_bp.route('/admin/donors/<int:donor_id>', methods=['DELETE'])
@login_required(roles='admin')
def admin_delete_donor(donor_id: int):
    """Removes a donor record."""
    donor = db.fetch_one("SELECT user_id, name FROM donors WHERE donor_id = %s", (donor_id,))
    if not donor:
        return jsonify({'success': False, 'message': 'Donor not found.'}), 404

    db.execute_query("DELETE FROM donors WHERE donor_id = %s", (donor_id,))
    return jsonify({'success': True, 'message': 'Donor profile removed.'}), 200


# ==========================================================
# 5. MANAGE BLOOD REQUESTS
# ==========================================================

@admin_bp.route('/admin/requests', methods=['GET'])
@login_required(roles='admin')
def admin_list_requests():
    """Lists all blood requests for admin review."""
    sql = "SELECT * FROM blood_requests ORDER BY created_at DESC"
    requests_list = db.fetch_all(sql)
    for r in requests_list:
        if r.get('required_date'):
            r['required_date'] = str(r['required_date'])
        if r.get('created_at'):
            r['created_at'] = str(r['created_at'])

    return jsonify({'success': True, 'count': len(requests_list), 'requests': requests_list}), 200


@admin_bp.route('/admin/logs', methods=['GET'])
@login_required(roles='admin')
def admin_get_logs():
    """Audit logs for administrative tracking."""
    logs = db.fetch_all("SELECT * FROM admin_logs ORDER BY created_at DESC LIMIT 50")
    for l in logs:
        if l.get('created_at'):
            l['created_at'] = str(l['created_at'])
    return jsonify({'success': True, 'logs': logs}), 200


@admin_bp.route('/admin/contact-messages', methods=['GET'])
@login_required(roles='admin')
def admin_get_messages():
    """Lists contact feedback messages."""
    messages = db.fetch_all("SELECT * FROM contact_messages ORDER BY created_at DESC LIMIT 50")
    for m in messages:
        if m.get('created_at'):
            m['created_at'] = str(m['created_at'])
    return jsonify({'success': True, 'messages': messages}), 200
