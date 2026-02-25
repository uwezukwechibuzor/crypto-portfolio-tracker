"""
Test configuration and fixtures
"""
import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Set test environment
os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
os.environ['REDIS_URL'] = 'redis://fake-redis:6379/0'
os.environ['ETHEREUM_RPC_URL'] = ''
os.environ['SOLANA_RPC_URL'] = ''
os.environ['RATE_LIMIT_ENABLED'] = 'false'

from app.main import create_app
from app.models.models import Base


@pytest.fixture
def app():
    """Create application for testing"""
    app = create_app()
    app.config['TESTING'] = True
    
    # Create in-memory SQLite database for tests
    from app.db.database import engine
    Base.metadata.create_all(bind=engine)
    
    yield app
    
    # Cleanup
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()
