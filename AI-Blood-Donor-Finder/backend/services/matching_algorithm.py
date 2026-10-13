"""
Intelligent Rule-Based Donor Matching and Ranking Algorithm
------------------------------------------------------------
Implements an academic 100-point transparent rule-based scoring engine
to rank compatible blood donors for patients and emergency requests.

Scoring Criteria (Total: 100 Points):
1. Blood Compatibility: 50 points
   - Strict RBC compatibility check
   - Exact blood group match: 50 pts
   - Alternative compatible type (e.g. O- universal): 45 pts
   - Incompatible: 0 pts (Donor excluded)
2. Location Proximity: 25 points
   - Same city and same area: 25 pts
   - Same city, nearby/different area: 15 pts
   - Different city: 5 pts
3. Availability Status: 15 points
   - Currently Available: 15 pts
   - Temporarily Unavailable: 0 pts
4. Donation Recency & Eligibility: 10 points
   - Standard whole blood safe interval: >= 90 days
   - Never donated or > 90 days: 10 pts
   - 60 - 89 days: 5 pts
   - < 60 days: 0 pts (Flagged as recent donor)

DISCLAIMER:
This is an application matching score and algorithm search aid.
It does NOT constitute medical advice, diagnosis, or clinical cross-matching.
"""

from datetime import datetime, date
from typing import List, Dict, Any, Optional
from .compatibility import is_compatible, normalize_blood_group

SAFE_DONATION_INTERVAL_DAYS = 90


def calculate_recency_score(last_donation_date: Optional[Any]) -> tuple[int, str]:
    """
    Evaluates donation interval in days.
    Returns (points, explanation_string).
    """
    if not last_donation_date:
        return 10, "First-time donor / No recent donation recorded (Eligible)"

    if isinstance(last_donation_date, str):
        try:
            last_date = datetime.strptime(last_donation_date, "%Y-%m-%d").date()
        except ValueError:
            try:
                last_date = datetime.strptime(last_donation_date[:10], "%Y-%m-%d").date()
            except Exception:
                return 8, "Valid donor history"
    elif isinstance(last_donation_date, datetime):
        last_date = last_donation_date.date()
    elif isinstance(last_donation_date, date):
        last_date = last_donation_date
    else:
        return 8, "Valid donor history"

    today = date.today()
    days_since = (today - last_date).days

    if days_since >= SAFE_DONATION_INTERVAL_DAYS:
        return 10, f"Eligible - {days_since} days since last donation (>= 90 days safe interval)"
    elif days_since >= 60:
        return 5, f"Borderline interval - {days_since} days since last donation (60-89 days)"
    else:
        return 0, f"Recent donor - {days_since} days since last donation (< 60 days rest period)"


def calculate_location_score(donor_city: str, donor_area: str,
                             req_city: Optional[str], req_area: Optional[str]) -> tuple[int, str]:
    """
    Computes location proximity score out of 25 points.
    """
    if not req_city:
        return 20, "Location match not filtered"

    d_city = (donor_city or "").strip().lower()
    r_city = req_city.strip().lower()

    if d_city != r_city:
        return 5, f"Different city ({donor_city} vs {req_city})"

    # Same city
    if req_area:
        d_area = (donor_area or "").strip().lower()
        r_area = req_area.strip().lower()
        if d_area == r_area or r_area in d_area or d_area in r_area:
            return 25, f"Exact area match in {donor_city} ({donor_area})"
        else:
            return 15, f"Same city ({donor_city}), different area ({donor_area})"
    else:
        return 25, f"Same city ({donor_city})"


def calculate_donor_match(donor: Dict[str, Any],
                          recipient_blood_group: str,
                          req_city: Optional[str] = None,
                          req_area: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    Evaluates a single donor against recipient criteria.
    Returns ranked match dictionary, or None if strictly incompatible.
    """
    donor_bg = donor.get('blood_group', '')
    if not is_compatible(donor_bg, recipient_blood_group):
        # Strict medical compatibility check: NEVER recommend incompatible donors
        return None

    # 1. Compatibility Score (50 pts)
    d_norm = normalize_blood_group(donor_bg)
    r_norm = normalize_blood_group(recipient_blood_group)
    if d_norm == r_norm:
        compat_score = 50
        compat_type = "Exact Match"
        compat_desc = f"Identical blood group ({d_norm})"
    else:
        compat_score = 45
        compat_type = "Compatible Group"
        compat_desc = f"RBC compatible type ({d_norm} donor for {r_norm} recipient)"

    # 2. Location Score (25 pts)
    loc_score, loc_desc = calculate_location_score(
        donor.get('city', ''),
        donor.get('area', ''),
        req_city,
        req_area
    )

    # 3. Availability Score (15 pts)
    is_available = donor.get('availability', 'Available') == 'Available'
    avail_score = 15 if is_available else 0
    avail_desc = "Immediately Available" if is_available else "Temporarily Unavailable"

    # 4. Recency / Eligibility Score (10 pts)
    recency_score, recency_desc = calculate_recency_score(donor.get('last_donation_date'))

    total_score = compat_score + loc_score + avail_score + recency_score

    # Determine recommendation tier
    if total_score >= 85 and is_available:
        tier = "Optimal Match"
    elif total_score >= 70:
        tier = "High Match"
    elif total_score >= 50:
        tier = "Moderate Match"
    else:
        tier = "Low Match"

    return {
        'donor_id': donor.get('donor_id'),
        'user_id': donor.get('user_id'),
        'name': donor.get('name'),
        'blood_group': d_norm,
        'gender': donor.get('gender'),
        'age': donor.get('age'),
        'phone': donor.get('phone'),
        'email': donor.get('email'),
        'city': donor.get('city'),
        'area': donor.get('area'),
        'address': donor.get('address'),
        'availability': donor.get('availability'),
        'last_donation_date': str(donor.get('last_donation_date')) if donor.get('last_donation_date') else None,
        'total_donations': donor.get('total_donations', 0),
        # Intelligent Matching Metrics
        'match_score': round(float(total_score), 1),
        'compatibility_type': compat_type,
        'tier': tier,
        'score_breakdown': {
            'compatibility': {'score': compat_score, 'max': 50, 'detail': compat_desc},
            'location': {'score': loc_score, 'max': 25, 'detail': loc_desc},
            'availability': {'score': avail_score, 'max': 15, 'detail': avail_desc},
            'recency': {'score': recency_score, 'max': 10, 'detail': recency_desc}
        },
        'disclaimer': "Application Match Score calculated by rule-based algorithmic ranking aid. Not a medical probability or advice."
    }


def rank_donors(donor_list: List[Dict[str, Any]],
                recipient_blood_group: str,
                req_city: Optional[str] = None,
                req_area: Optional[str] = None,
                available_only: bool = False,
                sort_by: str = 'score') -> List[Dict[str, Any]]:
    """
    Ranks a list of candidate donors using the intelligent rule-based algorithm.
    Filters out incompatible donors and optionally unavailable donors.
    """
    ranked: List[Dict[str, Any]] = []

    for donor in donor_list:
        if available_only and donor.get('availability') != 'Available':
            continue

        match_data = calculate_donor_match(
            donor=donor,
            recipient_blood_group=recipient_blood_group,
            req_city=req_city,
            req_area=req_area
        )

        if match_data is not None:
            ranked.append(match_data)

    # Sorting
    if sort_by == 'score':
        ranked.sort(key=lambda x: (x['match_score'], x['availability'] == 'Available'), reverse=True)
    elif sort_by == 'location':
        ranked.sort(key=lambda x: (x['score_breakdown']['location']['score'], x['match_score']), reverse=True)
    elif sort_by == 'availability':
        ranked.sort(key=lambda x: (x['availability'] == 'Available', x['match_score']), reverse=True)
    elif sort_by == 'recency':
        ranked.sort(key=lambda x: (x['score_breakdown']['recency']['score'], x['match_score']), reverse=True)
    else:
        ranked.sort(key=lambda x: x['match_score'], reverse=True)

    return ranked
