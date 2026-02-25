"""
Database models for the crypto portfolio tracker
"""
import uuid
from datetime import datetime
from decimal import Decimal
from sqlalchemy import Column, String, DateTime, Numeric, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.types import TypeDecorator, CHAR

Base = declarative_base()


class UUID(TypeDecorator):
    """
    Platform-independent UUID type.
    Uses PostgreSQL's UUID type, otherwise uses CHAR(36), storing as stringified hex values.
    """
    impl = CHAR
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(PG_UUID(as_uuid=True))
        else:
            return dialect.type_descriptor(CHAR(36))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return str(value) if not isinstance(value, uuid.UUID) else value
        else:
            if not isinstance(value, uuid.UUID):
                return str(uuid.UUID(value))
            else:
                return str(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        if not isinstance(value, uuid.UUID):
            return uuid.UUID(value)
        return value


class Wallet(Base):
    """
    Wallet model for storing blockchain wallet addresses
    """
    __tablename__ = "wallets"
    
    id = Column(UUID(), primary_key=True, default=uuid.uuid4)
    address = Column(String(255), nullable=False, index=True)
    chain = Column(String(50), nullable=False)  # 'ethereum' or 'solana'
    label = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    balances = relationship("Balance", back_populates="wallet", cascade="all, delete-orphan")
    balance_history = relationship("BalanceHistory", back_populates="wallet", cascade="all, delete-orphan")
    
    # Unique constraint on address and chain
    __table_args__ = (
        UniqueConstraint('address', 'chain', name='uix_wallet_address_chain'),
    )
    
    def __repr__(self):
        return f"<Wallet(id={self.id}, address={self.address}, chain={self.chain})>"
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            "id": str(self.id),
            "address": self.address,
            "chain": self.chain,
            "label": self.label,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class Balance(Base):
    """
    Balance model for storing current wallet balances
    """
    __tablename__ = "balances"
    
    id = Column(UUID(), primary_key=True, default=uuid.uuid4)
    wallet_id = Column(UUID(), ForeignKey("wallets.id", ondelete="CASCADE"), nullable=False)
    token_symbol = Column(String(50), nullable=False)  # 'ETH', 'SOL', 'USDC', etc.
    token_address = Column(String(255), nullable=True)  # NULL for native tokens
    balance = Column(Numeric(36, 18), nullable=False, default=0)
    usd_value = Column(Numeric(20, 2), nullable=True)
    last_updated = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    wallet = relationship("Wallet", back_populates="balances")
    
    # Unique constraint
    __table_args__ = (
        UniqueConstraint('wallet_id', 'token_symbol', 'token_address', name='uix_balance_wallet_token'),
    )
    
    def __repr__(self):
        return f"<Balance(wallet_id={self.wallet_id}, token={self.token_symbol}, balance={self.balance})>"
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            "id": str(self.id),
            "wallet_id": str(self.wallet_id),
            "token_symbol": self.token_symbol,
            "token_address": self.token_address,
            "balance": str(self.balance),
            "usd_value": str(self.usd_value) if self.usd_value else None,
            "last_updated": self.last_updated.isoformat() if self.last_updated else None,
        }


class BalanceHistory(Base):
    """
    Balance history model for tracking balance changes over time
    """
    __tablename__ = "balance_history"
    
    id = Column(UUID(), primary_key=True, default=uuid.uuid4)
    wallet_id = Column(UUID(), ForeignKey("wallets.id", ondelete="CASCADE"), nullable=False)
    token_symbol = Column(String(50), nullable=False)
    token_address = Column(String(255), nullable=True)
    balance = Column(Numeric(36, 18), nullable=False, default=0)
    usd_value = Column(Numeric(20, 2), nullable=True)
    recorded_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Relationships
    wallet = relationship("Wallet", back_populates="balance_history")
    
    def __repr__(self):
        return f"<BalanceHistory(wallet_id={self.wallet_id}, token={self.token_symbol}, recorded_at={self.recorded_at})>"
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            "id": str(self.id),
            "wallet_id": str(self.wallet_id),
            "token_symbol": self.token_symbol,
            "token_address": self.token_address,
            "balance": str(self.balance),
            "usd_value": str(self.usd_value) if self.usd_value else None,
            "recorded_at": self.recorded_at.isoformat() if self.recorded_at else None,
        }
