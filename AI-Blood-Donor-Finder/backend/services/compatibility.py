"""
Medical Red Blood Cell (RBC) Compatibility Service
---------------------------------------------------
Implements strict rule-based red blood cell antigen compatibility.
Used by the AI-Based Smart Blood Donor Finder to ensure INCOMPATIBLE
donors are NEVER recommended to recipients.

NOTE: This system serves as an academic intelligent matching aid and
does not replace clinical cross-matching or blood bank lab tests.
"""

from typing import List, Dict, Set

# Strict Red Blood Cell (RBC) Compatibility Matrix
# Key = Recipient Blood Group
# Value = Set of Donor Blood Groups that the recipient can safely receive from
RBC_RECIPIENT_COMPATIBILITY: Dict[str, Set[str]] = {
    'A+': {'A+', 'A-', 'O+', 'O-'},
    'A-': {'A-', 'O-'},
    'B+': {'B+', 'B-', 'O+', 'O-'},
    'B-': {'B-', 'O-'},
    'AB+': {'A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'},  # Universal Recipient
    'AB-': {'AB-', 'A-', 'B-', 'O-'},
    'O+': {'O+', 'O-'},
    'O-': {'O-'}  # Can only receive O-
}

# Derived Donor Matrix: Key = Donor Blood Group, Value = Set of Recipients donor can give to
RBC_DONOR_COMPATIBILITY: Dict[str, Set[str]] = {
    'O-': {'O-', 'O+', 'A-', 'A+', 'B-', 'B+', 'AB-', 'AB+'},  # Universal Donor
    'O+': {'O+', 'A+', 'B+', 'AB+'},
    'A-': {'A-', 'A+', 'AB-', 'AB+'},
    'A+': {'A+', 'AB+'},
    'B-': {'B-', 'B+', 'AB-', 'AB+'},
    'B+': {'B+', 'AB+'},
    'AB-': {'AB-', 'AB+'},
    'AB+': {'AB+'}
}

ALL_BLOOD_GROUPS = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']


def normalize_blood_group(bg: str) -> str:
    """Normalize blood group string (strip spaces, uppercase)."""
    if not bg:
        return ''
    cleaned = bg.strip().upper().replace('POSITIVE', '+').replace('NEGATIVE', '-')
    return cleaned


def is_valid_blood_group(bg: str) -> bool:
    """Check if blood group is one of the standard 8 types."""
    return normalize_blood_group(bg) in RBC_RECIPIENT_COMPATIBILITY


def is_compatible(donor_bg: str, recipient_bg: str) -> bool:
    """
    Check if a donor blood group is compatible for a recipient.
    Returns True ONLY if clinically compatible for red blood cells.
    """
    d_norm = normalize_blood_group(donor_bg)
    r_norm = normalize_blood_group(recipient_bg)

    if not is_valid_blood_group(d_norm) or not is_valid_blood_group(r_norm):
        return False

    return d_norm in RBC_RECIPIENT_COMPATIBILITY.get(r_norm, set())


def get_compatible_donor_groups(recipient_bg: str) -> List[str]:
    """
    Get list of all donor blood groups compatible with the recipient.
    """
    r_norm = normalize_blood_group(recipient_bg)
    if not is_valid_blood_group(r_norm):
        return []
    return sorted(list(RBC_RECIPIENT_COMPATIBILITY.get(r_norm, set())))


def get_compatible_recipient_groups(donor_bg: str) -> List[str]:
    """
    Get list of all recipient blood groups that this donor can give to.
    """
    d_norm = normalize_blood_group(donor_bg)
    if not is_valid_blood_group(d_norm):
        return []
    return sorted(list(RBC_DONOR_COMPATIBILITY.get(d_norm, set())))
