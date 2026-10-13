"""
Blood Requests and Donor Engagement Routes
------------------------------------------
Handles emergency and standard blood requests, direct donor requests,
request status lifecycle (Pending -> Accepted/Rejected -> Fulfilled),
and real-time platform statistics.
"""

import random
import string
from datetime import datetime, date
from flask import Blueprint, request, jsonify

from .. import database as db
from ..routes.auth_routes import login_required, get_current_user
from ..services.compatibility import get_compatible_donor_groups
from ..services.matching_algorithm import rank_donors
from ..services.notification_service import record_notification
from ..utils.validation import validate_blood_request_data, sanitize_string

request_bp = Blueprint('request_bp', __name__, url_prefix='/api')


def generate_request_id() -> str:
    """Generates a clean tracking ID formatted as BR-XXXXXX."""
    chars = string.ascii_uppercase + string.digits
    suffix = ''.join(random.choices(chars, k=6))
    return f"BR-{suffix}"


# ==========================================================
# 1. BLOOD REQUESTS (Emergency & General)
# ==========================================================

@request_bp.route('/requests', methods=['POST'])
def create_blood_request():
    """
    Creates a new blood requirement.
    Works for both logged-in users and emergency submissions.
    """
    user = get_current_user()
    data = request.get_json() or {}

    is_valid, errors = validate_blood_request_data(data)
    if not is_valid:
        return jsonify({'success': False, 'message': errors[0], 'errors': errors}), 400

    request_id = generate_request_id()
    user_id = user['user_id'] if user else None
    patient_name = sanitize_string(data.get('patient_name'))
    blood_group = sanitize_string(data.get('blood_group')).upper()
    hospital_name = sanitize_string(data.get('hospital_name'))
    hospital_location = sanitize_string(data.get('hospital_location'))
    city = sanitize_string(data.get('city'))
    area = sanitize_string(data.get('area'))
    contact_number = sanitize_string(data.get('contact_number'))
    required_units = int(data.get('required_units', 1))
    urgency = sanitize_string(data.get('urgency')) or 'Normal'
    required_date = sanitize_string(data.get('required_date')) or str(date.today())
    additional_info = sanitize_string(data.get('additional_information'))

    if urgency not in ['Emergency', 'High', 'Normal']:
        urgency = 'Normal'

    status = 'Matching' if urgency == 'Emergency' else 'Pending'

    db.execute_query(
        """
        INSERT INTO blood_requests (
            request_id, user_id, patient_name, blood_group, hospital_name,
            hospital_location, city, area, contact_number, required_units,
            urgency, required_date, additional_information, status
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """,
        (
            request_id, user_id, patient_name, blood_group, hospital_name,
            hospital_location, city, area, contact_number, required_units,
            urgency, required_date, additional_info, status
        )
    )

    # Immediately calculate compatible donor count in the area
    compatible_groups = get_compatible_donor_groups(blood_group)
    donors = db.fetch_all("SELECT * FROM donors WHERE is_active = 1")
    ranked = rank_donors(donors, blood_group, city, area, available_only=True)
    matching_donors_count = len(ranked)

    # Log notification
    alert_type = "emergency" if urgency == 'Emergency' else "info"
    record_notification(
        title=f"New {urgency} Blood Request: {blood_group}",
        message=f"{patient_name} requires {required_units} unit(s) of {blood_group} at {hospital_name}, {city}.",
        alert_type=alert_type,
        user_id=user_id
    )

    return jsonify({
        'success': True,
        'message': 'Blood request created successfully.',
        'request_id': request_id,
        'urgency': urgency,
        'status': status,
        'matching_donors_count': matching_donors_count,
        'data': {
            'request_id': request_id,
            'patient_name': patient_name,
            'blood_group': blood_group,
            'hospital_name': hospital_name,
            'city': city,
            'area': area,
            'required_units': required_units,
            'urgency': urgency,
            'status': status
        }
    }), 201


@request_bp.route('/requests', methods=['GET'])
def list_blood_requests():
    """Lists blood requests with filters."""
    user = get_current_user()
    my_only = request.args.get('my_requests', 'false').lower() == 'true'
    urgency = request.args.get('urgency', '').strip()
    status = request.args.get('status', '').strip()
    city = request.args.get('city', '').strip()
    blood_group = request.args.get('blood_group', '').strip().upper()

    sql = "SELECT * FROM blood_requests WHERE 1=1"
    params = []

    if my_only:
        if not user:
            return jsonify({'success': False, 'message': 'Login required to view your requests.'}), 401
        sql += " AND user_id = %s"
        params.append(user['user_id'])

    if urgency:
        sql += " AND urgency = %s"
        params.append(urgency)

    if status:
        sql += " AND status = %s"
        params.append(status)

    if city:
        sql += " AND LOWER(city) = LOWER(%s)"
        params.append(city)

    if blood_group:
        sql += " AND blood_group = %s"
        params.append(blood_group)

    sql += " ORDER BY CASE urgency WHEN 'Emergency' THEN 1 WHEN 'High' THEN 2 ELSE 3 END, created_at DESC LIMIT 50"

    requests_list = db.fetch_all(sql, params)
    for r in requests_list:
        if r.get('required_date'):
            r['required_date'] = str(r['required_date'])
        if r.get('created_at'):
            r['created_at'] = str(r['created_at'])

    return jsonify({
        'success': True,
        'count': len(requests_list),
        'requests': requests_list
    }), 200


@request_bp.route('/requests/<request_id>', methods=['GET'])
def get_request_detail(request_id: str):
    """
    Returns full details for a blood request along with ranked compatible donors.
    """
    req_data = db.fetch_one("SELECT * FROM blood_requests WHERE request_id = %s", (request_id,))
    if not req_data:
        return jsonify({'success': False, 'message': 'Blood request not found.'}), 404

    if req_data.get('required_date'):
        req_data['required_date'] = str(req_data['required_date'])
    if req_data.get('created_at'):
        req_data['created_at'] = str(req_data['created_at'])

    # Find ranked matching donors
    all_donors = db.fetch_all("SELECT * FROM donors WHERE is_active = 1")
    ranked_matches = rank_donors(
        donor_list=all_donors,
        recipient_blood_group=req_data['blood_group'],
        req_city=req_data.get('city'),
        req_area=req_data.get('area'),
        available_only=False
    )

    return jsonify({
        'success': True,
        'request': req_data,
        'matching_donors': ranked_matches,
        'matches_count': len(ranked_matches)
    }), 200


@request_bp.route('/requests/<request_id>/status', methods=['PUT'])
@login_required()
def update_request_status(request_id: str):
    """Updates request status (Fulfilled, Cancelled, etc.)."""
    user = request.current_user
    data = request.get_json() or {}
    new_status = sanitize_string(data.get('status'))

    valid_statuses = ['Pending', 'Matching', 'Donors Found', 'Fulfilled', 'Cancelled']
    if new_status not in valid_statuses:
        return jsonify({'success': False, 'message': 'Invalid status.'}), 400

    req_data = db.fetch_one("SELECT * FROM blood_requests WHERE request_id = %s", (request_id,))
    if not req_data:
        return jsonify({'success': False, 'message': 'Blood request not found.'}), 404

    # Allow if user created it or user is admin
    if user['role'] != 'admin' and req_data.get('user_id') != user['user_id']:
        return jsonify({'success': False, 'message': 'Permission denied.'}), 403

    db.execute_query(
        "UPDATE blood_requests SET status = %s WHERE request_id = %s",
        (new_status, request_id)
    )

    return jsonify({
        'success': True,
        'message': f'Request status updated to {new_status}.',
        'status': new_status
    }), 200


# ==========================================================
# 2. DONOR DIRECT REQUESTS (Seeker -> Donor engagement)
# ==========================================================

@request_bp.route('/donor-requests', methods=['POST'])
@login_required()
def send_donor_request():
    """
    Sends a direct blood donation request to a specific donor.
    """
    user = request.current_user
    data = request.get_json() or {}

    donor_id = data.get('donor_id')
    request_id = data.get('request_id')  # optional link to blood_requests
    match_score = float(data.get('match_score', 0.0))
    notes = sanitize_string(data.get('notes', 'Blood donation request from patient.'))

    if not donor_id:
        return jsonify({'success': False, 'message': 'Target donor ID is required.'}), 400

    donor = db.fetch_one("SELECT donor_id, name, email, phone FROM donors WHERE donor_id = %s AND is_active = 1", (donor_id,))
    if not donor:
        return jsonify({'success': False, 'message': 'Target donor not found or unavailable.'}), 404

    # Prevent duplicate pending request to same donor
    existing = db.fetch_one(
        "SELECT id FROM donor_requests WHERE requester_id = %s AND donor_id = %s AND status = 'Pending'",
        (user['user_id'], donor_id)
    )
    if existing:
        return jsonify({'success': False, 'message': 'You have already sent a pending request to this donor.'}), 409

    inserted_id = db.execute_query(
        """
        INSERT INTO donor_requests (request_id, requester_id, donor_id, match_score, notes, status)
        VALUES (%s, %s, %s, %s, %s, 'Pending')
        """,
        (request_id, user['user_id'], donor_id, match_score, notes)
    )

    record_notification(
        title="Donation Request Sent",
        message=f"Request sent to donor {donor['name']}.",
        alert_type="success",
        user_id=user['user_id']
    )

    return jsonify({
        'success': True,
        'message': f"Request sent successfully to {donor['name']}!",
        'donor_request_id': inserted_id
    }), 201


@request_bp.route('/donor-requests/my-requests', methods=['GET'])
@login_required()
def get_my_sent_requests():
    """Seeker views requests sent to donors."""
    user = request.current_user
    sql = """
    SELECT dr.id, dr.request_id, dr.match_score, dr.notes, dr.status, dr.created_at,
           d.name AS donor_name, d.blood_group AS donor_blood_group, d.phone AS donor_phone,
           d.city AS donor_city, d.area AS donor_area,
           br.patient_name, br.hospital_name, br.urgency
    FROM donor_requests dr
    JOIN donors d ON dr.donor_id = d.donor_id
    LEFT JOIN blood_requests br ON dr.request_id = br.request_id
    WHERE dr.requester_id = %s
    ORDER BY dr.created_at DESC
    """
    rows = db.fetch_all(sql, (user['user_id'],))
    for r in rows:
        if r.get('created_at'):
            r['created_at'] = str(r['created_at'])

    return jsonify({
        'success': True,
        'count': len(rows),
        'requests': rows
    }), 200


@request_bp.route('/donor-requests/incoming', methods=['GET'])
@login_required(roles='donor')
def get_incoming_donor_requests():
    """Donor views requests received from seekers."""
    user = request.current_user
    donor = db.fetch_one("SELECT donor_id FROM donors WHERE user_id = %s", (user['user_id'],))
    if not donor:
        return jsonify({'success': False, 'message': 'Donor profile not found.'}), 404

    sql = """
    SELECT dr.id, dr.request_id, dr.match_score, dr.notes, dr.status, dr.created_at,
           u.name AS requester_name, u.phone AS requester_phone, u.email AS requester_email,
           br.patient_name, br.hospital_name, br.hospital_location, br.city, br.area,
           br.required_units, br.urgency, br.required_date
    FROM donor_requests dr
    JOIN users u ON dr.requester_id = u.user_id
    LEFT JOIN blood_requests br ON dr.request_id = br.request_id
    WHERE dr.donor_id = %s
    ORDER BY dr.created_at DESC
    """
    rows = db.fetch_all(sql, (donor['donor_id'],))
    for r in rows:
        if r.get('created_at'):
            r['created_at'] = str(r['created_at'])
        if r.get('required_date'):
            r['required_date'] = str(r['required_date'])

    return jsonify({
        'success': True,
        'count': len(rows),
        'incoming_requests': rows
    }), 200


@request_bp.route('/donor-requests/<int:req_id>/status', methods=['PUT'])
@login_required()
def update_donor_request_status(req_id: int):
    """
    Donor accepts/rejects, or seeker completes/cancels the request.
    """
    user = request.current_user
    data = request.get_json() or {}
    new_status = sanitize_string(data.get('status'))

    if new_status not in ['Accepted', 'Rejected', 'Completed', 'Cancelled']:
        return jsonify({'success': False, 'message': 'Invalid status choice.'}), 400

    record = db.fetch_one("SELECT * FROM donor_requests WHERE id = %s", (req_id,))
    if not record:
        return jsonify({'success': False, 'message': 'Request not found.'}), 404

    # Permission check:
    # If user is donor: can Accept or Reject
    # If user is requester: can Complete or Cancel
    # If admin: can do anything
    donor = db.fetch_one("SELECT donor_id FROM donors WHERE user_id = %s", (user['user_id'],))
    is_donor = donor and donor['donor_id'] == record['donor_id']
    is_requester = record['requester_id'] == user['user_id']
    is_admin = user['role'] == 'admin'

    if not (is_donor or is_requester or is_admin):
        return jsonify({'success': False, 'message': 'Unauthorized to modify this request.'}), 403

    db.execute_query(
        "UPDATE donor_requests SET status = %s WHERE id = %s",
        (new_status, req_id)
    )

    record_notification(
        title=f"Request Status Updated: {new_status}",
        message=f"Donation request #{req_id} was marked as {new_status}.",
        alert_type="success" if new_status in ['Accepted', 'Completed'] else "warning"
    )

    return jsonify({
        'success': True,
        'message': f'Request status successfully updated to {new_status}.',
        'status': new_status
    }), 200


# ==========================================================
# 3. LIVE PLATFORM STATISTICS
# ==========================================================

@request_bp.route('/requests/stats', methods=['GET'])
def get_platform_statistics():
    """
    Returns real-time platform metrics dynamically calculated
    from the database for home and dashboard pages.
    """
    total_donors = db.fetch_one("SELECT COUNT(*) AS count FROM donors WHERE is_active = 1")['count']
    active_available_donors = db.fetch_one("SELECT COUNT(*) AS count FROM donors WHERE is_active = 1 AND availability = 'Available'")['count']
    total_users = db.fetch_one("SELECT COUNT(*) AS count FROM users WHERE is_active = 1")['count']
    total_requests = db.fetch_one("SELECT COUNT(*) AS count FROM blood_requests")['count']
    active_emergencies = db.fetch_one("SELECT COUNT(*) AS count FROM blood_requests WHERE urgency = 'Emergency' AND status IN ('Pending', 'Matching', 'Donors Found')")['count']
    successful_matches = db.fetch_one("SELECT COUNT(*) AS count FROM donor_requests WHERE status IN ('Accepted', 'Completed')")['count']

    # Blood group distribution
    bg_rows = db.fetch_all("SELECT blood_group, COUNT(*) AS count FROM donors WHERE is_active = 1 GROUP BY blood_group ORDER BY blood_group")
    bg_distribution = {row['blood_group']: row['count'] for row in bg_rows}

    return jsonify({
        'success': True,
        'stats': {
            'total_donors': total_donors,
            'active_donors': active_available_donors,
            'total_users': total_users,
            'total_requests': total_requests,
            'active_emergencies': active_emergencies,
            'successful_matches': successful_matches,
            'blood_groups_covered': len(bg_distribution),
            'blood_group_distribution': bg_distribution
        }
    }), 200
