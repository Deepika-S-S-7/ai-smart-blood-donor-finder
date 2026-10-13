"""
Intelligent Donor Search Routes
-------------------------------
Powers the AI-based smart search engine. Evaluates candidate donors
using strict Red Blood Cell compatibility, location proximity,
availability, and donation intervals.
"""

from flask import Blueprint, request, jsonify
from .. import database as db
from ..services.compatibility import (
    is_valid_blood_group,
    get_compatible_donor_groups,
    get_compatible_recipient_groups,
    normalize_blood_group
)
from ..services.matching_algorithm import rank_donors
from ..utils.validation import sanitize_string

search_bp = Blueprint('search_bp', __name__, url_prefix='/api/search')


@search_bp.route('/donors', methods=['POST'])
def search_donors():
    """
    Intelligent rule-based blood donor search.
    Expects JSON:
    - blood_group (required, recipient's blood group)
    - city (optional)
    - area (optional)
    - availability (optional, 'Available' or 'All')
    - sort_by (optional: 'score', 'location', 'availability', 'recency')
    """
    data = request.get_json() or {}
    bg_input = sanitize_string(data.get('blood_group')).upper()
    city = sanitize_string(data.get('city'))
    area = sanitize_string(data.get('area'))
    availability = sanitize_string(data.get('availability')) or 'Available'
    sort_by = sanitize_string(data.get('sort_by')) or 'score'

    if not bg_input or not is_valid_blood_group(bg_input):
        return jsonify({
            'success': False,
            'message': 'Please provide a valid recipient blood group (A+, A-, B+, B-, AB+, AB-, O+, O-).'
        }), 400

    recipient_bg = normalize_blood_group(bg_input)

    # 1. Fetch active donors from database
    # We query all active donors and allow the intelligent algorithm to evaluate compatibility and score
    donors_query = """
    SELECT donor_id, user_id, name, age, gender, blood_group, phone, email,
           city, area, address, availability, last_donation_date, total_donations
    FROM donors
    WHERE is_active = 1
    """
    params = []

    # Optional initial database filter on city for query optimization
    if city:
        # We also include nearby donors to allow ranking rather than hard cutoff
        # (matching algorithm scores same-city higher)
        pass

    all_donors = db.fetch_all(donors_query, params)

    # 2. Run Intelligent Matching Algorithm
    available_only = (availability.lower() == 'available')
    ranked_donors = rank_donors(
        donor_list=all_donors,
        recipient_blood_group=recipient_bg,
        req_city=city if city else None,
        req_area=area if area else None,
        available_only=available_only,
        sort_by=sort_by
    )

    compatible_groups = get_compatible_donor_groups(recipient_bg)

    return jsonify({
        'success': True,
        'count': len(ranked_donors),
        'search_criteria': {
            'recipient_blood_group': recipient_bg,
            'city': city or 'Any City',
            'area': area or 'Any Area',
            'availability_filter': availability,
            'sort_by': sort_by
        },
        'compatible_donor_groups': compatible_groups,
        'results': ranked_donors,
        'message': f"Found {len(ranked_donors)} compatible donors." if ranked_donors else "No compatible donors found matching your exact criteria."
    }), 200


@search_bp.route('/locations', methods=['GET'])
def get_search_locations():
    """
    Returns unique cities and areas from existing donors for
    dropdowns and autocomplete in search and emergency forms.
    """
    cities = db.fetch_all("SELECT DISTINCT city FROM donors WHERE is_active = 1 AND city IS NOT NULL AND city != '' ORDER BY city ASC")
    areas = db.fetch_all("SELECT DISTINCT city, area FROM donors WHERE is_active = 1 AND area IS NOT NULL AND area != '' ORDER BY city, area ASC")

    city_list = [c['city'] for c in cities]
    city_area_map = {}
    for item in areas:
        c = item['city']
        a = item['area']
        if c not in city_area_map:
            city_area_map[c] = []
        if a not in city_area_map[c]:
            city_area_map[c].append(a)

    return jsonify({
        'success': True,
        'cities': city_list,
        'city_areas': city_area_map
    }), 200


@search_bp.route('/compatibility/<blood_group>', methods=['GET'])
def get_compatibility_info(blood_group: str):
    """
    Returns compatibility breakdown (can receive from & can donate to)
    for interactive educational widgets.
    """
    bg = normalize_blood_group(blood_group)
    if not is_valid_blood_group(bg):
        return jsonify({'success': False, 'message': 'Invalid blood group'}), 400

    can_receive_from = get_compatible_donor_groups(bg)
    can_donate_to = get_compatible_recipient_groups(bg)

    is_universal_donor = (bg == 'O-')
    is_universal_recipient = (bg == 'AB+')

    return jsonify({
        'success': True,
        'blood_group': bg,
        'can_receive_from': can_receive_from,
        'can_donate_to': can_donate_to,
        'is_universal_donor': is_universal_donor,
        'is_universal_recipient': is_universal_recipient
    }), 200
