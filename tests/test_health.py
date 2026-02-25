"""
Test health endpoints
"""


def test_health_check(client):
    """Test health check endpoint"""
    response = client.get('/api/v1/health')
    assert response.status_code in [200, 503]
    data = response.get_json()
    assert 'status' in data
    assert 'version' in data


def test_readiness_check(client):
    """Test readiness check endpoint"""
    response = client.get('/api/v1/ready')
    assert response.status_code in [200, 503]
    data = response.get_json()
    assert 'status' in data


def test_liveness_check(client):
    """Test liveness check endpoint"""
    response = client.get('/api/v1/live')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'alive'


def test_root_endpoint(client):
    """Test root endpoint"""
    response = client.get('/')
    assert response.status_code == 200
    data = response.get_json()
    assert 'name' in data
    assert 'version' in data
    assert data['status'] == 'running'
