# Crypto Portfolio Tracker - System Architecture

## Overview
A production-ready cryptocurrency portfolio tracker supporting Ethereum and Solana chains, built with Python Flask, PostgreSQL, and Redis caching.

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         CLIENT LAYER                         │
│                    (REST API Consumers)                      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     API GATEWAY LAYER                        │
│                      (Flask + Uvicorn)                     │
│  ┌──────────────┬─────────────────┬──────────────────────┐  │
│  │  Wallet API  │  Portfolio API  │  Health/Metrics API  │  │
│  └──────────────┴─────────────────┴──────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     SERVICE LAYER                            │
│  ┌────────────────────┬──────────────────────────────────┐  │
│  │  Wallet Service    │  Portfolio Service               │  │
│  │  - Add wallets     │  - Calculate totals              │  │
│  │  - Validate addrs  │  - Aggregate balances            │  │
│  │  - Fetch balances  │  - Historical tracking           │  │
│  └────────────────────┴──────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
                    ┌─────────┴─────────┐
                    ▼                   ▼
┌───────────────────────────┐  ┌──────────────────────────────┐
│  BLOCKCHAIN ADAPTER LAYER │  │      CACHE LAYER             │
│  ┌─────────┬────────────┐ │  │      (Redis)                 │
│  │Ethereum │   Solana   │ │  │  - Balance caching           │
│  │Adapter  │   Adapter  │ │  │  - Rate limiting             │
│  │(Web3)   │   (Solana) │ │  │  - Session management        │
│  └─────────┴────────────┘ │  └──────────────────────────────┘
└───────────────────────────┘
         │         │
         ▼         ▼
┌─────────────────────────────────────────────────────────────┐
│              EXTERNAL BLOCKCHAIN RPCS                        │
│  ┌─────────────────────┬──────────────────────────────────┐ │
│  │  Ethereum RPC       │  Solana RPC                      │ │
│  │  (Infura/Alchemy)   │  (Solana Mainnet/QuickNode)      │ │
│  └─────────────────────┴──────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     DATA PERSISTENCE LAYER                   │
│                      (PostgreSQL)                            │
│  ┌────────────┬──────────────┬────────────────────────────┐ │
│  │  Wallets   │  Balances    │  Balance History           │ │
│  │  Table     │  Table       │  Table                     │ │
│  └────────────┴──────────────┴────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## Technology Stack

### Backend Framework
- **Flask**: Modern, high-performance web framework
- **Uvicorn**: ASGI server for production
- **Pydantic**: Data validation and settings management

### Database
- **PostgreSQL**: Primary data store
- **SQLAlchemy**: ORM for database operations
- **Alembic**: Database migrations

### Caching
- **Redis**: For caching balances and rate limiting

### Blockchain Integrations
- **Web3.py**: Ethereum blockchain interaction
- **Solana.py**: Solana blockchain interaction

### Production Features
- **Loguru**: Advanced logging
- **Prometheus**: Metrics and monitoring
- **Docker**: Containerization
- **Nginx**: Reverse proxy (optional)

## Data Models

### 1. Wallets Table
```sql
CREATE TABLE wallets (
    id UUID PRIMARY KEY,
    address VARCHAR(255) NOT NULL,
    chain VARCHAR(50) NOT NULL,  -- 'ethereum' or 'solana'
    label VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(address, chain)
);
```

### 2. Balances Table
```sql
CREATE TABLE balances (
    id UUID PRIMARY KEY,
    wallet_id UUID REFERENCES wallets(id),
    token_symbol VARCHAR(50) NOT NULL,  -- 'ETH', 'SOL', 'USDC', etc.
    token_address VARCHAR(255),  -- NULL for native tokens
    balance NUMERIC(36, 18) NOT NULL,
    usd_value NUMERIC(20, 2),
    last_updated TIMESTAMP DEFAULT NOW(),
    UNIQUE(wallet_id, token_symbol, token_address)
);
```

### 3. Balance History Table
```sql
CREATE TABLE balance_history (
    id UUID PRIMARY KEY,
    wallet_id UUID REFERENCES wallets(id),
    token_symbol VARCHAR(50) NOT NULL,
    balance NUMERIC(36, 18) NOT NULL,
    usd_value NUMERIC(20, 2),
    recorded_at TIMESTAMP DEFAULT NOW()
);
```

## API Endpoints

### Wallet Management
- `POST /api/v1/wallets` - Add a new wallet
- `GET /api/v1/wallets` - List all wallets
- `GET /api/v1/wallets/{wallet_id}` - Get wallet details
- `DELETE /api/v1/wallets/{wallet_id}` - Remove a wallet

### Balance Operations
- `POST /api/v1/wallets/{wallet_id}/fetch` - Fetch and update balances
- `GET /api/v1/wallets/{wallet_id}/balances` - Get wallet balances
- `GET /api/v1/portfolio` - Get entire portfolio summary
- `GET /api/v1/portfolio/history` - Get historical portfolio data

### System
- `GET /api/v1/health` - Health check
- `GET /api/v1/metrics` - Prometheus metrics

## Security Considerations

1. **Input Validation**: All inputs validated using Pydantic
2. **Rate Limiting**: Redis-based rate limiting on API endpoints
3. **CORS**: Configurable CORS policies
4. **Environment Variables**: Sensitive data in environment variables
5. **API Keys**: Optional API key authentication
6. **SQL Injection**: Protected via SQLAlchemy ORM

## Scalability Features

1. **Connection Pooling**: PostgreSQL and Redis connection pools
2. **Async Operations**: Async/await for I/O operations
3. **Caching Strategy**: Multi-level caching (Redis + in-memory)
4. **Background Tasks**: Celery for scheduled balance updates (optional)
5. **Horizontal Scaling**: Stateless API design

## Error Handling

1. **Structured Logging**: JSON-formatted logs
2. **Exception Middleware**: Global exception handling
3. **Retry Logic**: Automatic retries for blockchain RPC calls
4. **Circuit Breaker**: Fail-fast for external services
5. **Graceful Degradation**: Fallback to cached data

## Monitoring & Observability

1. **Health Checks**: Liveness and readiness probes
2. **Metrics**: Prometheus-compatible metrics
3. **Logging**: Structured logging with trace IDs
4. **Performance**: Response time tracking
5. **Alerting**: Configurable alerts for failures

## Deployment Architecture

```
┌─────────────────────────────────────────────┐
│            Load Balancer / Nginx            │
└─────────────────────────────────────────────┘
                     │
        ┌────────────┼────────────┐
        ▼            ▼            ▼
    ┌────────┐  ┌────────┐  ┌────────┐
    │ API    │  │ API    │  │ API    │
    │ Server │  │ Server │  │ Server │
    │   1    │  │   2    │  │   3    │
    └────────┘  └────────┘  └────────┘
         │           │           │
         └───────────┼───────────┘
                     ▼
         ┌───────────────────────┐
         │   PostgreSQL          │
         │   (Primary/Replica)   │
         └───────────────────────┘
                     │
                     ▼
         ┌───────────────────────┐
         │   Redis Cluster       │
         └───────────────────────┘
```

## Configuration Management

- **Environment-based**: Development, Staging, Production
- **12-Factor App**: Following 12-factor app principles
- **Secret Management**: Support for environment variables and secret managers
- **Feature Flags**: Easy feature toggling

## Testing Strategy

1. **Unit Tests**: Service and utility function tests
2. **Integration Tests**: Database and API tests
3. **E2E Tests**: Full workflow tests
4. **Load Tests**: Performance benchmarking

## Future Enhancements

1. **Additional Chains**: Bitcoin, Polygon, Binance Smart Chain
2. **Token Pricing**: Real-time price feeds (CoinGecko/CoinMarketCap)
3. **Webhooks**: Event notifications
4. **WebSocket**: Real-time balance updates
5. **Analytics**: Portfolio performance tracking
6. **Multi-tenancy**: User authentication and isolation
