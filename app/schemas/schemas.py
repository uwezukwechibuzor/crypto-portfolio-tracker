"""
Pydantic schemas for request/response validation
"""
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field, validator


class WalletCreate(BaseModel):
    """Schema for creating a wallet"""
    address: str = Field(..., min_length=1, max_length=255, description="Wallet address")
    chain: str = Field(..., description="Blockchain name (ethereum or solana)")
    label: Optional[str] = Field(None, max_length=255, description="Optional wallet label")
    
    @validator("chain")
    def validate_chain(cls, v):
        """Validate chain is supported"""
        supported_chains = ["ethereum", "solana"]
        if v.lower() not in supported_chains:
            raise ValueError(f"Chain must be one of: {', '.join(supported_chains)}")
        return v.lower()
    
    @validator("address")
    def validate_address(cls, v, values):
        """Basic address validation"""
        v = v.strip()
        if not v:
            raise ValueError("Address cannot be empty")
        return v


class WalletResponse(BaseModel):
    """Schema for wallet response"""
    id: str
    address: str
    chain: str
    label: Optional[str]
    created_at: str
    updated_at: str
    
    class Config:
        from_attributes = True


class BalanceResponse(BaseModel):
    """Schema for balance response"""
    id: str
    wallet_id: str
    token_symbol: str
    token_address: Optional[str]
    balance: str
    usd_value: Optional[str]
    last_updated: str
    
    class Config:
        from_attributes = True


class WalletWithBalances(BaseModel):
    """Schema for wallet with balances"""
    id: str
    address: str
    chain: str
    label: Optional[str]
    balances: List[BalanceResponse]
    total_usd_value: Optional[str]
    
    class Config:
        from_attributes = True


class PortfolioSummary(BaseModel):
    """Schema for portfolio summary"""
    total_wallets: int
    total_usd_value: str
    wallets: List[WalletWithBalances]


class BalanceHistoryResponse(BaseModel):
    """Schema for balance history"""
    id: str
    wallet_id: str
    token_symbol: str
    token_address: Optional[str]
    balance: str
    usd_value: Optional[str]
    recorded_at: str
    
    class Config:
        from_attributes = True


class FetchBalanceRequest(BaseModel):
    """Schema for fetching balances"""
    force_refresh: bool = Field(default=False, description="Force refresh from blockchain")


class HealthResponse(BaseModel):
    """Schema for health check response"""
    status: str
    version: str
    timestamp: str
    database: str
    redis: str


class ErrorResponse(BaseModel):
    """Schema for error response"""
    error: str
    message: str
    timestamp: str
