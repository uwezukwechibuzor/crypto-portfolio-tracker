"""
Flask application factory and configuration
"""
import os
from flask import Flask, jsonify
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from loguru import logger

from app.core.config import settings
from app.utils.logging import setup_logging
from app.db.database import init_db
from app.api.v1 import api_v1


def create_app() -> Flask:
    """
    Application factory for creating Flask app instance
    
    Returns:
        Flask: Configured Flask application
    """
    # Setup logging first
    os.makedirs("logs", exist_ok=True)
    setup_logging()
    
    # Create Flask app
    app = Flask(__name__)
    
    # Configure app
    app.config['JSON_SORT_KEYS'] = False
    app.config['SECRET_KEY'] = settings.API_KEY or 'dev-secret-key'
    
    # Setup CORS
    CORS(app, origins=settings.get_cors_origins())
    
    # Setup rate limiting
    if settings.RATE_LIMIT_ENABLED:
        limiter = Limiter(
            app=app,
            key_func=get_remote_address,
            default_limits=[f"{settings.RATE_LIMIT_REQUESTS} per {settings.RATE_LIMIT_PERIOD} seconds"],
            storage_uri=settings.REDIS_URL,
        )
        logger.info("Rate limiting enabled")
    
    # Register blueprints
    app.register_blueprint(api_v1)
    
    # Register error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "status": "error",
            "message": "Resource not found",
            "code": 404
        }), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"Internal server error: {error}")
        return jsonify({
            "status": "error",
            "message": "Internal server error",
            "code": 500
        }), 500
    
    @app.errorhandler(429)
    def rate_limit_exceeded(error):
        return jsonify({
            "status": "error",
            "message": "Rate limit exceeded",
            "code": 429
        }), 429
    
    # Root endpoint
    @app.route('/')
    def index():
        return jsonify({
            "name": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "status": "running",
            "docs": "/api/v1/health"
        })
    
    # Initialize database on startup
    with app.app_context():
        try:
            init_db()
            logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
    
    logger.info(f"{settings.APP_NAME} v{settings.APP_VERSION} started in {settings.ENVIRONMENT} mode")
    
    return app


# Create application instance
app = create_app()


if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=settings.DEBUG
    )
