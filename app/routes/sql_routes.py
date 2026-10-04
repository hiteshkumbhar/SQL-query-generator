"""API routes for Text-to-SQL generation."""

from flask import Blueprint, current_app, jsonify, request
from app.extensions import rate_limiter
from app.services.gemini_service import GeminiAuthError, GeminiRateLimitError, GeminiService, GeminiServiceError
from app.services.sql_generation_service import SQLGenerationService
from app.validators.request_validator import ValidationError, validate_generate_sql_request

sql_bp = Blueprint("sql", __name__)

@sql_bp.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "service": "text-to-sql",
    }), 200


@sql_bp.route("/schema/default", methods=["GET"])
def get_default_schema():
    """Return default schema and supported dialects for UI initialization."""
    config = current_app.config
    return jsonify({
        "default_schema": config.get("DEFAULT_SCHEMA", ""),
        "allowed_dialects": sorted(list(config.get("ALLOWED_DIALECTS", []))),
        "default_dialect": config.get("DEFAULT_DIALECT", "postgresql"),
    }), 200


@sql_bp.route("/generate-sql", methods=["POST"])
def generate_sql():
    """Generate SQL query from natural language request."""
    # Apply basic rate limiting by IP
    client_ip = request.remote_addr or "127.0.0.1"
    if not rate_limiter.is_allowed(client_ip):
        return jsonify({
            "success": False,
            "error": "RATE_LIMIT_EXCEEDED",
            "message": "Too many requests. Please wait a moment before trying again."
        }), 429

    # Enforce JSON content type
    if not request.is_json:
        return jsonify({
            "success": False,
            "error": "INVALID_CONTENT_TYPE",
            "message": "Request content type must be application/json."
        }), 400

    data = request.get_json(silent=True)
    if data is None:
        return jsonify({
            "success": False,
            "error": "MALFORMED_JSON",
            "message": "Malformed JSON payload in request body."
        }), 400

    # 1. Validation
    try:
        prompt, schema, dialect = validate_generate_sql_request(data, current_app.config)
    except ValidationError as err:
        return jsonify({
            "success": False,
            "error": "VALIDATION_ERROR",
            "message": err.message,
        }), err.status_code

    # 2. Service execution
    api_key = current_app.config.get("GEMINI_API_KEY", "")
    model_name = current_app.config.get("GEMINI_MODEL", "gemini-3.8-flash")

    gemini_svc = GeminiService(api_key=api_key, model_name=model_name)
    sql_svc = SQLGenerationService(gemini_service=gemini_svc)

    try:
        result = sql_svc.generate_sql(prompt=prompt, schema=schema, dialect=dialect)
        return jsonify(result), 200

    except GeminiAuthError as auth_err:
        return jsonify({
            "success": False,
            "error": "AUTH_ERROR",
            "message": "Gemini API credentials error. Please verify server configuration."
        }), 401

    except GeminiRateLimitError as rate_err:
        return jsonify({
            "success": False,
            "error": "GEMINI_RATE_LIMIT",
            "message": "Gemini API rate limit reached. Please wait a few moments and try again."
        }), 429

    except GeminiServiceError as svc_err:
        return jsonify({
            "success": False,
            "error": "AI_SERVICE_ERROR",
            "message": svc_err.message or "Failed to generate SQL query from AI provider."
        }), 500

    except Exception as exc:
        return jsonify({
            "success": False,
            "error": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected error occurred while processing your request."
        }), 500
