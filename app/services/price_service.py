"""
Price service for fetching cryptocurrency prices
"""
from typing import Dict, Optional
from decimal import Decimal
import requests
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential
from app.db.redis_cache import cache


class PriceService:
    """Service for fetching cryptocurrency prices"""
    
    COINGECKO_API = "https://api.coingecko.com/api/v3"
    
    # Map token symbols to CoinGecko IDs
    TOKEN_MAP = {
        "ETH": "ethereum",
        "BTC": "bitcoin",
        "SOL": "solana",
        "USDC": "usd-coin",
        "USDT": "tether",
        "DAI": "dai",
        "WETH": "weth",
        "WBTC": "wrapped-bitcoin",
    }
    
    @staticmethod
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def get_price(token_symbol: str) -> Optional[Decimal]:
        """
        Get current USD price for a token
        
        Args:
            token_symbol: Token symbol (ETH, BTC, SOL, etc.)
            
        Returns:
            Price in USD as Decimal, or None if not found
        """
        # Check cache first (5 minute TTL)
        cache_key = f"price:{token_symbol}:usd"
        cached_price = cache.get(cache_key)
        if cached_price:
            logger.debug(f"Returning cached price for {token_symbol}: ${cached_price}")
            return Decimal(str(cached_price))
        
        try:
            # Get CoinGecko ID for token
            coingecko_id = PriceService.TOKEN_MAP.get(token_symbol.upper())
            if not coingecko_id:
                logger.warning(f"No CoinGecko mapping for token: {token_symbol}")
                return None
            
            # Fetch price from CoinGecko
            url = f"{PriceService.COINGECKO_API}/simple/price"
            params = {
                "ids": coingecko_id,
                "vs_currencies": "usd"
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            price = data.get(coingecko_id, {}).get("usd")
            
            if price:
                price_decimal = Decimal(str(price))
                # Cache for 5 minutes
                cache.set(cache_key, float(price), ttl=300)
                logger.debug(f"Fetched price for {token_symbol}: ${price}")
                return price_decimal
            else:
                logger.warning(f"No price data for {token_symbol}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching price for {token_symbol}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error fetching price for {token_symbol}: {e}")
            return None
    
    @staticmethod
    def get_prices(token_symbols: list[str]) -> Dict[str, Optional[Decimal]]:
        """
        Get prices for multiple tokens (batch request)
        
        Args:
            token_symbols: List of token symbols
            
        Returns:
            Dictionary mapping symbols to prices
        """
        # Get CoinGecko IDs
        coingecko_ids = []
        symbol_to_id = {}
        
        for symbol in token_symbols:
            coingecko_id = PriceService.TOKEN_MAP.get(symbol.upper())
            if coingecko_id:
                coingecko_ids.append(coingecko_id)
                symbol_to_id[coingecko_id] = symbol.upper()
        
        if not coingecko_ids:
            return {symbol: None for symbol in token_symbols}
        
        try:
            # Batch fetch from CoinGecko
            url = f"{PriceService.COINGECKO_API}/simple/price"
            params = {
                "ids": ",".join(coingecko_ids),
                "vs_currencies": "usd"
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Build result dictionary
            result = {}
            for coingecko_id, symbol in symbol_to_id.items():
                price = data.get(coingecko_id, {}).get("usd")
                if price:
                    result[symbol] = Decimal(str(price))
                    # Cache each price
                    cache_key = f"price:{symbol}:usd"
                    cache.set(cache_key, float(price), ttl=300)
                else:
                    result[symbol] = None
            
            # Add None for unmapped symbols
            for symbol in token_symbols:
                if symbol.upper() not in result:
                    result[symbol.upper()] = None
            
            logger.info(f"Fetched prices for {len(result)} tokens")
            return result
            
        except Exception as e:
            logger.error(f"Error fetching batch prices: {e}")
            return {symbol: None for symbol in token_symbols}


# Global price service instance
price_service = PriceService()
