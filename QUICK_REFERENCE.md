# Quick Reference Guide

## 🚀 Getting Started (30 seconds)

```bash
# 1. Setup environment
cp .env.example .env
# Edit .env and add your Ethereum RPC URL

# 2. Start everything
./start.sh

# 3. Test it
curl http://localhost:5000/api/v1/health
```

## 📋 Common Commands

### Using Make
```bash
make help          # Show all commands
make prod          # Start production
make dev           # Start development mode
make logs          # View logs
make stop          # Stop all services
make test          # Run tests
```

### Using Docker Compose
```bash
docker-compose up -d              # Start
docker-compose down               # Stop
docker-compose logs -f app        # View logs
docker-compose ps                 # Check status
docker-compose restart app        # Restart app
```

## 🔗 Essential URLs

- **API Base:** http://localhost:5000/api/v1
- **Health Check:** http://localhost:5000/api/v1/health
- **PostgreSQL:** localhost:5432
- **Redis:** localhost:6379

## 📝 Quick API Examples

### 1. Create Ethereum Wallet
```bash
curl -X POST http://localhost:5000/api/v1/wallets \
  -H "Content-Type: application/json" \
  -d '{"address":"0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb","chain":"ethereum","label":"My Wallet"}'
```

### 2. Fetch Balances
```bash
# Replace WALLET_ID with the ID from step 1
curl -X POST http://localhost:5000/api/v1/wallets/WALLET_ID/fetch \
  -H "Content-Type: application/json" \
  -d '{"force_refresh":true}'
```

### 3. View Portfolio
```bash
curl http://localhost:5000/api/v1/portfolio
```

## 🔧 Configuration

### Required Environment Variables
```env
ETHEREUM_RPC_URL=https://mainnet.infura.io/v3/YOUR_KEY
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/crypto_portfolio
REDIS_URL=redis://localhost:6379/0
```

### Optional Settings
```env
SOLANA_RPC_URL=https://api.mainnet-beta.solana.com
RATE_LIMIT_REQUESTS=100
CACHE_TTL=300
LOG_LEVEL=INFO
```

## 🐛 Troubleshooting

### Service Won't Start
```bash
# Check logs
docker-compose logs app

# Verify database
docker-compose exec postgres psql -U postgres -c "SELECT 1"

# Check environment
docker-compose exec app env | grep DATABASE_URL
```

### Database Issues
```bash
# Restart PostgreSQL
docker-compose restart postgres

# Check connections
docker-compose exec postgres psql -U postgres -c "SELECT count(*) FROM pg_stat_activity;"

# Reset database (WARNING: deletes data)
docker-compose down -v
docker-compose up -d
```

### Redis Issues
```bash
# Check Redis
docker-compose exec redis redis-cli ping

# Clear cache
docker-compose exec redis redis-cli FLUSHALL
```

## 📊 Monitoring

### View Logs
```bash
# Application logs
docker-compose logs -f app

# All services
docker-compose logs -f

# Last 100 lines
docker-compose logs --tail=100 app
```

### Check Health
```bash
# Quick health check
curl http://localhost:5000/api/v1/health

# Pretty print
curl -s http://localhost:5000/api/v1/health | json_pp
```

### Database Stats
```bash
# Table sizes
docker-compose exec postgres psql -U postgres -d crypto_portfolio \
  -c "SELECT tablename, pg_size_pretty(pg_total_relation_size(tablename::text)) FROM pg_tables WHERE schemaname='public';"

# Connection count
docker-compose exec postgres psql -U postgres -d crypto_portfolio \
  -c "SELECT count(*) FROM pg_stat_activity;"
```

## 🔄 Database Migrations

### Create Migration
```bash
# Using Make
make migrate-create MSG="add new column"

# Using Alembic directly
alembic revision --autogenerate -m "add new column"
```

### Apply Migrations
```bash
make migrate
# OR
docker-compose exec app alembic upgrade head
```

### Rollback
```bash
make migrate-rollback
# OR
docker-compose exec app alembic downgrade -1
```

## 📦 Backup & Restore

### Backup Database
```bash
# Create backup
docker-compose exec -T postgres pg_dump -U postgres crypto_portfolio > backup.sql

# Or with timestamp
make backup-db
```

### Restore Database
```bash
# Restore from backup
docker-compose exec -T postgres psql -U postgres crypto_portfolio < backup.sql

# Or using Make
make restore-db FILE=backup.sql
```

## 🧪 Testing

### Run Tests
```bash
# All tests
make test

# With coverage
pytest tests/ -v --cov=app --cov-report=html

# Specific test file
pytest tests/test_health.py -v
```

## 🎯 Development Workflow

### Local Development
```bash
# 1. Create virtual environment
python -m venv venv
source venv/bin/activate

# 2. Install dependencies
make install-dev

# 3. Start database & Redis
docker-compose up -d postgres redis

# 4. Run migrations
make migrate

# 5. Start app
python app/main.py
```

### Code Quality
```bash
# Format code
make format

# Lint code
make lint

# Type check
make type-check

# Run all checks
make check
```

## 📈 Scaling

### Scale Application
```bash
# Scale to 3 instances
docker-compose up -d --scale app=3

# Using Make
make scale REPLICAS=3

# With load balancer
# Add nginx or traefik in front
```

## 🔒 Security Checklist

- [ ] Change default passwords in `.env`
- [ ] Set strong `API_KEY`
- [ ] Configure `CORS_ORIGINS` for production
- [ ] Use HTTPS in production
- [ ] Secure RPC endpoints
- [ ] Enable rate limiting
- [ ] Regular backups
- [ ] Monitor logs for suspicious activity

## 📚 Documentation Files

- **README.md** - Main documentation
- **ARCHITECTURE.md** - System design
- **DEPLOYMENT.md** - Production deployment
- **API_EXAMPLES.md** - API usage examples
- **PROJECT_SUMMARY.md** - Complete overview
- **QUICK_REFERENCE.md** - This file

## 💡 Tips

1. **Use Make commands** for common tasks
2. **Check logs first** when debugging
3. **Test with health endpoint** before using API
4. **Cache is your friend** - balances cached for 5 minutes
5. **Use force_refresh=true** to bypass cache
6. **Monitor RPC rate limits** on your providers
7. **Keep backups** of your database
8. **Use Docker** for consistency

## 🆘 Support

### Common Error Messages

**"Ethereum service not connected"**
- Check `ETHEREUM_RPC_URL` in `.env`
- Verify RPC endpoint is accessible
- Check API key/credits

**"Database connection failed"**
- Ensure PostgreSQL is running
- Check `DATABASE_URL` format
- Verify credentials

**"Redis connection failed"**
- Start Redis: `docker-compose up -d redis`
- Check `REDIS_URL` in `.env`

**"Invalid address"**
- Verify address format for the chain
- Ethereum: 0x + 40 hex characters
- Solana: Base58 encoded (32-44 chars)

## 🎓 Next Steps

1. **Add your wallets** via API
2. **Fetch balances** and see them in portfolio
3. **Track changes** over time with history
4. **Integrate** with your frontend
5. **Add more chains** (see ARCHITECTURE.md)
6. **Implement price feeds** for USD values
7. **Add webhooks** for notifications
8. **Scale** as needed

---

**Need more help?** Check the full documentation in README.md and ARCHITECTURE.md
