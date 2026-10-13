"""
Root Application Runner
-----------------------
Quick entry point to start the AI-Based Smart Blood Donor Finder.
Usage:
    python run.py
    or
    python backend/app.py
"""

import sys
from pathlib import Path

# Add project root to sys.path
ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from backend.app import app
from backend.config import Config
import backend.database as db

if __name__ == '__main__':
    print("=" * 60)
    print(" AI-BASED SMART BLOOD DONOR FINDER")
    print("=" * 60)
    print(f"[*] Server URL:      http://localhost:{Config.PORT}")
    print(f"[*] Database Engine: {db.get_current_db_type()}")
    print(f"[*] Web Interface:   http://localhost:{Config.PORT}/index.html")
    print(f"[*] Health Check:    http://localhost:{Config.PORT}/api/health")
    print("=" * 60)
    app.run(host='0.0.0.0', port=Config.PORT, debug=Config.DEBUG)
