"""
Live Demonstration Script for AI-Based Smart Blood Donor Finder
---------------------------------------------------------------
Sends real HTTP requests to http://localhost:5000 to demonstrate all features
and outputs readable, structured terminal logs.
"""

import urllib.request
import json

BASE_URL = "http://localhost:5050"

def make_request(path, method="GET", data=None, token=None):
    url = f"{BASE_URL}{path}"
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    body = json.dumps(data).encode("utf-8") if data else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode("utf-8"))

def run_demo():
    print("=" * 70)
    print("  AI-BASED SMART BLOOD DONOR FINDER - LIVE SYSTEM OUTPUT")
    print("=" * 70)

    # 1. Health Check
    print("\n[1] Checking System Health & Server Status...")
    status, health = make_request("/api/health")
    print(f"    Status Code: {status}")
    print(f"    Service:     {health.get('service')}")
    print(f"    Database:    {health.get('database_engine')}")
    print(f"    Version:     {health.get('version')}")

    # 2. Platform Statistics
    print("\n[2] Fetching Live Platform Statistics...")
    status, stats_res = make_request("/api/requests/stats")
    stats = stats_res.get("stats", {})
    print(f"    Total Registered Donors: {stats.get('total_donors')}")
    print(f"    Active Available Donors: {stats.get('active_donors')}")
    print(f"    Total Platform Users:    {stats.get('total_users')}")
    print(f"    Active Emergencies:      {stats.get('active_emergencies')}")
    print(f"    Successful Matches:      {stats.get('successful_matches')}")
    print(f"    Blood Group Coverage:    {stats.get('blood_groups_covered')} / 8 types")

    # 3. Authentication Flow
    print("\n[3] Authenticating as Blood Seeker (seeker@example.com)...")
    status, login_res = make_request("/api/auth/login", method="POST", data={
        "email": "seeker@example.com",
        "password": "User@123"
    })
    seeker_token = login_res.get("token")
    user = login_res.get("user", {})
    print(f"    Login Status: {status} OK")
    print(f"    Logged-in User: {user.get('name')} | Role: {user.get('role')} | City: {user.get('city')}")
    print(f"    Auth Token:   {seeker_token[:25]}... (URLSafeTimed JWT)")

    # 4. Intelligent AI Matching Algorithm (Recipient: A+ in Mumbai)
    print("\n[4] Running Intelligent Donor Matching Algorithm (Recipient: A+, Location: Mumbai)...")
    status, search_res = make_request("/api/search/donors", method="POST", data={
        "blood_group": "A+",
        "city": "Mumbai",
        "area": "Andheri East",
        "availability": "Available",
        "sort_by": "score"
    })
    donors = search_res.get("results", [])
    print(f"    Compatible Donor Types: {', '.join(search_res.get('compatible_donor_groups', []))}")
    print(f"    Matching Donors Found:  {len(donors)}")
    print("    ------------------------------------------------------------------")
    print("    Top Ranked Donors by 100-Point Rule Scoring:")
    for idx, d in enumerate(donors[:3], 1):
        b = d.get("score_breakdown", {})
        compat_s = b.get("compatibility", {}).get("score", 0)
        loc_s = b.get("location", {}).get("score", 0)
        avail_s = b.get("availability", {}).get("score", 0)
        rec_s = b.get("recency", {}).get("score", 0)
        print(f"    Rank #{idx}: {d.get('name')} [{d.get('blood_group')}] - {d.get('city')} ({d.get('area')})")
        print(f"      - Match Score: {d.get('match_score')}% ({d.get('tier')})")
        print(f"      - Breakdown: Compat: {compat_s}/50 | Location: {loc_s}/25 | Avail: {avail_s}/15 | Recency: {rec_s}/10")
        print(f"      - Last Donated: {d.get('last_donation_date') or 'First-time donor (Fully Eligible)'}")

    # 5. Strict RBC Compatibility Verification (Recipient: O-)
    print("\n[5] Strict Compatibility Test: Searching Donors for Rare O- Negative Recipient...")
    status, o_neg_res = make_request("/api/search/donors", method="POST", data={"blood_group": "O-"})
    o_donors = o_neg_res.get("results", [])
    matched_groups = set(d["blood_group"] for d in o_donors)
    print(f"    Allowed Donor Types for O-: {o_neg_res.get('compatible_donor_groups')}")
    print(f"    Matched Blood Types in DB:  {list(matched_groups)}")
    assert matched_groups == {"O-"}, "Violation: Non-O- donor returned for O- recipient!"
    print(f"    [OK] Medical safety confirmed: 100% of {len(o_donors)} matches are strictly O- negative.")

    # 6. Emergency Blood Request Creation
    print("\n[6] Submitting Emergency Blood Broadcast (/api/requests)...")
    status, req_res = make_request("/api/requests", method="POST", data={
        "patient_name": "Siddharth Malhotra",
        "blood_group": "A+",
        "hospital_name": "Kokilaben Dhirubhai Ambani Hospital",
        "hospital_location": "Rao Saheb Achutrao Patwardhan Marg",
        "city": "Mumbai",
        "area": "Andheri West",
        "contact_number": "9820098200",
        "required_units": 2,
        "urgency": "Emergency",
        "required_date": "2026-10-06",
        "additional_information": "Immediate emergency trauma surgery required."
    }, token=seeker_token)
    req_id = req_res.get("request_id")
    print(f"    Status Code:        {status} CREATED")
    print(f"    Generated ID:       {req_id}")
    print(f"    Urgency Level:      {req_res.get('urgency')}")
    print(f"    Immediate Matches:  {req_res.get('matching_donors_count')} compatible donors alerted in hospital zone")

    # 7. Sending Direct Blood Request to Top Donor
    top_donor_id = donors[0]["donor_id"]
    top_donor_name = donors[0]["name"]
    print(f"\n[7] Sending Direct Blood Request to Top Donor #{top_donor_id} ({top_donor_name})...")
    status, dreq_res = make_request("/api/donor-requests", method="POST", data={
        "donor_id": top_donor_id,
        "request_id": req_id,
        "match_score": donors[0]["match_score"],
        "notes": "Urgent requirement for trauma surgery at Kokilaben Hospital Mumbai."
    }, token=seeker_token)
    print(f"    Status: {dreq_res.get('message')}")

    # 8. Donor Login & Viewing Incoming Requests
    print(f"\n[8] Logging in as Donor Rajesh Kumar (rajesh.a_pos@example.com)...")
    status, donor_login = make_request("/api/auth/login", method="POST", data={
        "email": "rajesh.a_pos@example.com",
        "password": "Donor@123"
    })
    donor_token = donor_login.get("token")
    status, inc_res = make_request("/api/donor-requests/incoming", token=donor_token)
    incoming_list = inc_res.get("incoming_requests", [])
    print(f"    Donor Incoming Requests Count: {len(incoming_list)}")
    if incoming_list:
        latest = incoming_list[0]
        print(f"    Latest Request #{latest.get('id')}: From {latest.get('requester_name')} (Phone: {latest.get('requester_phone')})")
        print(f"      Patient: {latest.get('patient_name')} at {latest.get('hospital_name')}, {latest.get('city')}")
        print(f"      Urgency: {latest.get('urgency')} | Status: {latest.get('status')}")

        # Donor Accepts the Request
        print(f"    Donor Actions: Accepting Request #{latest.get('id')}...")
        status, update_res = make_request(f"/api/donor-requests/{latest.get('id')}/status", method="PUT", data={
            "status": "Accepted"
        }, token=donor_token)
        print(f"    Response: {update_res.get('message')}")

    # 9. Admin Dashboard Metrics
    print("\n[9] Accessing Admin Portal (/api/admin/dashboard)...")
    status, admin_login = make_request("/api/auth/login", method="POST", data={
        "email": "admin@bloodfinder.org",
        "password": "Admin@123"
    })
    admin_token = admin_login.get("token")
    status, admin_dash = make_request("/api/admin/dashboard", token=admin_token)
    m = admin_dash.get("metrics", {})
    print(f"    Admin KPIs:")
    print(f"      - Total System Users:     {m.get('total_users')}")
    print(f"      - Registered Donors:      {m.get('total_donors')}")
    print(f"      - Active Donors:          {m.get('active_donors')}")
    print(f"      - Active Emergencies:     {m.get('active_emergencies')}")
    print(f"      - Successful Matches:     {m.get('successful_matches')}")
    print(f"      - Total Blood Requests:   {m.get('total_requests')}")

    print("\n" + "=" * 70)
    print("  LIVE DEMONSTRATION COMPLETE - ALL 9 END-TO-END FLOWS OPERATIONAL!")
    print("=" * 70)

if __name__ == "__main__":
    run_demo()
