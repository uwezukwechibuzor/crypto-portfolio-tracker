"""
API v1 Blueprint registration
"""
from flask import Blueprint
from app.api.v1.wallets import wallet_bp
from app.api.v1.portfolio import portfolio_bp
from app.api.v1.health import health_bp

# Create main v1 blueprint
api_v1 = Blueprint('api_v1', __name__, url_prefix='/api/v1')

# Register sub-blueprints
api_v1.register_blueprint(wallet_bp)
api_v1.register_blueprint(portfolio_bp)
api_v1.register_blueprint(health_bp)

__all__ = ['api_v1']
