#!/bin/bash
set -e

echo "🚀 Starting EvalOps Docker Stack..."
echo "  Postgres: localhost:5432"
echo "  Redis: localhost:6379"
echo "  ClickHouse: localhost:8123"
echo "  Prometheus: localhost:9090"
echo "  Grafana: localhost:3000"
echo "  Backend API: localhost:8000"
echo ""

docker-compose up -d

echo "✓ Stack started!"
echo ""
echo "Next steps:"
echo "  1. Wait 10s for Postgres to initialize"
echo "  2. Run database migrations:"
echo "     cd ../../backend && python -m alembic upgrade head"
echo "  3. Visit API docs: http://localhost:8000/docs"
echo "  4. Visit Grafana: http://localhost:3000 (admin/admin)"
echo ""
echo "To stop: docker-compose down"
