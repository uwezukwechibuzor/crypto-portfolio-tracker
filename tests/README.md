# Testing Guide

## Running Tests

The test suite is configured to run with minimal dependencies using in-memory SQLite and mocked external services.

### Quick Start

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_health.py -v

# Run with coverage
pytest tests/ -v --cov=app --cov-report=html
```

### Test Requirements

Tests use:
- **SQLite in-memory database** - No PostgreSQL required
- **Mocked Redis** - No Redis server required
- **Mocked blockchain services** - No RPC endpoints required

This allows tests to run anywhere without external dependencies.

## Test Structure

```
tests/
├── conftest.py          # Fixtures and configuration
├── test_health.py       # Health check endpoint tests
└── test_wallets.py      # Wallet API tests
```

## Writing Tests

### Example Test

```python
def test_example(client):
    """Test example endpoint"""
    response = client.get('/api/v1/endpoint')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'success'
```

### Test Fixtures

- `app` - Flask application instance with test configuration
- `client` - Test client for making HTTP requests

## CI/CD Integration

Tests are designed to run in CI/CD pipelines without external services:

```yaml
# Example GitHub Actions
- name: Run tests
  run: pytest tests/ -v --cov=app
```

## Note on Database Tests

The tests use SQLite instead of PostgreSQL for simplicity. For testing with PostgreSQL:

1. Start PostgreSQL:
   ```bash
   docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=postgres postgres:15
   ```

2. Set environment variable:
   ```bash
   export DATABASE_URL="postgresql://postgres:postgres@localhost:5432/test_db"
   ```

3. Run tests:
   ```bash
   pytest tests/ -v
   ```

## Known Issues

- Tests requiring actual blockchain interaction should mock the services
- Redis operations are mocked (cache will not actually work in tests)
- For integration tests with real databases, use Docker Compose

## Example: Running with Docker

```bash
# Start test environment
docker-compose -f docker-compose.test.yml up -d

# Run tests
docker-compose -f docker-compose.test.yml exec app pytest tests/ -v

# Stop environment
docker-compose -f docker-compose.test.yml down
```
