# AI-Based Smart Blood Donor Finder

An intelligent, production-style academic web platform designed to connect blood seekers with compatible, nearby blood donors rapidly during medical emergencies. Built as a College Computer Science & Engineering (CSE) full-stack project using **Python Flask REST API**, **MySQL (XAMPP)**, and responsive **Vanilla HTML5/CSS3/JavaScript**.

---

## 🌟 Key Features

1. **Intelligent Rule-Based Donor Ranking Algorithm (AI Component)**:
   - Transparent 100-point scoring model evaluating:
     - **Blood Compatibility (50 Points)**: Strict Red Blood Cell (RBC) antigen match. Incompatible donors receive 0 points and are strictly eliminated.
     - **Location Proximity (25 Points)**: Proximity evaluation across neighborhood areas and city boundaries.
     - **Live Availability (15 Points)**: Real-time donor availability status.
     - **Donation Recency & Safety Interval (10 Points)**: Enforces medical rest intervals (>= 90 days).
   - Generates an **Application Match Score (e.g. 95%)** with complete scoring breakdown.
2. **Strict Red Blood Cell Compatibility Matrix**:
   - Clinically mapped compatibility rules (`O-` universal donor, `AB+` universal recipient).
   - Guarantees **no incompatible donor** is ever recommended.
3. **Emergency Blood Broadcast System**:
   - Immediate requirement creation generating a unique tracking ID (`BR-XXXXXX`).
   - Instant calculation of available compatible donors in hospital vicinity.
4. **Donor Management & Live Availability Switch**:
   - Donors can toggle status between **"Available"** and **"Temporarily Unavailable"** at any time.
   - Record blood donations and track donation intervals.
5. **Seeker-to-Donor Request Lifecycle**:
   - Seekers send direct blood donation requests.
   - Donors receive notifications with **Accept** or **Decline** options.
   - Real-time status indicators (**Pending**, **Accepted**, **Rejected**, **Fulfilled**).
6. **Administrative Portal**:
   - Platform metrics, donor distribution across all 8 blood groups, user management (activate/deactivate/delete), and audit trail logs.
7. **Production Healthcare UI/UX**:
   - Glassmorphism, red/white healthcare palette, animated toast notifications, loading spinners, empty states, and 100% mobile-responsive layout.

---

## 🏗️ System Architecture

```
USER BROWSER (Desktop / Laptop / Tablet / Mobile)
   │
   ▼
Frontend (HTML5 + CSS3 + Vanilla JavaScript + Fetch API)
   │  REST API Calls (JSON)
   ▼
Flask Backend Server (Python 3.x, CORS, Security)
   │
   ├──► Intelligent Rule-Based Matching Algorithm (backend/services/matching_algorithm.py)
   │     └── Strict RBC Compatibility Matrix (backend/services/compatibility.py)
   │
   ├──► Validation & Password Hashing (Werkzeug Security, Regex)
   │
   ▼
MySQL Database (XAMPP phpMyAdmin / MySQL Server)
   ├── users (Seekers, Donors, Admins)
   ├── donors (Medical & geographic donor profiles)
   ├── blood_requests (Emergency requirements, hospital info, BR-XXXXXX)
   ├── donor_requests (Direct seeker-to-donor engagement)
   ├── contact_messages
   └── admin_logs
```

---

## 📁 Project Folder Structure

```
ai-blood-donor-finder/
├── frontend/
│   ├── index.html              # Modern landing page with dynamic statistics
│   ├── login.html              # Login with demo accounts autofill & password toggle
│   ├── register.html           # Seeker registration form
│   ├── donor-register.html     # Comprehensive donor registration form
│   ├── dashboard.html          # Personalized user & donor dashboard
│   ├── search.html             # Smart blood donor search with match scoring
│   ├── emergency-request.html  # Emergency blood broadcast with BR-XXXXXX ID
│   ├── my-requests.html        # Dual-tab request tracking (Seeker & Donor views)
│   ├── profile.html            # Profile editor, availability & donation dates
│   ├── admin.html              # Admin portal (KPIs, Users, Donors, Logs)
│   ├── about.html              # AI matching explanation, RBC matrix, disclaimers
│   ├── contact.html            # Contact form, emergency hotlines & FAQs
│   ├── css/
│   │   ├── style.css           # Healthcare design system & core components
│   │   ├── auth.css            # Authentication cards & form styling
│   │   ├── dashboard.css       # Widgets, analytics cards & data tables
│   │   ├── search.css          # Search filters, donor cards & score meters
│   │   └── responsive.css      # Mobile drawer & adaptive breakpoints
│   └── js/
│       ├── api.js              # Fetch API client, toast alerts, loading overlay
│       ├── auth.js             # Session tokens, navbar updater, route guards
│       ├── main.js             # Mobile menu, live stats counters, compat widget
│       ├── search.js           # Smart donor search & ranking controller
│       ├── request.js          # Emergency flow & Accept/Decline request actions
│       ├── dashboard.js        # Dashboard metrics & availability switch
│       ├── profile.js          # Profile management & donation logger
│       └── admin.js            # Admin portal controls & user/donor management
│
├── backend/
│   ├── app.py                  # Flask application factory & frontend server
│   ├── config.py               # Environment configuration (.env loader)
│   ├── database.py             # PyMySQL connection manager with safe fallback
│   ├── init_db.py              # CLI database setup & seed population script
│   ├── requirements.txt        # Backend dependencies
│   ├── routes/
│   │   ├── auth_routes.py      # Registration, login, JWT-signed tokens
│   │   ├── donor_routes.py     # Donor profiles, availability toggles
│   │   ├── search_routes.py    # Rule-based search & location endpoints
│   │   ├── request_routes.py   # Blood requests & donor engagement lifecycle
│   │   └── admin_routes.py     # Admin KPIs, user controls, audit logs
│   ├── services/
│   │   ├── compatibility.py    # Strict RBC compatibility matrix
│   │   ├── matching_algorithm.py # 100-point intelligent donor ranking algorithm
│   │   └── notification_service.py # In-app alerts & activity logging
│   └── utils/
│       └── validation.py       # Data sanitization & input validation
│
├── database/
│   ├── schema.sql              # Complete MySQL DDL table definitions & indexes
│   └── seed_data.sql           # Realistic fictional donors across all 8 blood groups
│
├── .env.example                # Template for environment variables
├── .gitignore                  # Git exclusions (virtualenvs, .env, __pycache__)
├── requirements.txt            # Project dependencies
└── README.md                   # Complete documentation
```

---

## 🛠️ Technology Stack

- **Frontend**: HTML5, CSS3, Vanilla JavaScript (ES6+), Fetch API.
- **Backend**: Python 3.10+, Flask, Flask-CORS, Werkzeug Security, itsdangerous.
- **Database**: MySQL 5.7+ / 8.0+ / MariaDB (via XAMPP).
- **Driver**: PyMySQL (Pure Python, no compilation needed).

---

## 🚀 Installation & Local Setup

### Step 1: Clone or Navigate to Project Directory
```powershell
cd "c:\Users\HP\Desktop\ai blood"
```

### Step 2: Create and Activate Virtual Environment (Recommended)
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### Step 3: Install Required Dependencies
```powershell
pip install -r requirements.txt
```

### Step 4: Configure Database Settings
Copy `.env.example` to `.env`:
```powershell
cp .env.example .env
```
Default `.env` values configured for standard XAMPP:
```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=
DB_NAME=blood_donor_finder
PORT=5000
```

### Step 5: Start MySQL in XAMPP & Initialize Database
1. Open **XAMPP Control Panel**.
2. Click **Start** next to **MySQL** (and **Apache** if using phpMyAdmin).
3. Initialize the database schema and 19 fictional donor records:
```powershell
python backend/init_db.py
```
> **Note**: You can also import `database/schema.sql` followed by `database/seed_data.sql` directly inside phpMyAdmin (`http://localhost/phpmyadmin`).

### Step 6: Start the Application Server
```powershell
python backend/app.py
```

### Step 7: Open in Browser
Visit: **[http://localhost:5000](http://localhost:5000)**

---

## 🔑 Demo Accounts for Evaluation

| Role | Email | Password | Access Level |
| :--- | :--- | :--- | :--- |
| **System Administrator** | `admin@bloodfinder.org` | `Admin@123` | Full Admin Portal (`/admin.html`) |
| **Blood Seeker** | `seeker@example.com` | `User@123` | Search, Emergency Requests, My Requests |
| **Donor (A+ Mumbai)** | `rajesh.a_pos@example.com` | `Donor@123` | Donor Dashboard, Accept/Decline Requests |
| **Donor (O- Chennai)** | `karthik.o_neg@example.com` | `Donor@123` | Universal Donor, Emergency Trauma Matching |

*(Clickable autofill buttons are also provided on `login.html` for instant one-click login!)*

---

## 🧠 AI Rule-Based Matching Algorithm Breakdown

The application implements a multi-parameter scoring formula totaling **100 Points**:

$$\text{Score} = \text{Compatibility (50)} + \text{Location (25)} + \text{Availability (15)} + \text{Recency (10)}$$

1. **Blood Compatibility (50 pts)**:
   - Evaluates Red Blood Cell antigens.
   - Exact match ($50\text{ pts}$), Alternative compatible donor ($45\text{ pts}$).
   - Incompatible donors score $0\text{ pts}$ and are strictly filtered out.
2. **Location Proximity (25 pts)**:
   - Same city & same neighborhood: $25\text{ pts}$.
   - Same city, different neighborhood: $15\text{ pts}$.
   - Different city: $5\text{ pts}$.
3. **Donor Availability (15 pts)**:
   - Available immediately: $15\text{ pts}$.
   - Temporarily unavailable: $0\text{ pts}$.
4. **Safe Donation Recency (10 pts)**:
   - Last donation $\ge 90\text{ days}$ ago or first-time donor: $10\text{ pts}$.
   - $60 - 89\text{ days}$: $5\text{ pts}$.
   - $< 60\text{ days}$: $0\text{ pts}$ (Recent donor rest period).

---

## 📡 REST API Overview

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/auth/register` | Register general seeker account |
| `POST` | `/api/auth/donor-register` | Register new donor with medical profile |
| `POST` | `/api/auth/login` | Authenticate user & receive signed token |
| `GET` | `/api/auth/me` | Fetch active user profile |
| `POST` | `/api/search/donors` | Search compatible donors with AI ranking |
| `GET` | `/api/search/locations` | List available cities and areas |
| `GET` | `/api/search/compatibility/<bg>` | Get RBC compatibility breakdown |
| `POST` | `/api/requests` | Create emergency or standard blood request |
| `GET` | `/api/requests` | List blood requests with filters |
| `GET` | `/api/requests/stats` | Live platform metrics |
| `POST` | `/api/donor-requests` | Send direct request to specific donor |
| `GET` | `/api/donor-requests/incoming` | Donor incoming requests |
| `PUT` | `/api/donor-requests/<id>/status` | Donor accepts/declines request |
| `PUT` | `/api/donors/availability` | Toggle donor availability status |
| `GET` | `/api/admin/dashboard` | High-level administrative metrics |
| `GET` | `/api/admin/users` | Manage user accounts |
| `POST` | `/api/contact` | Submit feedback or emergency inquiry |

---

## 🧪 Verification & Testing Commands

To verify the test suite:
```powershell
# Run database check
python backend/init_db.py

# Verify matching algorithm
python -c "import backend.database as db; from backend.services.matching_algorithm import rank_donors; donors = db.fetch_all('SELECT * FROM donors'); print('Ranked A+:', len(rank_donors(donors, 'A+')))"

# Verify server response
python -c "from backend.app import app; c = app.test_client(); print(c.get('/api/health').get_json())"
```

---

## 📦 Version Control (Git & GitHub Commands)

```powershell
# Initialize local git repository
git init

# Stage all files
git add .

# Create initial commit
git commit -m "feat: complete AI-Based Smart Blood Donor Finder project"

# Rename default branch to main
git branch -M main

# Add your remote GitHub repository
git remote add origin https://github.com/YOUR_USERNAME/AI-Blood-Donor-Finder.git

# Push to GitHub
git push -u origin main
```

---

## ⚠️ Academic Disclaimer
*This web application is an academic engineering project created for university CSE evaluation. It serves strictly as an informational and matching aid. It does not provide medical advice or replace certified hospital blood bank cross-matching procedures.*
