#!/bin/bash

# Quick start script for Crypto Portfolio Tracker

set -e

echo "🚀 Starting Crypto Portfolio Tracker..."
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env file and add your RPC URLs before continuing!"
    echo ""
    read -p "Press enter to continue after editing .env..."
fi

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is available (v2 or v1)
if docker compose version &> /dev/null; then
    COMPOSE_CMD="docker compose"
elif command -v docker-compose &> /dev/null; then
    COMPOSE_CMD="docker-compose"
else
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

echo "✅ Docker is installed"
echo ""

# Start services
echo "🐳 Starting Docker containers..."
if ! $COMPOSE_CMD up -d; then
    echo ""
    echo "❌ Failed to start Docker containers."
    echo "💡 Possible solutions:"
    echo "   1. Make sure Docker Desktop is running"
    echo "   2. Check if you have permission to access Docker"
    echo "   3. Try running: sudo $COMPOSE_CMD up -d"
    exit 1
fi

echo ""
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check health
echo ""
echo "🏥 Checking application health..."
curl -f http://localhost:8000/api/v1/health || {
    echo "❌ Health check failed. Check logs with: $COMPOSE_CMD logs app"
    exit 1
}

echo ""
echo ""
echo "✅ Crypto Portfolio Tracker is running!"
echo ""
echo "📍 API Base URL: http://localhost:8000/api/v1"
echo "🏥 Health Check: http://localhost:8000/api/v1/health"
echo ""
echo "📚 Documentation:"
echo "   - README.md - Getting started guide"
echo "   - ARCHITECTURE.md - System architecture"
echo "   - API_EXAMPLES.md - API usage examples"
echo "   - DEPLOYMENT.md - Production deployment guide"
echo ""
echo "📊 View logs:"
echo "   $COMPOSE_CMD logs -f app"
echo ""
echo "🛑 Stop services:"
echo "   $COMPOSE_CMD down"
echo ""
echo "Happy tracking! 🎯"
