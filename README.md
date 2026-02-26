# Crypto Portfolio Tracker

A production-ready cryptocurrency portfolio tracker supporting Ethereum, Solana, Cosmos Hub, and Celestia blockchains. Built with Flask, PostgreSQL, and Redis.

![Architecture](https://img.shields.io/badge/Architecture-Microservices-blue)
![Python](https://img.shields.io/badge/Python-3.11+-green)
![Flask](https://img.shields.io/badge/Flask-3.0+-lightgrey)
![License](https://img.shields.io/badge/License-MIT-yellow)

## Features

✅ **Multi-Chain Support**
- Ethereum (ETH and ERC-20 tokens)
- Solana (SOL and SPL tokens)
- Cosmos Hub (ATOM)
- Celestia (TIA)

✅ **Core Functionality**
- Add and manage wallet addresses
- Fetch real-time balances from blockchain
- USD price tracking with CoinGecko integration
- Store and track balance history
- RESTful API for portfolio access
- Real-time portfolio aggregation

✅ **Production-Ready**
- Docker containerization
- PostgreSQL for data persistence
- Redis caching for performance
- Structured logging with Loguru
- Rate limiting and CORS protection
- Health check endpoints
- Database migrations with Alembic

## Architecture

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed system design.

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │
┌──────▼──────────┐
│   Flask API     │
│  (REST Endpoints)│
└──────┬──────────┘
       │
┌──────▼──────────┐     ┌──────────────┐
│  Service Layer  │────▶│  Blockchain  │
│  (Business Logic)│     │   Adapters   │
└──────┬──────────┘     └──────────────┘
       │
┌──────▼──────────┐     ┌──────────────┐
│   PostgreSQL    │     │    Redis     │
│   (Persistence) │     │   (Cache)    │
└─────────────────┘     └──────────────┘
```

## Technology Stack

- **Backend**: Flask 3.0, Python 3.11+
- **Database**: PostgreSQL 15
- **Cache**: Redis 7
- **Blockchain**: Web3.py (Ethereum), Solana.py (Solana), Cosmos REST APIs
- **Validation**: Pydantic
- **Migrations**: Alembic
- **Logging**: Loguru
- **Deployment**: Docker, Docker Compose, Gunicorn

## Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- Docker & Docker Compose (for containerized deployment)

### Option 1: Docker Deployment (Recommended)

1. **Clone the repository**
```bash
git clone <repository-url>
cd crypto-portfolio-tracker
```

2. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env and add your RPC URLs
```

3. **Start all services**
```bash
docker-compose up -d
```

4. **Check health**
```bash
curl http://localhost:5000/api/v1/health
```

The API will be available at `http://localhost:5000`

### Option 2: Local Development

1. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set up environment**
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. **Start PostgreSQL and Redis**
```bash
# Using Docker
docker run -d --name postgres -p 5432:5432 -e POSTGRES_PASSWORD=postgres postgres:15-alpine
docker run -d --name redis -p 6379:6379 redis:7-alpine
```

5. **Run database migrations**
```bash
alembic upgrade head
```

6. **Start the application**
```bash
python app/main.py
# Or with Flask CLI
flask run --host=0.0.0.0 --port=5000
```

## API Documentation

### Base URL
```
http://localhost:5000/api/v1
```

### Endpoints

#### 1. Health Check
```bash
GET /api/v1/health
```

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2024-02-25T10:30:00",
  "database": "connected",
  "redis": "connected"
}
```

#### 2. Create Wallet
```bash
POST /api/v1/wallets
Content-Type: application/json

{
  "address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
  "chain": "ethereum",
  "label": "My Main Wallet"
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "id": "uuid-here",
    "address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
    "chain": "ethereum",
    "label": "My Main Wallet",
    "created_at": "2024-02-25T10:30:00",
    "updated_at": "2024-02-25T10:30:00"
  }
}
```

#### 3. Get All Wallets
```bash
GET /api/v1/wallets
```

#### 4. Get Wallet by ID
```bash
GET /api/v1/wallets/{wallet_id}
```

#### 5. Delete Wallet
```bash
DELETE /api/v1/wallets/{wallet_id}
```

#### 6. Fetch Wallet Balances
```bash
POST /api/v1/wallets/{wallet_id}/fetch
Content-Type: application/json

{
  "force_refresh": false
}
```

**Response:**
```json
{
  "status": "success",
  "data": [
    {
      "id": "uuid-here",
      "wallet_id": "wallet-uuid",
      "token_symbol": "ETH",
      "token_address": null,
      "balance": "1.234567890123456789",
      "usd_value": "2500.00",
      "last_updated": "2024-02-25T10:30:00"
    }
  ],
  "count": 1
}
```

#### 7. Get Wallet Balances
```bash
GET /api/v1/wallets/{wallet_id}/balances
```

#### 8. Get Portfolio Summary
```bash
GET /api/v1/portfolio
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "total_wallets": 2,
    "total_usd_value": "5000.00",
    "wallets": [
      {
        "id": "uuid-here",
        "address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
        "chain": "ethereum",
        "label": "My Main Wallet",
        "balances": [...],
        "total_usd_value": "2500.00"
      }
    ]
  }
}
```

#### 9. Get Balance History
```bash
GET /api/v1/portfolio/history?wallet_id={wallet_id}&token_symbol=ETH&limit=100
```

## Configuration

### Environment Variables

See `.env.example` for all available configuration options.

**Required:**
- `ETHEREUM_RPC_URL` - Your Ethereum RPC endpoint (Infura, Alchemy, etc.)
- `SOLANA_RPC_URL` - Solana RPC endpoint (default: public mainnet)
- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_URL` - Redis connection string

**Optional:**
- `RATE_LIMIT_REQUESTS` - Rate limit per period (default: 100)
- `RATE_LIMIT_PERIOD` - Rate limit period in seconds (default: 60)
- `CACHE_TTL` - Cache time-to-live in seconds (default: 300)
- `LOG_LEVEL` - Logging level (default: INFO)

## Database Schema

### Wallets Table
- `id` (UUID, PK)
- `address` (VARCHAR)
- `chain` (VARCHAR)
- `label` (VARCHAR, nullable)
- `created_at` (TIMESTAMP)
- `updated_at` (TIMESTAMP)

### Balances Table
- `id` (UUID, PK)
- `wallet_id` (UUID, FK)
- `token_symbol` (VARCHAR)
- `token_address` (VARCHAR, nullable)
- `balance` (NUMERIC)
- `usd_value` (NUMERIC, nullable)
- `last_updated` (TIMESTAMP)

### Balance History Table
- `id` (UUID, PK)
- `wallet_id` (UUID, FK)
- `token_symbol` (VARCHAR)
- `token_address` (VARCHAR, nullable)
- `balance` (NUMERIC)
- `usd_value` (NUMERIC, nullable)
- `recorded_at` (TIMESTAMP)

## Development

### Running Tests
```bash
pytest tests/ -v --cov=app
```

### Code Formatting
```bash
black app/
flake8 app/
```

### Database Migrations
```bash
# Create new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

### Development Mode with Docker
```bash
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up
```

## Production Deployment

### Docker Deployment

1. **Build image**
```bash
docker build -t crypto-portfolio-tracker:latest .
```

2. **Deploy with docker-compose**
```bash
docker-compose up -d
```

3. **Check logs**
```bash
docker-compose logs -f app
```

### Manual Deployment

1. Install dependencies
2. Configure environment variables
3. Run migrations: `alembic upgrade head`
4. Start with Gunicorn:
```bash
gunicorn --bind 0.0.0.0:5000 --workers 4 --timeout 120 app.main:app
```

### Health Checks

The application provides three health check endpoints:

- `/api/v1/health` - Overall health (database, Redis)
- `/api/v1/ready` - Readiness check (for K8s)
- `/api/v1/live` - Liveness check (for K8s)

## Monitoring

### Logs

Logs are stored in the `logs/` directory:
- `app.log` - All application logs
- `error.log` - Error-level logs only

### Metrics

The application includes structured logging for monitoring:
- Request/response times
- Error rates
- Cache hit/miss rates
- Blockchain RPC call metrics

## Security Considerations

✅ Input validation with Pydantic
✅ Rate limiting on all endpoints
✅ CORS protection
✅ SQL injection protection (SQLAlchemy ORM)
✅ Environment-based secrets
✅ Connection pooling
✅ Retry logic with exponential backoff

## Troubleshooting

### Database Connection Issues
```bash
# Check PostgreSQL is running
docker ps | grep postgres

# Test connection
psql -h localhost -U postgres -d crypto_portfolio
```

### Redis Connection Issues
```bash
# Check Redis is running
docker ps | grep redis

# Test connection
redis-cli ping
```

### Blockchain RPC Issues
- Ensure your RPC URLs are correct in `.env`
- Check rate limits on your RPC provider
- Verify network connectivity

## Roadmap

- [ ] Support for additional chains (Polygon, BSC, Bitcoin)
- [ ] Real-time price feeds integration
- [ ] WebSocket support for live updates
- [ ] Token discovery and automatic detection
- [ ] Multi-user support with authentication
- [ ] Portfolio analytics and charts
- [ ] Webhook notifications
- [ ] Mobile app integration

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Support

For issues, questions, or contributions, please open an issue on GitHub.
