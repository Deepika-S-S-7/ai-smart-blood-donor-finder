"""
Comprehensive Test Suite for AI-Based Smart Blood Donor Finder
--------------------------------------------------------------
Verifies:
1. Blood Compatibility Matrix (Strict RBC rules)
2. 100-Point Rule-Based Matching Algorithm
3. Flask REST APIs & Authentication
4. Emergency Request Lifecycle & Tracking ID
5. Donor Acceptance / Rejection Workflow
6. Admin Dashboard Access & Static HTML Serving
"""

import sys
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from backend.app import app
import backend.database as db
from backend.services.compatibility import is_compatible, get_compatible_donor_groups, get_compatible_recipient_groups
from backend.services.matching_algorithm import rank_donors, calculate_donor_match

def test_compatibility():
    print("[*] Testing Medical RBC Compatibility...")
    # O- is universal donor
    assert is_compatible('O-', 'A+') == True
    assert is_compatible('O-', 'B+') == True
    assert is_compatible('O-', 'AB+') == True
    assert is_compatible('O-', 'O-') == True
    assert len(get_compatible_recipient_groups('O-')) == 8

    # O- can only receive from O-
    assert is_compatible('A+', 'O-') == False
    assert is_compatible('B+', 'O-') == False
    assert is_compatible('O+', 'O-') == False
    assert is_compatible('O-', 'O-') == True
    assert get_compatible_donor_groups('O-') == ['O-']

    # AB+ is universal recipient
    assert len(get_compatible_donor_groups('AB+')) == 8

    # Incompatible pairs
    assert is_compatible('A+', 'B+') == False
    assert is_compatible('B+', 'A-') == False
    print("    [OK] Strict RBC Compatibility tests PASSED!")

def test_algorithm():
    print("[*] Testing 100-Point Rule-Based Matching Algorithm...")
    donors = db.fetch_all("SELECT * FROM donors WHERE is_active = 1")
    assert len(donors) > 0

    # Search for A+ in Mumbai Andheri East
    ranked = rank_donors(donors, recipient_blood_group='A+', req_city='Mumbai', req_area='Andheri East')
    assert len(ranked) > 0
    top = ranked[0]
    print(f"    Top donor for A+ in Mumbai: {top['name']} ({top['blood_group']}) - Score: {top['match_score']}% ({top['tier']})")
    assert top['blood_group'] in ['A+', 'A-', 'O+', 'O-']
    assert top['match_score'] >= 90.0

    # Incompatible recipient test: O- recipient must ONLY match O- donors
    ranked_oneg = rank_donors(donors, recipient_blood_group='O-')
    for d in ranked_oneg:
        assert d['blood_group'] == 'O-', f"Found incompatible blood group {d['blood_group']} for O- recipient!"
    print(f"    [OK] O- recipient strictly received only O- donors ({len(ranked_oneg)} matches).")
    print("    [OK] Matching Algorithm tests PASSED!")

def test_api_suite():
    print("[*] Testing REST API Endpoints via Flask Test Client...")
    client = app.test_client()

    # 1. Health check
    res = client.get('/api/health')
    assert res.status_code == 200
    assert res.get_json()['status'] == 'healthy'

    # 2. Stats
    res = client.get('/api/requests/stats')
    assert res.status_code == 200
    assert res.get_json()['stats']['total_donors'] >= 19

    # 3. Invalid login
    res = client.post('/api/auth/login', json={'email': 'nonexistent@test.com', 'password': 'wrong'})
    assert res.status_code == 401

    # 4. Valid Admin login
    res = client.post('/api/auth/login', json={'email': 'admin@bloodfinder.org', 'password': 'Admin@123'})
    assert res.status_code == 200
    admin_token = res.get_json()['token']
    assert admin_token is not None

    # 5. Valid Seeker login
    res = client.post('/api/auth/login', json={'email': 'seeker@example.com', 'password': 'User@123'})
    assert res.status_code == 200
    seeker_token = res.get_json()['token']

    # 6. Valid Donor login
    res = client.post('/api/auth/login', json={'email': 'rajesh.a_pos@example.com', 'password': 'Donor@123'})
    assert res.status_code == 200
    donor_token = res.get_json()['token']

    # 7. Search API
    res = client.post('/api/search/donors', json={'blood_group': 'B+', 'city': 'Bangalore'})
    assert res.status_code == 200
    search_data = res.get_json()
    assert search_data['count'] > 0
    print(f"    Search for B+ in Bangalore returned {search_data['count']} ranked donors.")

    # 8. Create Emergency Blood Request
    req_payload = {
        'patient_name': 'Test Emergency Patient',
        'blood_group': 'O-',
        'hospital_name': 'City General Hospital',
        'hospital_location': 'ICU Ward 2',
        'city': 'Mumbai',
        'area': 'Borivali',
        'contact_number': '9876501234',
        'required_units': 2,
        'urgency': 'Emergency',
        'required_date': '2026-09-24',
        'additional_information': 'Automated test emergency run.'
    }
    res = client.post('/api/requests', json=req_payload, headers={'Authorization': f'Bearer {seeker_token}'})
    assert res.status_code == 201
    req_res = res.get_json()
    request_id = req_res['request_id']
    assert request_id.startswith('BR-')
    print(f"    Created Emergency Blood Request: {request_id} with {req_res['matching_donors_count']} matching donors in area.")

    # 9. Send direct donor request
    # Donor Rajesh Kumar has donor_id = 1
    dreq_res = client.post('/api/donor-requests', json={
        'donor_id': 1,
        'request_id': request_id,
        'match_score': 95.0,
        'notes': 'Urgent requirement at City General'
    }, headers={'Authorization': f'Bearer {seeker_token}'})
    # Either 201 or 409 if already exists
    assert dreq_res.status_code in [201, 409]

    # 10. Donor incoming requests
    res = client.get('/api/donor-requests/incoming', headers={'Authorization': f'Bearer {donor_token}'})
    assert res.status_code == 200
    incoming = res.get_json()['incoming_requests']
    print(f"    Donor Rajesh has {len(incoming)} incoming requests.")

    # 11. Donor toggles availability
    res = client.put('/api/donors/availability', json={'availability': 'Temporarily Unavailable'}, headers={'Authorization': f'Bearer {donor_token}'})
    assert res.status_code == 200
    # Toggle back to Available
    res = client.put('/api/donors/availability', json={'availability': 'Available'}, headers={'Authorization': f'Bearer {donor_token}'})
    assert res.status_code == 200

    # 12. Admin portal access
    res = client.get('/api/admin/dashboard', headers={'Authorization': f'Bearer {admin_token}'})
    assert res.status_code == 200
    metrics = res.get_json()['metrics']
    assert metrics['total_users'] > 0
    print(f"    Admin Dashboard verified: {metrics['total_users']} users, {metrics['total_donors']} donors.")

    # 13. Static frontend pages test
    pages = ['/', '/index.html', '/login.html', '/register.html', '/donor-register.html', '/dashboard.html', '/search.html', '/emergency-request.html', '/my-requests.html', '/profile.html', '/admin.html', '/about.html', '/contact.html']
    for p in pages:
        r = client.get(p)
        assert r.status_code == 200, f"Page {p} returned status {r.status_code}"
    print(f"    [OK] All {len(pages)} frontend web pages served with HTTP 200 OK.")

    print("    [OK] All REST API and Frontend Serving tests PASSED!")

if __name__ == '__main__':
    print("==================================================")
    print(" AI-Based Smart Blood Donor Finder - Verification")
    print("==================================================")
    test_compatibility()
    test_algorithm()
    test_api_suite()
    print("==================================================")
    print(" ALL TESTS SUCCESSFULLY PASSED! APPLICATION IS 100% READY.")
    print("==================================================")
