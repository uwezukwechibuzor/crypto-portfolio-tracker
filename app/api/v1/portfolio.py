"""
Portfolio API endpoints
"""
from flask import Blueprint, request, jsonify
from loguru import logger

from app.db.database import get_db_context
from app.services.wallet_service import WalletService

portfolio_bp = Blueprint('portfolio', __name__, url_prefix='/portfolio')


@portfolio_bp.route('', methods=['GET'])
def get_portfolio():
    """
    Get complete portfolio summary
    
    Returns:
        200: Portfolio summary with all wallets and total value
        500: Server error
    """
    try:
        with get_db_context() as db:
            portfolio = WalletService.get_portfolio_summary(db)
            
            return jsonify({
                "status": "success",
                "data": portfolio
            }), 200
    except Exception as e:
        logger.error(f"Error fetching portfolio: {e}")
        return jsonify({
            "status": "error",
            "message": "Internal server error"
        }), 500


@portfolio_bp.route('/history', methods=['GET'])
def get_portfolio_history():
    """
    Get portfolio balance history
    
    Query Parameters:
        wallet_id: Optional wallet filter
        token_symbol: Optional token filter
        limit: Maximum number of records (default: 100)
    
    Returns:
        200: Balance history records
        500: Server error
    """
    try:
        wallet_id = request.args.get('wallet_id')
        token_symbol = request.args.get('token_symbol')
        limit = int(request.args.get('limit', 100))
        
        if not wallet_id:
            return jsonify({
                "status": "error",
                "message": "wallet_id is required"
            }), 400
        
        with get_db_context() as db:
            history = WalletService.get_balance_history(
                db=db,
                wallet_id=wallet_id,
                token_symbol=token_symbol,
                limit=limit
            )
            
            return jsonify({
                "status": "success",
                "data": [record.to_dict() for record in history],
                "count": len(history)
            }), 200
    except ValueError as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 400
    except Exception as e:
        logger.error(f"Error fetching portfolio history: {e}")
        return jsonify({
            "status": "error",
            "message": "Internal server error"
        }), 500
