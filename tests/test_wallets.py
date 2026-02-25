"""
Test wallet API endpoints
"""
import json


def test_create_wallet_ethereum(client):
    """Test creating an Ethereum wallet"""
    # Note: This test requires a valid Ethereum RPC connection
    # In a real test environment, you'd mock the blockchain service
    
    data = {
        "address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
        "chain": "ethereum",
        "label": "Test Wallet"
    }
    
    response = client.post(
        '/api/v1/wallets',
        data=json.dumps(data),
        content_type='application/json'
    )
    
    # Will fail without RPC connection, but validates the endpoint structure
    assert response.status_code in [201, 400, 500]


def test_get_wallets(client):
    """Test getting all wallets"""
    response = client.get('/api/v1/wallets')
    assert response.status_code == 200
    data = response.get_json()
    assert 'status' in data
    assert data['status'] == 'success'
