"""
Wallet API endpoints
"""
from flask import Blueprint, request, jsonify
from pydantic import ValidationError
from loguru import logger

from app.db.database import get_db_context
from app.services.wallet_service import WalletService
from app.schemas.schemas import WalletCreate, FetchBalanceRequest

wallet_bp = Blueprint('wallets', __name__, url_prefix='/wallets')


@wallet_bp.route('', methods=['POST'])
def create_wallet():
    """
    Create a new wallet
    
    Request Body:
        {
            "address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
            "chain": "ethereum",
            "label": "My Main Wallet"
        }
    
    Returns:
        201: Wallet created successfully
        400: Invalid request
        500: Server error
    """
    try:
        # Validate request
        data = request.get_json()
        wallet_data = WalletCreate(**data)
        
        # Create wallet
        with get_db_context() as db:
            wallet = WalletService.create_wallet(
                db=db,
                address=wallet_data.address,
                chain=wallet_data.chain,
                label=wallet_data.label
            )
            
            return jsonify({
                "status": "success",
                "data": wallet.to_dict()
            }), 201
    except ValidationError as e:
        return jsonify({
            "status": "error",
            "message": "Validation error",
            "errors": e.errors()
        }), 400
    except ValueError as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 400
    except Exception as e:
        logger.error(f"Error creating wallet: {e}")
        return jsonify({
            "status": "error",
            "message": "Internal server error"
        }), 500


@wallet_bp.route('', methods=['GET'])
def get_wallets():
    """
    Get all wallets
    
    Returns:
        200: List of wallets
        500: Server error
    """
    try:
        with get_db_context() as db:
            wallets = WalletService.get_all_wallets(db)
            
            return jsonify({
                "status": "success",
                "data": [wallet.to_dict() for wallet in wallets],
                "count": len(wallets)
            }), 200
    except Exception as e:
        logger.error(f"Error fetching wallets: {e}")
        return jsonify({
            "status": "error",
            "message": "Internal server error"
        }), 500


@wallet_bp.route('/<wallet_id>', methods=['GET'])
def get_wallet(wallet_id):
    """
    Get wallet by ID
    
    Args:
        wallet_id: Wallet UUID
    
    Returns:
        200: Wallet details
        404: Wallet not found
        500: Server error
    """
    try:
        with get_db_context() as db:
            wallet = WalletService.get_wallet(db, wallet_id)
            
            if not wallet:
                return jsonify({
                    "status": "error",
                    "message": "Wallet not found"
                }), 404
            
            return jsonify({
                "status": "success",
                "data": wallet.to_dict()
            }), 200
    except Exception as e:
        logger.error(f"Error fetching wallet {wallet_id}: {e}")
        return jsonify({
            "status": "error",
            "message": "Internal server error"
        }), 500


@wallet_bp.route('/<wallet_id>', methods=['DELETE'])
def delete_wallet(wallet_id):
    """
    Delete a wallet
    
    Args:
        wallet_id: Wallet UUID
    
    Returns:
        200: Wallet deleted
        404: Wallet not found
        500: Server error
    """
    try:
        with get_db_context() as db:
            deleted = WalletService.delete_wallet(db, wallet_id)
            
            if not deleted:
                return jsonify({
                    "status": "error",
                    "message": "Wallet not found"
                }), 404
            
            return jsonify({
                "status": "success",
                "message": "Wallet deleted successfully"
            }), 200
    except Exception as e:
        logger.error(f"Error deleting wallet {wallet_id}: {e}")
        return jsonify({
            "status": "error",
            "message": "Internal server error"
        }), 500


@wallet_bp.route('/<wallet_id>/fetch', methods=['POST'])
def fetch_balances(wallet_id):
    """
    Fetch and update wallet balances from blockchain
    
    Args:
        wallet_id: Wallet UUID
    
    Request Body:
        {
            "force_refresh": false
        }
    
    Returns:
        200: Balances fetched successfully
        404: Wallet not found
        500: Server error
    """
    try:
        data = request.get_json() or {}
        fetch_request = FetchBalanceRequest(**data)
        
        with get_db_context() as db:
            balances = WalletService.fetch_and_store_balances(
                db=db,
                wallet_id=wallet_id,
                force_refresh=fetch_request.force_refresh
            )
            
            return jsonify({
                "status": "success",
                "data": [balance.to_dict() for balance in balances],
                "count": len(balances)
            }), 200
    except ValueError as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 404
    except Exception as e:
        logger.error(f"Error fetching balances for wallet {wallet_id}: {e}")
        return jsonify({
            "status": "error",
            "message": "Internal server error"
        }), 500


@wallet_bp.route('/<wallet_id>/balances', methods=['GET'])
def get_balances(wallet_id):
    """
    Get stored balances for a wallet
    
    Args:
        wallet_id: Wallet UUID
    
    Returns:
        200: List of balances
        500: Server error
    """
    try:
        with get_db_context() as db:
            balances = WalletService.get_wallet_balances(db, wallet_id)
            
            return jsonify({
                "status": "success",
                "data": [balance.to_dict() for balance in balances],
                "count": len(balances)
            }), 200
    except Exception as e:
        logger.error(f"Error fetching balances for wallet {wallet_id}: {e}")
        return jsonify({
            "status": "error",
            "message": "Internal server error"
        }), 500
