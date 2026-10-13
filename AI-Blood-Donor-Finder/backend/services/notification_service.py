"""
Notification & Activity Logging Service
---------------------------------------
Provides in-app notifications and logging for emergency broadcasts,
seeker blood requests, and donor response status updates.
"""

from datetime import datetime
from typing import Dict, Any, List

# In-memory session notifications buffer (in addition to database audit logs)
_recent_alerts: List[Dict[str, Any]] = []


def record_notification(title: str, message: str, alert_type: str = "info", user_id: int = None) -> Dict[str, Any]:
    """Records an in-app notification event."""
    alert = {
        'id': len(_recent_alerts) + 1,
        'title': title,
        'message': message,
        'alert_type': alert_type,  # emergency, success, warning, info
        'user_id': user_id,
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    _recent_alerts.insert(0, alert)
    if len(_recent_alerts) > 50:
        _recent_alerts.pop()
    return alert


def get_recent_alerts(limit: int = 10, user_id: int = None) -> List[Dict[str, Any]]:
    """Fetches recent notification events."""
    if user_id:
        filtered = [a for a in _recent_alerts if a['user_id'] == user_id or a['user_id'] is None]
        return filtered[:limit]
    return _recent_alerts[:limit]
