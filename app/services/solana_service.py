"""
Solana blockchain service for fetching wallet balances
"""
from typing import Dict, Optional
from decimal import Decimal
from solana.rpc.api import Client
from solana.rpc.commitment import Confirmed
from solana.rpc.types import TokenAccountOpts
from solders.pubkey import Pubkey  # type: ignore
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential
from app.core.config import settings


class SolanaService:
    """Service for interacting with Solana blockchain"""
    
    # Solana lamports per SOL
    LAMPORTS_PER_SOL = 1_000_000_000
    
    def __init__(self):
        """Initialize Solana RPC connection"""
        self.client: Optional[Client] = None
        self._connect()
    
    def _connect(self):
        """Establish connection to Solana RPC"""
        try:
            if not settings.SOLANA_RPC_URL:
                logger.warning("Solana RPC URL not configured")
                return
            
            self.client = Client(
                settings.SOLANA_RPC_URL,
                commitment=Confirmed,
                timeout=settings.SOLANA_TIMEOUT
            )
            
            # Test connection
            version = self.client.get_version()
            if version.value:
                logger.info(f"Connected to Solana network (Version: {version.value})")
            else:
                logger.error("Failed to connect to Solana network")
                self.client = None
        except Exception as e:
            logger.error(f"Error connecting to Solana: {e}")
            self.client = None
    
    def is_valid_address(self, address: str) -> bool:
        """
        Validate Solana address
        
        Args:
            address: Solana address to validate
            
        Returns:
            True if valid, False otherwise
        """
        try:
            Pubkey.from_string(address)
            return True
        except Exception:
            return False
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def get_sol_balance(self, address: str) -> Decimal:
        """
        Get SOL balance for an address
        
        Args:
            address: Solana address
            
        Returns:
            SOL balance as Decimal
        """
        if not self.client:
            raise Exception("Solana service not connected")
        
        try:
            pubkey = Pubkey.from_string(address)
            response = self.client.get_balance(pubkey)
            
            if response.value is not None:
                balance_lamports = response.value
                balance_sol = Decimal(balance_lamports) / Decimal(self.LAMPORTS_PER_SOL)
                logger.debug(f"SOL balance for {address}: {balance_sol}")
                return balance_sol
            else:
                logger.warning(f"No balance returned for {address}")
                return Decimal(0)
        except Exception as e:
            logger.error(f"Error fetching SOL balance for {address}: {e}")
            raise
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def get_token_accounts(self, address: str) -> Dict[str, Decimal]:
        """
        Get SPL token balances for an address
        
        Args:
            address: Solana wallet address
            
        Returns:
            Dictionary of token mint addresses to balances
        """
        if not self.client:
            raise Exception("Solana service not connected")
        
        token_balances = {}
        
        try:
            pubkey = Pubkey.from_string(address)
            
            # Get token accounts owned by this wallet
            # Note: Token program ID is hardcoded for now
            token_program_id = Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA")
            opts = TokenAccountOpts(program_id=token_program_id)
            response = self.client.get_token_accounts_by_owner(pubkey, opts)
            
            if response.value:
                for account in response.value:
                    try:
                        # Parse token account data
                        # Note: In production, you'd parse the account data properly
                        # and map mint addresses to token symbols
                        pass
                    except Exception as e:
                        logger.debug(f"Error parsing token account: {e}")
                        continue
            
            logger.info(f"Fetched {len(token_balances)} token balances for {address}")
            return token_balances
        except Exception as e:
            logger.error(f"Error fetching token accounts for {address}: {e}")
            raise
    
    def get_wallet_balances(self, address: str) -> Dict[str, Decimal]:
        """
        Get all balances for a wallet (SOL + SPL tokens)
        
        Args:
            address: Solana wallet address
            
        Returns:
            Dictionary of token symbols to balances
        """
        if not self.client:
            raise Exception("Solana service not connected")
        
        balances = {}
        
        try:
            # Get SOL balance
            sol_balance = self.get_sol_balance(address)
            if sol_balance > 0:
                balances["SOL"] = sol_balance
            
            # Get SPL token balances
            token_balances = self.get_token_accounts(address)
            balances.update(token_balances)
            
            logger.info(f"Fetched {len(balances)} balances for {address}")
            return balances
        except Exception as e:
            logger.error(f"Error fetching wallet balances for {address}: {e}")
            raise
    
    def get_slot(self) -> int:
        """
        Get current slot
        
        Returns:
            Current slot number
        """
        if not self.client:
            raise Exception("Solana service not connected")
        response = self.client.get_slot()
        return response.value if response.value else 0


# Global Solana service instance
solana_service = SolanaService()
