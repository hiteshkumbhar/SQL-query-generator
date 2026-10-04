"""Flask application factory."""

import os
from flask import Flask, jsonify, render_template
from app.routes.sql_routes import sql_bp


def create_app(config_class):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    template_folder = os.path.abspath(os.path.join(base_dir, "..", "templates"))
    static_folder = os.path.abspath(os.path.join(base_dir, "..", "static"))

    app = Flask(
        __name__,
        template_folder=template_folder,
        static_folder=static_folder,
    )

    app.config.from_object(config_class)

    # Register Blueprints
    app.register_blueprint(sql_bp, url_prefix="/api")

    # Serve Main Application UI
    @app.route("/")
    def index():
        return render_template("index.html")

    # Global Error Handlers
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": "BAD_REQUEST",
            "message": getattr(error, "description", "Bad request.")
        }), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": "NOT_FOUND",
            "message": "The requested resource was not found."
        }), 404

    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({
            "success": False,
            "error": "METHOD_NOT_ALLOWED",
            "message": "HTTP method not allowed."
        }), 405

    @app.errorhandler(413)
    def request_entity_too_large(error):
        return jsonify({
            "success": False,
            "error": "PAYLOAD_TOO_LARGE",
            "message": "Request payload exceeds maximum allowed size."
        }), 413

    @app.errorhandler(429)
    def too_many_requests(error):
        return jsonify({
            "success": False,
            "error": "RATE_LIMIT_EXCEEDED",
            "message": "Too many requests. Please slow down."
        }), 429

    @app.errorhandler(500)
    def internal_server_error(error):
        return jsonify({
            "success": False,
            "error": "INTERNAL_SERVER_ERROR",
            "message": "An internal error occurred. Please try again later."
        }), 500

    return app
