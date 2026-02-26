"""
Cosmos blockchain service for fetching wallet balances
"""
from typing import Dict, Optional
from decimal import Decimal
import requests
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential
from app.core.config import settings


class CosmosService:
    """Service for interacting with Cosmos-based blockchains"""
    
    def __init__(self):
        """Initialize Cosmos service"""
        # RPC endpoints from config
        self.rpcs = {
            "cosmos": settings.COSMOS_RPC_URL,
            "celestia": settings.CELESTIA_RPC_URL,
        }
        
        # Timeouts from config
        self.timeouts = {
            "cosmos": settings.COSMOS_TIMEOUT,
            "celestia": settings.CELESTIA_TIMEOUT,
        }
        
        # Native token info
        self.native_tokens = {
            "cosmos": {"symbol": "ATOM", "decimals": 6},
            "celestia": {"symbol": "TIA", "decimals": 6},
        }
    
    def is_valid_address(self, address: str, chain: str) -> bool:
        """
        Validate Cosmos address format
        
        Args:
            address: Cosmos address to validate
            chain: Chain name (cosmos or celestia)
            
        Returns:
            True if valid, False otherwise
        """
        # Cosmos addresses start with chain-specific prefix
        prefixes = {
            "cosmos": "cosmos",
            "celestia": "celestia"
        }
        
        prefix = prefixes.get(chain)
        if not prefix:
            return False
        
        # Basic validation: starts with prefix and has correct length
        if not address.startswith(prefix):
            return False
        
        # Cosmos addresses are typically 39-50 characters (including prefix)
        # Examples: cosmos1... (45 chars), celestia1... (49 chars)
        # TODO: use the right function to validate the address
        if len(address) < 39 or len(address) > 65:
            return False
        
        return True
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def get_all_balances(self, address: str, chain: str) -> Dict[str, Decimal]:
        """
        Get all token balances for an address (native + IBC tokens)
        
        Args:
            address: Cosmos address
            chain: Chain name (cosmos or celestia)
            
        Returns:
            Dictionary mapping token identifiers to balances
        """
        rpc_url = self.rpcs.get(chain)
        if not rpc_url:
            raise Exception(f"Unsupported Cosmos chain: {chain}")
        
        timeout = self.timeouts.get(chain, 30)
        
        try:
            # Query all balances from Cosmos REST API
            url = f"{rpc_url}/cosmos/bank/v1beta1/balances/{address}"
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()
            
            data = response.json()
            balances_data = data.get("balances", [])
            
            token_info = self.native_tokens.get(chain)
            if not token_info:
                return {}
            
            # Native token denoms
            denoms = {
                "cosmos": "uatom",  # micro ATOM
                "celestia": "utia"  # micro TIA
            }
            native_denom = denoms.get(chain)
            
            result = {}
            
            for balance in balances_data:
                denom = balance.get("denom", "")
                amount = balance.get("amount", "0")
                
                if not denom or not amount:
                    continue
                
                # Handle native token with proper symbol
                if denom == native_denom:
                    # Convert from micro units (1 ATOM = 1,000,000 uatom)
                    balance_decimal = Decimal(amount) / Decimal(10 ** token_info["decimals"])
                    result[token_info["symbol"]] = balance_decimal
                    logger.debug(f"{token_info['symbol']} balance for {address}: {balance_decimal}")
                
                # Handle IBC tokens - use full denom as identifier
                elif denom.startswith("ibc/"):
                    # For IBC tokens, we don't know the decimals, assume 6 as standard
                    balance_decimal = Decimal(amount) / Decimal(10 ** 6)
                    result[denom] = balance_decimal
                    logger.debug(f"{denom} balance for {address}: {balance_decimal}")
                
                # Handle other tokens
                else:
                    # Use the denom as-is, assume 6 decimals
                    balance_decimal = Decimal(amount) / Decimal(10 ** 6)
                    result[denom] = balance_decimal
                    logger.debug(f"{denom} balance for {address}: {balance_decimal}")
            
            return result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching {chain} balances for {address}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error fetching {chain} balances: {e}")
            raise
    
    def get_wallet_balances(self, address: str, chain: str) -> Dict[str, Decimal]:
        """
        Get all balances for a wallet (native + IBC tokens)
        
        Args:
            address: Cosmos wallet address
            chain: Chain name (cosmos or celestia)
            
        Returns:
            Dictionary of token identifiers to balances
        """
        try:
            balances = self.get_all_balances(address, chain)
            logger.info(f"Fetched {len(balances)} token balances for {address} on {chain}")
            return balances
            
        except Exception as e:
            logger.error(f"Error fetching wallet balances for {address} on {chain}: {e}")
            raise


# Global Cosmos service instance
cosmos_service = CosmosService()
