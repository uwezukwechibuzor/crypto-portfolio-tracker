"""
Ethereum blockchain service for fetching wallet balances
"""
from typing import Dict, List, Optional, cast
from decimal import Decimal
from web3 import Web3
from web3.exceptions import Web3Exception
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential
from app.core.config import settings


class EthereumService:
    """Service for interacting with Ethereum blockchain"""
    
    def __init__(self):
        """Initialize Ethereum Web3 connection"""
        self.w3: Optional[Web3] = None
        self._connect()
    
    def _connect(self):
        """Establish connection to Ethereum RPC"""
        try:
            if not settings.ETHEREUM_RPC_URL:
                logger.warning("Ethereum RPC URL not configured")
                return
            
            self.w3 = Web3(Web3.HTTPProvider(
                settings.ETHEREUM_RPC_URL,
                request_kwargs={'timeout': settings.ETHEREUM_TIMEOUT}
            ))
            
            if self.w3.is_connected():
                logger.info(f"Connected to Ethereum network (Chain ID: {self.w3.eth.chain_id})")
            else:
                logger.error("Failed to connect to Ethereum network")
                self.w3 = None
        except Exception as e:
            logger.error(f"Error connecting to Ethereum: {e}")
            self.w3 = None
    
    def is_valid_address(self, address: str) -> bool:
        """
        Validate Ethereum address
        
        Args:
            address: Ethereum address to validate
            
        Returns:
            True if valid, False otherwise
        """
        # Validate address format without requiring connection
        return Web3.is_address(address)
    
    def checksum_address(self, address: str) -> str:
        """
        Convert address to checksum format
        
        Args:
            address: Ethereum address
            
        Returns:
            Checksummed address
        """
        # Checksum address without requiring connection
        return Web3.to_checksum_address(address)
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def get_eth_balance(self, address: str) -> Decimal:
        """
        Get ETH balance for an address
        
        Args:
            address: Ethereum address
            
        Returns:
            ETH balance as Decimal
        """
        if not self.w3:
            raise Exception("Ethereum RPC not configured. Please set ETHEREUM_RPC_URL in .env file. Get a free API key from Infura (https://infura.io) or Alchemy (https://alchemy.com)")
        
        try:
            checksum_addr = self.checksum_address(address)
            balance_wei = self.w3.eth.get_balance(checksum_addr)  # type: ignore
            balance_eth = Decimal(balance_wei) / Decimal(10**18)
            logger.debug(f"ETH balance for {address}: {balance_eth}")
            return balance_eth
        except Web3Exception as e:
            logger.error(f"Error fetching ETH balance for {address}: {e}")
            raise
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def get_erc20_balance(self, wallet_address: str, token_address: str, decimals: int = 18) -> Decimal:
        """
        Get ERC20 token balance for an address
        
        Args:
            wallet_address: Wallet address
            token_address: Token contract address
            decimals: Token decimals (default: 18)
            
        Returns:
            Token balance as Decimal
        """
        if not self.w3:
            raise Exception("Ethereum RPC not configured. Please set ETHEREUM_RPC_URL in .env file. Get a free API key from Infura (https://infura.io) or Alchemy (https://alchemy.com)")
        
        try:
            # ERC20 balanceOf ABI
            balance_of_abi = {
                "constant": True,
                "inputs": [{"name": "_owner", "type": "address"}],
                "name": "balanceOf",
                "outputs": [{"name": "balance", "type": "uint256"}],
                "type": "function"
            }
            
            checksum_wallet = self.checksum_address(wallet_address)
            checksum_token = self.checksum_address(token_address)
            
            contract = self.w3.eth.contract(address=cast("ChecksumAddress", checksum_token), abi=[balance_of_abi])  # type: ignore
            balance = contract.functions.balanceOf(checksum_wallet).call()
            
            balance_decimal = Decimal(balance) / Decimal(10**decimals)
            logger.debug(f"ERC20 balance for {wallet_address} (token: {token_address}): {balance_decimal}")
            return balance_decimal
        except Exception as e:
            logger.error(f"Error fetching ERC20 balance: {e}")
            raise
    
    def get_wallet_balances(self, address: str) -> Dict[str, Decimal]:
        """
        Get all balances for a wallet (ETH + common tokens)
        
        Args:
            address: Ethereum wallet address
            
        Returns:
            Dictionary of token symbols to balances
        """
        if not self.w3:
            raise Exception("Ethereum RPC not configured. Please set ETHEREUM_RPC_URL in .env file. Get a free API key from Infura (https://infura.io) or Alchemy (https://alchemy.com)")
        
        balances = {}
        
        try:
            # Get ETH balance
            eth_balance = self.get_eth_balance(address)
            if eth_balance > 0:
                balances["ETH"] = eth_balance
            
            # For production, you would fetch token balances here
            # This requires either:
            # 1. User-specified token list
            # 2. Integration with token discovery services (e.g., Alchemy, Etherscan)
            # 3. Indexer/subgraph queries
            
            logger.info(f"Fetched {len(balances)} balances for {address}")
            return balances
        except Exception as e:
            logger.error(f"Error fetching wallet balances for {address}: {e}")
            raise
    
    def get_block_number(self) -> int:
        """
        Get current block number
        
        Returns:
            Current block number
        """
        if not self.w3:
            raise Exception("Ethereum RPC not configured. Please set ETHEREUM_RPC_URL in .env file. Get a free API key from Infura (https://infura.io) or Alchemy (https://alchemy.com)")
        return self.w3.eth.block_number


# Global Ethereum service instance
ethereum_service = EthereumService()
