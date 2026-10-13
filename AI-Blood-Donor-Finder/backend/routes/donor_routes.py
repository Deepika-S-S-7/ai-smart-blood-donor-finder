"""
Donor Management Routes
-----------------------
Handles donor directory queries, profile retrieval, profile updates,
availability toggles, and donation history updates.
"""

from datetime import datetime, date
from flask import Blueprint, request, jsonify

from .. import database as db
from ..routes.auth_routes import login_required
from ..utils.validation import validate_donor_data, sanitize_string, validate_age, validate_phone, validate_name

donor_bp = Blueprint('donor_bp', __name__, url_prefix='/api/donors')


@donor_bp.route('', methods=['GET'])
def list_donors():
    """
    Returns public active donor list with optional blood group,
    city, area, and availability filters.
    """
    bg = request.args.get('blood_group', '').strip().upper()
    city = request.args.get('city', '').strip()
    area = request.args.get('area', '').strip()
    availability = request.args.get('availability', '').strip()

    sql = """
    SELECT donor_id, name, blood_group, gender, age, city, area, availability,
           last_donation_date, total_donations
    FROM donors
    WHERE is_active = 1
    """
    params = []

    if bg:
        sql += " AND blood_group = %s"
        params.append(bg)
    if city:
        sql += " AND LOWER(city) = LOWER(%s)"
        params.append(city)
    if area:
        sql += " AND LOWER(area) LIKE LOWER(%s)"
        params.append(f"%{area}%")
    if availability:
        sql += " AND availability = %s"
        params.append(availability)

    sql += " ORDER BY availability ASC, donor_id DESC LIMIT 100"

    donors = db.fetch_all(sql, params)
    for d in donors:
        if d.get('last_donation_date'):
            d['last_donation_date'] = str(d['last_donation_date'])

    return jsonify({
        'success': True,
        'count': len(donors),
        'donors': donors
    }), 200


@donor_bp.route('/<int:donor_id>', methods=['GET'])
def get_donor_detail(donor_id: int):
    """Returns single public donor profile."""
    donor = db.fetch_one(
        """
        SELECT donor_id, name, blood_group, gender, age, city, area, address, phone, email,
               availability, last_donation_date, total_donations, created_at
        FROM donors
        WHERE donor_id = %s AND is_active = 1
        """,
        (donor_id,)
    )
    if not donor:
        return jsonify({'success': False, 'message': 'Donor not found or inactive.'}), 404

    if donor.get('last_donation_date'):
        donor['last_donation_date'] = str(donor['last_donation_date'])
    if donor.get('created_at'):
        donor['created_at'] = str(donor['created_at'])

    return jsonify({'success': True, 'donor': donor}), 200


@donor_bp.route('/profile', methods=['GET'])
@login_required(roles='donor')
def get_my_donor_profile():
    """Returns profile for currently logged-in donor."""
    user = request.current_user
    donor = db.fetch_one("SELECT * FROM donors WHERE user_id = %s", (user['user_id'],))
    if not donor:
        return jsonify({'success': False, 'message': 'Donor record not found.'}), 404

    if donor.get('last_donation_date'):
        donor['last_donation_date'] = str(donor['last_donation_date'])

    return jsonify({'success': True, 'donor': donor}), 200


@donor_bp.route('/profile', methods=['PUT'])
@login_required(roles='donor')
def update_donor_profile():
    """Updates profile information for the authenticated donor."""
    user = request.current_user
    data = request.get_json() or {}

    donor = db.fetch_one("SELECT donor_id FROM donors WHERE user_id = %s", (user['user_id'],))
    if not donor:
        return jsonify({'success': False, 'message': 'Donor profile not found.'}), 404

    name = sanitize_string(data.get('name'))
    phone = sanitize_string(data.get('phone'))
    city = sanitize_string(data.get('city'))
    area = sanitize_string(data.get('area'))
    address = sanitize_string(data.get('address'))
    age = data.get('age')

    valid_name, name_err = validate_name(name, "Donor full name")
    if not valid_name:
        return jsonify({'success': False, 'message': name_err}), 400

    if not validate_phone(phone):
        return jsonify({'success': False, 'message': 'Please provide a valid contact phone number.'}), 400

    valid_age, age_err = validate_age(age)
    if not valid_age:
        return jsonify({'success': False, 'message': age_err}), 400

    # Update donors table
    db.execute_query(
        """
        UPDATE donors
        SET name = %s, phone = %s, city = %s, area = %s, address = %s, age = %s
        WHERE donor_id = %s
        """,
        (name, phone, city, area, address, int(age), donor['donor_id'])
    )

    # Update users table
    db.execute_query(
        "UPDATE users SET name = %s, phone = %s, city = %s, area = %s WHERE user_id = %s",
        (name, phone, city, area, user['user_id'])
    )

    return jsonify({
        'success': True,
        'message': 'Donor profile updated successfully.'
    }), 200


@donor_bp.route('/availability', methods=['PUT'])
@login_required(roles='donor')
def update_availability():
    """Quick toggle between 'Available' and 'Temporarily Unavailable'."""
    user = request.current_user
    data = request.get_json() or {}
    new_status = sanitize_string(data.get('availability'))

    if new_status not in ['Available', 'Temporarily Unavailable']:
        return jsonify({'success': False, 'message': 'Invalid availability status.'}), 400

    donor = db.fetch_one("SELECT donor_id FROM donors WHERE user_id = %s", (user['user_id'],))
    if not donor:
        return jsonify({'success': False, 'message': 'Donor profile not found.'}), 404

    db.execute_query(
        "UPDATE donors SET availability = %s WHERE donor_id = %s",
        (new_status, donor['donor_id'])
    )

    return jsonify({
        'success': True,
        'message': f'Availability updated to: {new_status}',
        'availability': new_status
    }), 200


@donor_bp.route('/donation-date', methods=['PUT'])
@login_required(roles='donor')
def update_donation_date():
    """Updates last donation date and increments donation counter."""
    user = request.current_user
    data = request.get_json() or {}
    donation_date = sanitize_string(data.get('last_donation_date'))

    if not donation_date:
        return jsonify({'success': False, 'message': 'Donation date is required.'}), 400

    try:
        parsed_date = datetime.strptime(donation_date, "%Y-%m-%d").date()
        if parsed_date > date.today():
            return jsonify({'success': False, 'message': 'Donation date cannot be in the future.'}), 400
    except Exception:
        return jsonify({'success': False, 'message': 'Invalid date format. Use YYYY-MM-DD.'}), 400

    donor = db.fetch_one("SELECT donor_id, total_donations FROM donors WHERE user_id = %s", (user['user_id'],))
    if not donor:
        return jsonify({'success': False, 'message': 'Donor profile not found.'}), 404

    new_total = (donor.get('total_donations') or 0) + 1
    db.execute_query(
        """
        UPDATE donors
        SET last_donation_date = %s, total_donations = %s
        WHERE donor_id = %s
        """,
        (donation_date, new_total, donor['donor_id'])
    )

    return jsonify({
        'success': True,
        'message': 'Donation record updated successfully. Thank you for your contribution!',
        'last_donation_date': donation_date,
        'total_donations': new_total
    }), 200
