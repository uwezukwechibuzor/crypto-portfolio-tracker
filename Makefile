.PHONY: help install dev prod test clean logs migrate shell db-shell redis-shell

help: ## Show this help message
	@echo "Crypto Portfolio Tracker - Available Commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies
	pip install -r requirements.txt

setup: ## Setup environment file
	cp .env.example .env
	@echo "✅ Created .env file. Please edit it with your configuration."

dev: ## Start development environment with Docker
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml up

prod: ## Start production environment with Docker
	docker-compose up -d

start: ## Quick start (same as ./start.sh)
	./start.sh

stop: ## Stop all Docker containers
	docker-compose down

restart: ## Restart Docker containers
	docker-compose restart

logs: ## View application logs
	docker-compose logs -f app

logs-all: ## View all container logs
	docker-compose logs -f

build: ## Build Docker image
	docker-compose build

clean: ## Clean up containers and volumes
	docker-compose down -v
	rm -rf __pycache__ */__pycache__ */*/__pycache__
	rm -rf .pytest_cache
	rm -rf logs/*.log

test: ## Run tests
	pytest tests/ -v --cov=app

test-watch: ## Run tests in watch mode
	pytest-watch tests/

migrate: ## Run database migrations
	alembic upgrade head

migrate-create: ## Create new migration (use MSG="message")
	alembic revision --autogenerate -m "$(MSG)"

migrate-rollback: ## Rollback last migration
	alembic downgrade -1

shell: ## Open Python shell with app context
	docker-compose exec app python

db-shell: ## Open PostgreSQL shell
	docker-compose exec postgres psql -U postgres -d crypto_portfolio

redis-shell: ## Open Redis CLI
	docker-compose exec redis redis-cli

health: ## Check application health
	curl -f http://localhost:5000/api/v1/health | json_pp || echo "❌ Health check failed"

status: ## Check status of all services
	@echo "=== Docker Containers ==="
	docker-compose ps
	@echo ""
	@echo "=== Application Health ==="
	curl -s http://localhost:5000/api/v1/health | json_pp || echo "❌ App not responding"

format: ## Format code with black
	black app/ tests/

lint: ## Lint code with flake8
	flake8 app/ tests/

type-check: ## Type check with mypy
	mypy app/

check: format lint type-check ## Run all code quality checks

backup-db: ## Backup database
	docker-compose exec -T postgres pg_dump -U postgres crypto_portfolio > backup_$(shell date +%Y%m%d_%H%M%S).sql

restore-db: ## Restore database (use FILE=backup.sql)
	docker-compose exec -T postgres psql -U postgres crypto_portfolio < $(FILE)

# Development commands
run-local: ## Run application locally (without Docker)
	python app/main.py

install-dev: ## Install development dependencies
	pip install -r requirements.txt
	pip install pytest pytest-watch pytest-cov black flake8 mypy

init-db: ## Initialize database tables
	python -c "from app.db.database import init_db; init_db()"

# Monitoring
monitor-db: ## Monitor database connections
	docker-compose exec postgres psql -U postgres -d crypto_portfolio -c "SELECT count(*) as connections FROM pg_stat_activity;"

monitor-redis: ## Monitor Redis statistics
	docker-compose exec redis redis-cli INFO stats

monitor-size: ## Check database size
	docker-compose exec postgres psql -U postgres -d crypto_portfolio -c "SELECT pg_size_pretty(pg_database_size('crypto_portfolio'));"

# Production commands
deploy: ## Deploy to production
	@echo "Building and starting production containers..."
	docker-compose build
	docker-compose up -d
	@echo "Waiting for services..."
	sleep 10
	docker-compose exec app alembic upgrade head
	@echo "✅ Deployment complete!"

scale: ## Scale app instances (use REPLICAS=3)
	docker-compose up -d --scale app=$(REPLICAS)
