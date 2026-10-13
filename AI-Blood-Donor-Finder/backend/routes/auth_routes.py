"""
Authentication and User Account Routes
--------------------------------------
Provides secure user/donor registration, password hashing (Werkzeug),
token-based session management, profile retrieval, and password updates.
"""

from functools import wraps
from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature

from ..config import Config
from .. import database as db
from ..utils.validation import (
    validate_email,
    validate_phone,
    validate_registration_data,
    validate_donor_data,
    validate_password,
    sanitize_string
)

auth_bp = Blueprint('auth_bp', __name__, url_prefix='/api/auth')
serializer = URLSafeTimedSerializer(Config.SECRET_KEY)
TOKEN_MAX_AGE = 86400 * 7  # 7 days


def generate_token(user_id: int, role: str, email: str) -> str:
    """Generates a cryptographically signed authentication token."""
    return serializer.dumps({'user_id': user_id, 'role': role, 'email': email})


def decode_token(token: str) -> dict | None:
    """Validates and unpacks authentication token."""
    if not token:
        return None
    try:
        return serializer.loads(token, max_age=TOKEN_MAX_AGE)
    except (SignatureExpired, BadSignature, Exception):
        return None


def get_current_user():
    """Extracts authenticated user from Authorization header."""
    auth_header = request.headers.get('Authorization', '')
    token = None
    if auth_header.startswith('Bearer '):
        token = auth_header.split(' ', 1)[1].strip()
    elif 'token' in request.args:
        token = request.args.get('token')

    if not token:
        return None

    payload = decode_token(token)
    if not payload:
        return None

    user = db.fetch_one(
        "SELECT user_id, name, email, phone, role, city, area, is_active, created_at FROM users WHERE user_id = %s",
        (payload['user_id'],)
    )
    if not user or not user.get('is_active', 1):
        return None

    # Attach donor details if user is a registered donor
    if user['role'] == 'donor':
        donor = db.fetch_one("SELECT * FROM donors WHERE user_id = %s", (user['user_id'],))
        user['donor_profile'] = donor

    return user


def login_required(roles=None):
    """Decorator to enforce authentication and optional role restrictions."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user = get_current_user()
            if not user:
                return jsonify({
                    'success': False,
                    'message': 'Authentication required. Please log in.'
                }), 401

            if roles:
                allowed = [roles] if isinstance(roles, str) else roles
                if user['role'] not in allowed:
                    return jsonify({
                        'success': False,
                        'message': 'Unauthorized access: You do not have permission to view this resource.'
                    }), 403

            request.current_user = user
            return f(*args, **kwargs)
        return decorated_function
    return decorator


@auth_bp.route('/register', methods=['POST'])
def register():
    """Registers a general user (Seeker / Patient / Blood Requester)."""
    data = request.get_json() or {}
    is_valid, errors = validate_registration_data(data)
    if not is_valid:
        return jsonify({'success': False, 'message': errors[0], 'errors': errors}), 400

    name = sanitize_string(data.get('name'))
    email = sanitize_string(data.get('email')).lower()
    phone = sanitize_string(data.get('phone'))
    password = data.get('password')
    city = sanitize_string(data.get('city'))
    area = sanitize_string(data.get('area'))
    role = 'seeker'

    # Check for duplicate email
    existing = db.fetch_one("SELECT user_id FROM users WHERE LOWER(email) = %s", (email,))
    if existing:
        return jsonify({'success': False, 'message': 'An account with this email already exists.'}), 409

    pwd_hash = generate_password_hash(password)
    user_id = db.execute_query(
        """
        INSERT INTO users (name, email, phone, password_hash, role, city, area, is_active)
        VALUES (%s, %s, %s, %s, %s, %s, %s, 1)
        """,
        (name, email, phone, pwd_hash, role, city, area)
    )

    token = generate_token(user_id, role, email)
    return jsonify({
        'success': True,
        'message': 'Registration successful! Welcome to Smart Blood Donor Finder.',
        'token': token,
        'user': {
            'user_id': user_id,
            'name': name,
            'email': email,
            'role': role,
            'phone': phone,
            'city': city,
            'area': area
        }
    }), 201


@auth_bp.route('/donor-register', methods=['POST'])
def donor_register():
    """Registers a new donor (creates User record + linked Donor profile)."""
    data = request.get_json() or {}

    # Validation
    is_valid, errors = validate_donor_data(data)
    pwd = data.get('password', '')
    valid_pwd, pwd_msg = validate_password(pwd)
    if not valid_pwd:
        errors.append(pwd_msg)
        is_valid = False

    if not is_valid:
        return jsonify({'success': False, 'message': errors[0], 'errors': errors}), 400

    name = sanitize_string(data.get('name'))
    email = sanitize_string(data.get('email')).lower()
    phone = sanitize_string(data.get('phone'))
    city = sanitize_string(data.get('city'))
    area = sanitize_string(data.get('area'))
    address = sanitize_string(data.get('address'))
    blood_group = sanitize_string(data.get('blood_group')).upper()
    gender = sanitize_string(data.get('gender')) or 'Male'
    age = int(data.get('age'))
    availability = sanitize_string(data.get('availability')) or 'Available'
    last_donation_date = data.get('last_donation_date') or None

    # Check for duplicate email
    existing = db.fetch_one("SELECT user_id FROM users WHERE LOWER(email) = %s", (email,))
    if existing:
        return jsonify({'success': False, 'message': 'An account with this email address already exists.'}), 409

    pwd_hash = generate_password_hash(pwd)

    # 1. Insert into users
    user_id = db.execute_query(
        """
        INSERT INTO users (name, email, phone, password_hash, role, city, area, is_active)
        VALUES (%s, %s, %s, %s, 'donor', %s, %s, 1)
        """,
        (name, email, phone, pwd_hash, city, area)
    )

    # 2. Insert into donors
    donor_id = db.execute_query(
        """
        INSERT INTO donors (user_id, name, age, gender, blood_group, phone, email, city, area, address, availability, last_donation_date, total_donations, is_active)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 0, 1)
        """,
        (user_id, name, age, gender, blood_group, phone, email, city, area, address, availability, last_donation_date)
    )

    token = generate_token(user_id, 'donor', email)
    return jsonify({
        'success': True,
        'message': 'Donor registered successfully! Thank you for choosing to save lives.',
        'token': token,
        'user': {
            'user_id': user_id,
            'donor_id': donor_id,
            'name': name,
            'email': email,
            'role': 'donor',
            'blood_group': blood_group,
            'availability': availability,
            'city': city,
            'area': area
        }
    }), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    """Authenticates user with email and password."""
    data = request.get_json() or {}
    email = sanitize_string(data.get('email')).lower()
    password = data.get('password', '')

    if not email or not password:
        return jsonify({'success': False, 'message': 'Please enter both email and password.'}), 400

    user = db.fetch_one("SELECT * FROM users WHERE LOWER(email) = %s", (email,))
    if not user or not check_password_hash(user['password_hash'], password):
        return jsonify({'success': False, 'message': 'Invalid email address or password.'}), 401

    if not user.get('is_active', 1):
        return jsonify({'success': False, 'message': 'Your account has been deactivated. Please contact support.'}), 403

    token = generate_token(user['user_id'], user['role'], user['email'])

    # Build response user object
    user_data = {
        'user_id': user['user_id'],
        'name': user['name'],
        'email': user['email'],
        'phone': user['phone'],
        'role': user['role'],
        'city': user.get('city'),
        'area': user.get('area')
    }

    if user['role'] == 'donor':
        donor = db.fetch_one("SELECT * FROM donors WHERE user_id = %s", (user['user_id'],))
        if donor:
            user_data['donor_id'] = donor.get('donor_id')
            user_data['blood_group'] = donor.get('blood_group')
            user_data['availability'] = donor.get('availability')
            user_data['last_donation_date'] = str(donor.get('last_donation_date')) if donor.get('last_donation_date') else None

    return jsonify({
        'success': True,
        'message': f"Welcome back, {user['name']}!",
        'token': token,
        'user': user_data
    }), 200


@auth_bp.route('/me', methods=['GET'])
def get_current_user_profile():
    """Returns currently authenticated user profile."""
    user = get_current_user()
    if not user:
        return jsonify({'success': False, 'message': 'Not authenticated'}), 401

    return jsonify({
        'success': True,
        'user': user
    }), 200


@auth_bp.route('/logout', methods=['POST'])
def logout():
    """Logs out user."""
    return jsonify({
        'success': True,
        'message': 'Logged out successfully.'
    }), 200


@auth_bp.route('/change-password', methods=['PUT'])
@login_required()
def change_password():
    """Allows authenticated user to update their password."""
    user = request.current_user
    data = request.get_json() or {}

    old_pwd = data.get('old_password', '')
    new_pwd = data.get('new_password', '')

    valid_pwd, pwd_msg = validate_password(new_pwd)
    if not valid_pwd:
        return jsonify({'success': False, 'message': pwd_msg}), 400

    # Retrieve current password hash
    current_record = db.fetch_one("SELECT password_hash FROM users WHERE user_id = %s", (user['user_id'],))
    if not current_record or not check_password_hash(current_record['password_hash'], old_pwd):
        return jsonify({'success': False, 'message': 'Incorrect current password.'}), 400

    new_hash = generate_password_hash(new_pwd)
    db.execute_query("UPDATE users SET password_hash = %s WHERE user_id = %s", (new_hash, user['user_id']))

    return jsonify({
        'success': True,
        'message': 'Password changed successfully.'
    }), 200
