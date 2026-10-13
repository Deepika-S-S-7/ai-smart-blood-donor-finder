"""
Application Configuration Module
--------------------------------
Loads environment variables from .env with fallback defaults
suitable for local XAMPP and development environments.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BASE_DIR / '.env'

# Load environment variables
if ENV_FILE.exists():
    load_dotenv(dotenv_path=ENV_FILE)
else:
    load_dotenv()

class Config:
    """Base application configuration."""
    BASE_DIR = BASE_DIR
    SECRET_KEY = os.getenv('SECRET_KEY', 'blood-donor-ai-secret-key-2026-academic')

    # MySQL Database Settings (XAMPP defaults)
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = int(os.getenv('DB_PORT', 3306))
    DB_USER = os.getenv('DB_USER', 'root')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    DB_NAME = os.getenv('DB_NAME', 'blood_donor_finder')

    # Server settings
    PORT = int(os.getenv('PORT', 5000))
    DEBUG = os.getenv('FLASK_DEBUG', '1') == '1'
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*')

    # Static / Frontend directory
    FRONTEND_DIR = BASE_DIR / 'frontend'
    SCHEMA_FILE = BASE_DIR / 'database' / 'schema.sql'
    SEED_FILE = BASE_DIR / 'database' / 'seed_data.sql'
