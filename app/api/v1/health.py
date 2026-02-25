"""
Health check and system status endpoints
"""
from flask import Blueprint, jsonify
from datetime import datetime
from loguru import logger

from app.core.config import settings
from app.db.database import engine
from app.db.redis_cache import cache

health_bp = Blueprint('health', __name__)


@health_bp.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint
    
    Returns:
        200: Service is healthy
        503: Service is unhealthy
    """
    health_status = {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "timestamp": datetime.utcnow().isoformat(),
        "environment": settings.ENVIRONMENT
    }
    
    # Check database
    try:
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        health_status["database"] = "connected"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        health_status["database"] = "disconnected"
        health_status["status"] = "unhealthy"
    
    # Check Redis
    try:
        if cache.redis_client:
            cache.redis_client.ping()
            health_status["redis"] = "connected"
        else:
            health_status["redis"] = "disconnected"
    except Exception as e:
        logger.error(f"Redis health check failed: {e}")
        health_status["redis"] = "disconnected"
    
    status_code = 200 if health_status["status"] == "healthy" else 503
    return jsonify(health_status), status_code


@health_bp.route('/ready', methods=['GET'])
def readiness_check():
    """
    Readiness check for Kubernetes/orchestration
    
    Returns:
        200: Service is ready
        503: Service is not ready
    """
    try:
        # Check database connection
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        
        return jsonify({
            "status": "ready",
            "timestamp": datetime.utcnow().isoformat()
        }), 200
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        return jsonify({
            "status": "not_ready",
            "timestamp": datetime.utcnow().isoformat()
        }), 503


@health_bp.route('/live', methods=['GET'])
def liveness_check():
    """
    Liveness check for Kubernetes/orchestration
    
    Returns:
        200: Service is alive
    """
    return jsonify({
        "status": "alive",
        "timestamp": datetime.utcnow().isoformat()
    }), 200
