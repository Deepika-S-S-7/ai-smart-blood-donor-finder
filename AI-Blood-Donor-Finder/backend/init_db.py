"""
Database Initialization Script
------------------------------
Initializes the database schema and populates seed data.
Prioritizes MySQL (XAMPP default localhost:3306).
If MySQL is not currently running, initializes local fallback SQLite
database so tests and local preview work immediately without crashing.
"""

import sys
import re
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from backend.config import Config
import backend.database as db_module


def parse_sql_statements(sql_content: str) -> list[str]:
    """Splits SQL script into executable individual statements."""
    # Remove SQL comments
    cleaned = re.sub(r'--[^\n]*\n', '\n', sql_content)
    cleaned = re.sub(r'/\*.*?\*/', '', cleaned, flags=re.DOTALL)

    statements = []
    current = []
    for line in cleaned.splitlines():
        line_str = line.strip()
        if not line_str:
            continue
        current.append(line_str)
        if line_str.endswith(';'):
            stmt = ' '.join(current).rstrip(';').strip()
            if stmt and not stmt.upper().startswith(('CREATE DATABASE', 'USE')):
                statements.append(stmt)
            current = []
    return statements


def init_mysql():
    """Initializes schema and seed data on MySQL (e.g. XAMPP)."""
    import pymysql

    print(f"[*] Connecting to MySQL at {Config.DB_HOST}:{Config.DB_PORT} as '{Config.DB_USER}'...")
    conn = pymysql.connect(
        host=Config.DB_HOST,
        port=Config.DB_PORT,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        autocommit=True
    )
    cursor = conn.cursor()

    print(f"[*] Creating database '{Config.DB_NAME}' if not exists...")
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{Config.DB_NAME}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
    cursor.execute(f"USE `{Config.DB_NAME}`;")

    # Read and run schema
    print(f"[*] Executing schema from {Config.SCHEMA_FILE}...")
    with open(Config.SCHEMA_FILE, 'r', encoding='utf-8') as f:
        schema_sql = f.read()

    for stmt in parse_sql_statements(schema_sql):
        try:
            cursor.execute(stmt)
        except Exception as e:
            print(f"  [!] Notice during schema execution: {e}")

    # Read and run seed data
    print(f"[*] Seeding fictional donors, test users, and sample requests from {Config.SEED_FILE}...")
    with open(Config.SEED_FILE, 'r', encoding='utf-8') as f:
        seed_sql = f.read()

    for stmt in parse_sql_statements(seed_sql):
        try:
            cursor.execute(stmt)
        except Exception as e:
            print(f"  [!] Notice during seed execution: {e}")

    cursor.close()
    conn.close()
    print("[OK] MySQL Database initialized successfully!")
    print(f"    Database: {Config.DB_NAME}")
    print("    Credentials:")
    print("      - Admin: admin@bloodfinder.org / Admin@123")
    print("      - Seeker: seeker@example.com / User@123")
    print("      - Donors: rajesh.a_pos@example.com / Donor@123")


def init_sqlite():
    """Initializes local SQLite fallback database."""
    import sqlite3

    db_path = db_module._SQLITE_PATH
    db_path.parent.mkdir(parents=True, exist_ok=True)
    print(f"[*] Initializing local fallback database at {db_path}...")

    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    # SQLite compatible DDL
    schema_sqlite = """
    DROP TABLE IF EXISTS admin_logs;
    DROP TABLE IF EXISTS contact_messages;
    DROP TABLE IF EXISTS donor_requests;
    DROP TABLE IF EXISTS blood_requests;
    DROP TABLE IF EXISTS donors;
    DROP TABLE IF EXISTS users;

    CREATE TABLE users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        phone TEXT NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'seeker',
        city TEXT,
        area TEXT,
        is_active INTEGER NOT NULL DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE donors (
        donor_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL UNIQUE,
        name TEXT NOT NULL,
        age INTEGER NOT NULL,
        gender TEXT NOT NULL,
        blood_group TEXT NOT NULL,
        phone TEXT NOT NULL,
        email TEXT NOT NULL,
        city TEXT NOT NULL,
        area TEXT NOT NULL,
        address TEXT,
        availability TEXT NOT NULL DEFAULT 'Available',
        last_donation_date DATE,
        total_donations INTEGER NOT NULL DEFAULT 0,
        is_active INTEGER NOT NULL DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE
    );

    CREATE TABLE blood_requests (
        request_id TEXT PRIMARY KEY,
        user_id INTEGER,
        patient_name TEXT NOT NULL,
        blood_group TEXT NOT NULL,
        hospital_name TEXT NOT NULL,
        hospital_location TEXT,
        city TEXT NOT NULL,
        area TEXT NOT NULL,
        contact_number TEXT NOT NULL,
        required_units INTEGER NOT NULL DEFAULT 1,
        urgency TEXT NOT NULL DEFAULT 'Normal',
        required_date DATE NOT NULL,
        additional_information TEXT,
        status TEXT NOT NULL DEFAULT 'Pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE SET NULL
    );

    CREATE TABLE donor_requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        request_id TEXT,
        requester_id INTEGER NOT NULL,
        donor_id INTEGER NOT NULL,
        match_score REAL DEFAULT 0.0,
        notes TEXT,
        status TEXT NOT NULL DEFAULT 'Pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (request_id) REFERENCES blood_requests (request_id) ON DELETE CASCADE,
        FOREIGN KEY (requester_id) REFERENCES users (user_id) ON DELETE CASCADE,
        FOREIGN KEY (donor_id) REFERENCES donors (donor_id) ON DELETE CASCADE
    );

    CREATE TABLE contact_messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL,
        subject TEXT NOT NULL,
        message TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE admin_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        admin_id INTEGER,
        action TEXT NOT NULL,
        details TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (admin_id) REFERENCES users (user_id) ON DELETE SET NULL
    );
    """
    cursor.executescript(schema_sqlite)

    # Seed data
    with open(Config.SEED_FILE, 'r', encoding='utf-8') as f:
        seed_sql = f.read()

    for stmt in parse_sql_statements(seed_sql):
        try:
            cursor.execute(stmt)
        except Exception as e:
            pass

    conn.commit()
    cursor.close()
    conn.close()
    print("[OK] Local SQLite fallback database initialized successfully!")


def main():
    print("==================================================")
    print(" AI-Based Smart Blood Donor Finder - DB Setup")
    print("==================================================")

    if db_module.is_mysql_available():
        try:
            init_mysql()
            return
        except Exception as e:
            print(f"[!] Error during MySQL initialization: {e}")
            print("[*] Falling back to SQLite setup for continuous availability...")

    else:
        print("[!] MySQL server (XAMPP) was not detected on localhost:3306.")
        print("    If you wish to use MySQL in XAMPP:")
        print("    1. Open XAMPP Control Panel")
        print("    2. Click 'Start' next to MySQL")
        print("    3. Re-run: python backend/init_db.py")
        print("    Initializing local fallback database so application can run right now...\n")

    init_sqlite()


if __name__ == '__main__':
    main()
