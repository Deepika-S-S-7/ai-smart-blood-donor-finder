"""
Data Validation Utilities
-------------------------
Provides rigorous frontend and backend validation for:
- User registration
- Donor registration
- Blood search & requests
- Password requirements
"""

import re
from datetime import datetime, date
from typing import Dict, Any, List, Tuple
from ..services.compatibility import is_valid_blood_group, normalize_blood_group

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')
PHONE_REGEX = re.compile(r'^[+]?[0-9]{10,15}$')


def sanitize_string(val: Any) -> str:
    """Strip whitespace and return clean string."""
    if val is None:
        return ""
    return str(val).strip()


def validate_email(email: str) -> bool:
    """Validate email address format."""
    if not email:
        return False
    return bool(EMAIL_REGEX.match(email.strip()))


def validate_phone(phone: str) -> bool:
    """Validate phone number format (10-15 digits, optional +)."""
    if not phone:
        return False
    cleaned = re.sub(r'[\s\-()]', '', phone.strip())
    return bool(PHONE_REGEX.match(cleaned))


def validate_blood_group(bg: str) -> bool:
    """Validate blood group against the 8 medical types."""
    return is_valid_blood_group(bg)


def validate_password(password: str) -> Tuple[bool, str]:
    """Validate password strength (at least 6 characters)."""
    if not password or len(password) < 6:
        return False, "Password must be at least 6 characters long."
    return True, ""


def validate_age(age: Any) -> Tuple[bool, str]:
    """Validate donor age (must be 18 - 65 for safe blood donation)."""
    try:
        age_int = int(age)
        if 18 <= age_int <= 65:
            return True, ""
        return False, "Donor age must be between 18 and 65 years for medical eligibility."
    except (ValueError, TypeError):
        return False, "Please enter a valid numeric age."


def validate_name(name: str, field_label: str = "Name") -> Tuple[bool, str]:
    """
    Validates that a name does not contain numbers and only contains letters, spaces, hyphens, and periods.
    """
    if not name or len(name.strip()) < 2:
        return False, f"{field_label} is required (minimum 2 characters)."
    if any(char.isdigit() for char in name):
        return False, f"Numbers are not allowed in {field_label.lower()}. Please enter letters only (no numbers)."
    if not re.match(r"^[a-zA-Z\s.'-]+$", name.strip()):
        return False, f"{field_label} should only contain alphabetic letters and spaces."
    return True, ""


def validate_registration_data(data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Validates general user registration payload."""
    errors: List[str] = []

    name = sanitize_string(data.get('name'))
    email = sanitize_string(data.get('email'))
    phone = sanitize_string(data.get('phone'))
    password = data.get('password', '')

    valid_name, name_err = validate_name(name, "Full name")
    if not valid_name:
        errors.append(name_err)

    if not validate_email(email):
        errors.append("Please provide a valid email address.")

    if not validate_phone(phone):
        errors.append("Please provide a valid 10 to 15 digit contact phone number.")

    valid_pwd, pwd_msg = validate_password(password)
    if not valid_pwd:
        errors.append(pwd_msg)

    return len(errors) == 0, errors


def validate_donor_data(data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Validates donor registration and profile update payload."""
    errors: List[str] = []

    # Basic user fields
    name = sanitize_string(data.get('name'))
    email = sanitize_string(data.get('email'))
    phone = sanitize_string(data.get('phone'))
    city = sanitize_string(data.get('city'))
    area = sanitize_string(data.get('area'))
    blood_group = sanitize_string(data.get('blood_group'))

    valid_name, name_err = validate_name(name, "Donor full name")
    if not valid_name:
        errors.append(name_err)

    if not validate_email(email):
        errors.append("Valid email address is required.")

    if not validate_phone(phone):
        errors.append("Valid contact phone number is required.")

    if not city:
        errors.append("City is required for location-based matching.")

    if not area:
        errors.append("Area / Neighborhood is required for location-based matching.")

    if not validate_blood_group(blood_group):
        errors.append("Valid blood group is required (A+, A-, B+, B-, AB+, AB-, O+, O-).")

    # Age check
    valid_age, age_msg = validate_age(data.get('age'))
    if not valid_age:
        errors.append(age_msg)

    # Last donation date check (if supplied)
    last_donation = data.get('last_donation_date')
    if last_donation:
        try:
            d_date = datetime.strptime(str(last_donation)[:10], "%Y-%m-%d").date()
            if d_date > date.today():
                errors.append("Last donation date cannot be in the future.")
        except Exception:
            errors.append("Invalid date format for last donation date. Use YYYY-MM-DD.")

    return len(errors) == 0, errors


def validate_blood_request_data(data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Validates blood request / emergency request payload."""
    errors: List[str] = []

    patient_name = sanitize_string(data.get('patient_name'))
    blood_group = sanitize_string(data.get('blood_group'))
    hospital_name = sanitize_string(data.get('hospital_name'))
    city = sanitize_string(data.get('city'))
    area = sanitize_string(data.get('area'))
    contact_number = sanitize_string(data.get('contact_number'))

    valid_pname, pname_err = validate_name(patient_name, "Patient name")
    if not valid_pname:
        errors.append(pname_err)

    if not validate_blood_group(blood_group):
        errors.append("Valid patient blood group is required.")

    if not hospital_name:
        errors.append("Hospital name is required.")

    if not city:
        errors.append("City is required.")

    if not area:
        errors.append("Area is required.")

    if not validate_phone(contact_number):
        errors.append("Valid emergency contact phone number is required.")

    units = data.get('required_units', 1)
    try:
        u_int = int(units)
        if u_int < 1 or u_int > 50:
            errors.append("Required units must be between 1 and 50.")
    except Exception:
        errors.append("Required units must be a positive integer.")

    return len(errors) == 0, errors
