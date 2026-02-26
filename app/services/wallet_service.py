"""
Wallet service for managing wallet operations
"""
from typing import List, Optional, Dict
from datetime import datetime
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from loguru import logger

from app.models.models import Wallet, Balance, BalanceHistory
from app.services.ethereum_service import ethereum_service
from app.services.solana_service import solana_service
from app.services.coingecko_price_service import coingecko_price_service
from app.db.redis_cache import cache


class WalletService:
    """Service for wallet management and balance tracking"""
    
    @staticmethod
    def create_wallet(db: Session, address: str, chain: str, label: Optional[str] = None) -> Wallet:
        """
        Create a new wallet
        
        Args:
            db: Database session
            address: Wallet address
            chain: Blockchain name
            label: Optional wallet label
            
        Returns:
            Created wallet
        """
        # Validate address based on chain
        if chain == "ethereum":
            if not ethereum_service.is_valid_address(address):
                raise ValueError("Invalid Ethereum address")
            address = ethereum_service.checksum_address(address)
        elif chain == "solana":
            if not solana_service.is_valid_address(address):
                raise ValueError("Invalid Solana address")
        else:
            raise ValueError(f"Unsupported chain: {chain}")
        
        try:
            wallet = Wallet(address=address, chain=chain, label=label)
            db.add(wallet)
            db.commit()
            db.refresh(wallet)
            
            logger.info(f"Created wallet: {wallet.id} ({chain}: {address})")
            return wallet
        except IntegrityError:
            db.rollback()
            raise ValueError(f"Wallet already exists for address {address} on {chain}")
    
    @staticmethod
    def get_wallet(db: Session, wallet_id: str) -> Optional[Wallet]:
        """
        Get wallet by ID
        
        Args:
            db: Database session
            wallet_id: Wallet UUID
            
        Returns:
            Wallet or None
        """
        return db.query(Wallet).filter(Wallet.id == wallet_id).first()
    
    @staticmethod
    def get_all_wallets(db: Session) -> List[Wallet]:
        """
        Get all wallets
        
        Args:
            db: Database session
            
        Returns:
            List of wallets
        """
        return db.query(Wallet).all()
    
    @staticmethod
    def delete_wallet(db: Session, wallet_id: str) -> bool:
        """
        Delete a wallet
        
        Args:
            db: Database session
            wallet_id: Wallet UUID
            
        Returns:
            True if deleted, False if not found
        """
        wallet = db.query(Wallet).filter(Wallet.id == wallet_id).first()
        if not wallet:
            return False
        
        # Clear cache
        cache.delete(f"wallet:{wallet_id}:balances")
        
        db.delete(wallet)
        db.commit()
        logger.info(f"Deleted wallet: {wallet_id}")
        return True
    
    @staticmethod
    def fetch_and_store_balances(
        db: Session, 
        wallet_id: str, 
        force_refresh: bool = False
    ) -> List[Balance]:
        """
        Fetch balances from blockchain and store in database
        
        Args:
            db: Database session
            wallet_id: Wallet UUID
            force_refresh: Force refresh from blockchain
            
        Returns:
            List of balances
        """
        wallet = WalletService.get_wallet(db, wallet_id)
        if not wallet:
            raise ValueError(f"Wallet not found: {wallet_id}")
        
        # Check cache first
        cache_key = f"wallet:{wallet_id}:balances"
        if not force_refresh:
            cached_balances = cache.get(cache_key)
            if cached_balances:
                logger.debug(f"Returning cached balances for wallet {wallet_id}")
                return db.query(Balance).filter(Balance.wallet_id == wallet_id).all()
        
        try:
            # Fetch balances from blockchain
            if wallet.chain == "ethereum":  # type: ignore
                token_balances = ethereum_service.get_wallet_balances(wallet.address)  # type: ignore
            elif wallet.chain == "solana":  # type: ignore
                token_balances = solana_service.get_wallet_balances(wallet.address)  # type: ignore
            else:
                raise ValueError(f"Unsupported chain: {wallet.chain}")
            
            # Store balances in database
            stored_balances = []
            for token_symbol, balance in token_balances.items():
                # Get USD price for token
                usd_price = coingecko_price_service.get_price(token_symbol)
                usd_value = None
                if usd_price:
                    usd_value = balance * usd_price
                
                # Update or create balance
                existing_balance = db.query(Balance).filter(
                    Balance.wallet_id == wallet_id,
                    Balance.token_symbol == token_symbol,
                    Balance.token_address == None
                ).first()
                
                if existing_balance:
                    existing_balance.balance = balance  # type: ignore
                    existing_balance.usd_value = usd_value  # type: ignore
                    existing_balance.last_updated = datetime.utcnow()  # type: ignore
                    balance_obj = existing_balance
                else:
                    balance_obj = Balance(
                        wallet_id=wallet_id,
                        token_symbol=token_symbol,
                        balance=balance,
                        usd_value=usd_value,
                        last_updated=datetime.utcnow()
                    )
                    db.add(balance_obj)
                
                stored_balances.append(balance_obj)
                
                # Store in history
                history = BalanceHistory(
                    wallet_id=wallet_id,
                    token_symbol=token_symbol,
                    balance=balance,
                    usd_value=usd_value,
                    recorded_at=datetime.utcnow()
                )
                db.add(history)
            
            db.commit()
            
            # Update cache
            cache.set(cache_key, True, ttl=300)  # 5 minutes
            
            logger.info(f"Stored {len(stored_balances)} balances for wallet {wallet_id}")
            return stored_balances
        except Exception as e:
            db.rollback()
            logger.error(f"Error fetching balances for wallet {wallet_id}: {e}")
            raise
    
    @staticmethod
    def get_wallet_balances(db: Session, wallet_id: str) -> List[Balance]:
        """
        Get stored balances for a wallet
        
        Args:
            db: Database session
            wallet_id: Wallet UUID
            
        Returns:
            List of balances
        """
        return db.query(Balance).filter(Balance.wallet_id == wallet_id).all()
    
    @staticmethod
    def get_portfolio_summary(db: Session) -> Dict:
        """
        Get portfolio summary with all wallets and total value
        
        Args:
            db: Database session
            
        Returns:
            Portfolio summary dictionary
        """
        wallets = WalletService.get_all_wallets(db)
        total_usd_value = Decimal(0)
        wallet_data = []
        
        for wallet in wallets:
            balances = WalletService.get_wallet_balances(db, str(wallet.id))
            wallet_usd_value = sum(
                (Decimal(b.usd_value) if b.usd_value is not None else Decimal(0))  # type: ignore
                for b in balances
            )
            total_usd_value += wallet_usd_value
            
            wallet_data.append({
                "id": str(wallet.id),
                "address": wallet.address,
                "chain": wallet.chain,
                "label": wallet.label,
                "balances": [b.to_dict() for b in balances],
                "total_usd_value": str(wallet_usd_value)
            })
        
        return {
            "total_wallets": len(wallets),
            "total_usd_value": str(total_usd_value),
            "wallets": wallet_data
        }
    
    @staticmethod
    def get_balance_history(
        db: Session, 
        wallet_id: str, 
        token_symbol: Optional[str] = None,
        limit: int = 100
    ) -> List[BalanceHistory]:
        """
        Get balance history for a wallet
        
        Args:
            db: Database session
            wallet_id: Wallet UUID
            token_symbol: Optional token symbol filter
            limit: Maximum number of records
            
        Returns:
            List of balance history records
        """
        query = db.query(BalanceHistory).filter(BalanceHistory.wallet_id == wallet_id)
        
        if token_symbol:
            query = query.filter(BalanceHistory.token_symbol == token_symbol)
        
        return query.order_by(BalanceHistory.recorded_at.desc()).limit(limit).all()
