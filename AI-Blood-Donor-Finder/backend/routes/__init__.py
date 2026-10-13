from .auth_routes import auth_bp
from .donor_routes import donor_bp
from .search_routes import search_bp
from .request_routes import request_bp
from .admin_routes import admin_bp

__all__ = [
    'auth_bp',
    'donor_bp',
    'search_bp',
    'request_bp',
    'admin_bp'
]
