"""
Flask Application Entrypoint & Factory
--------------------------------------
Serves REST API endpoints and static frontend client.
Provides CORS, error handling, database verification,
and health-check diagnostics.
"""

import os
import sys
from pathlib import Path

# Ensure project root is in sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from flask import Flask, send_from_directory, jsonify, request
from flask_cors import CORS

from backend.config import Config
from backend.routes import auth_bp, donor_bp, search_bp, request_bp, admin_bp
from backend import database as db


def create_app():
    """Application factory for Flask backend."""
    app = Flask(
        __name__,
        static_folder=str(Config.FRONTEND_DIR),
        static_url_path=''
    )

    app.config.from_object(Config)

    # Enable CORS
    CORS(app, resources={r"/api/*": {"origins": Config.CORS_ORIGINS}}, supports_credentials=True)

    # Register API Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(donor_bp)
    app.register_blueprint(search_bp)
    app.register_blueprint(request_bp)
    app.register_blueprint(admin_bp)

    # Database auto-check / setup
    with app.app_context():
        try:
            # Quick check if tables exist
            db.fetch_one("SELECT 1 FROM users LIMIT 1")
        except Exception:
            # Auto initialize DB if needed
            from backend.init_db import main as run_init
            run_init()

    # ------------------------------------------------------
    # System Diagnostics & Health Check
    # ------------------------------------------------------
    @app.route('/api/health', methods=['GET'])
    def health_check():
        db_type = db.get_current_db_type()
        mysql_online = db.is_mysql_available()
        return jsonify({
            'status': 'healthy',
            'service': 'AI-Based Smart Blood Donor Finder',
            'database_engine': db_type,
            'mysql_server_online': mysql_online,
            'version': '1.0.0-academic'
        }), 200

    # ------------------------------------------------------
    # Static Frontend Page Serving
    # ------------------------------------------------------
    @app.route('/', methods=['GET'])
    def serve_home():
        return send_from_directory(Config.FRONTEND_DIR, 'index.html')

    @app.route('/<path:filename>', methods=['GET'])
    def serve_frontend_files(filename):
        target_path = Path(Config.FRONTEND_DIR) / filename
        if target_path.exists() and target_path.is_file():
            return send_from_directory(Config.FRONTEND_DIR, filename)

        # Allow URL without .html extension (e.g. /search -> search.html)
        html_candidate = Path(Config.FRONTEND_DIR) / f"{filename}.html"
        if html_candidate.exists() and html_candidate.is_file():
            return send_from_directory(Config.FRONTEND_DIR, f"{filename}.html")

        # If requesting an API route that didn't match, return 404 JSON
        if filename.startswith('api/'):
            return jsonify({'success': False, 'message': 'API endpoint not found'}), 404

        # Fallback to index.html
        return send_from_directory(Config.FRONTEND_DIR, 'index.html')

    # ------------------------------------------------------
    # Global Error Handlers (JSON for API, readable)
    # ------------------------------------------------------
    @app.errorhandler(404)
    def not_found(e):
        if request.path.startswith('/api/'):
            return jsonify({'success': False, 'message': 'Resource not found'}), 404
        return send_from_directory(Config.FRONTEND_DIR, 'index.html'), 404

    @app.errorhandler(500)
    def server_error(e):
        return jsonify({'success': False, 'message': 'An internal server error occurred. Please try again later.'}), 500

    @app.errorhandler(400)
    def bad_request(e):
        return jsonify({'success': False, 'message': 'Bad request'}), 400

    return app


app = create_app()

if __name__ == '__main__':
    print(f"[*] Starting AI-Based Smart Blood Donor Finder on http://localhost:{Config.PORT}")
    print(f"[*] Database mode: {db.get_current_db_type()}")
    app.run(host='0.0.0.0', port=Config.PORT, debug=Config.DEBUG)
