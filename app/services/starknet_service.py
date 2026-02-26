"""
Starknet blockchain service for fetching wallet balances
"""
from typing import Dict, Optional
from decimal import Decimal
import requests
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential
from app.core.config import settings


class StarknetService:
    """Service for interacting with Starknet blockchain"""
    
    def __init__(self):
        """Initialize Starknet service"""
        # RPC endpoint from config
        self.rpc_url = settings.STARKNET_RPC_URL
        self.timeout = settings.STARKNET_TIMEOUT
        
        # Native token info
        self.native_tokens = {
            "STRK": {"decimals": 18},  # Starknet token
            "ETH": {"decimals": 18},   # ETH on Starknet L2
        }
        
        # Token contract addresses on Starknet
        self.token_contracts = {
            "ETH": "0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7",
            "STRK": "0x04718f5a0fc34cc1af16a1cdee98ffb20c31f5cd61d6ab07201858f4287c938d",
            "USDC": "0x053c91253bc9682c04929ca02ed00b3e423f6710d2ee7e0d5ebb06f3ecf368a8",
            "USDT": "0x068f5c6a61780768455de69077e07e89787839bf8166decfbf92b645209c0fb8",
        }
    
    def is_valid_address(self, address: str) -> bool:
        """
        Validate Starknet address format
        
        Args:
            address: Starknet address to validate
            
        Returns:
            True if valid, False otherwise
        """
        # Starknet addresses start with 0x and are 66 characters (including 0x)
        if not address.startswith("0x"):
            return False
        
        # Check length (66 chars including 0x)
        if len(address) != 66:
            return False
        
        # Check if it's valid hex
        try:
            int(address, 16)
            return True
        except ValueError:
            return False
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def get_balance(self, address: str, token_contract: str) -> Decimal:
        """
        Get token balance for an address using Starknet RPC
        
        Args:
            address: Starknet address
            token_contract: Token contract address
            
        Returns:
            Token balance as Decimal
        """
        if not self.rpc_url:
            logger.warning("Starknet RPC URL not configured")
            return Decimal(0)
        
        try:
            # Call balanceOf function on the token contract
            payload = {
                "jsonrpc": "2.0",
                "method": "starknet_call",
                "params": [
                    {
                        "contract_address": token_contract,
                        "entry_point_selector": "0x2e4263afad30923c891518314c3c95dbe830a16874e8abc5777a9a20b54c76e",  # balanceOf selector
                        "calldata": [address]
                    },
                    "latest"
                ],
                "id": 1
            }
            
            response = requests.post(
                self.rpc_url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=self.timeout
            )
            response.raise_for_status()
            
            data = response.json()
            
            if "result" in data and len(data["result"]) > 0:
                # Starknet returns balance as an array [low, high] for uint256
                balance_low = int(data["result"][0], 16)
                balance_high = int(data["result"][1], 16) if len(data["result"]) > 1 else 0
                
                # Combine low and high parts
                balance_raw = balance_low + (balance_high << 128)
                
                # Convert to decimal (18 decimals for STRK and ETH)
                balance_decimal = Decimal(balance_raw) / Decimal(10 ** 18)
                
                logger.debug(f"Balance for {address} on contract {token_contract}: {balance_decimal}")
                return balance_decimal
            
            return Decimal(0)
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching Starknet balance for {address}: {e}")
            return Decimal(0)
        except Exception as e:
            logger.error(f"Unexpected error fetching Starknet balance: {e}")
            return Decimal(0)
    
    def get_wallet_balances(self, address: str) -> Dict[str, Decimal]:
        """
        Get all balances for a Starknet wallet
        
        Args:
            address: Starknet wallet address
            
        Returns:
            Dictionary of token symbols to balances
        """
        balances = {}
        
        if not self.rpc_url:
            logger.error("Starknet RPC URL not configured")
            return balances
        
        try:
            # Get balances for known tokens
            for token_symbol, contract_address in self.token_contracts.items():
                balance = self.get_balance(address, contract_address)
                if balance > 0:
                    balances[token_symbol] = balance
            
            logger.info(f"Fetched {len(balances)} token balances for {address} on Starknet")
            return balances
            
        except Exception as e:
            logger.error(f"Error fetching wallet balances for {address} on Starknet: {e}")
            raise


# Global Starknet service instance
starknet_service = StarknetService()
