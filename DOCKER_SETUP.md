# Docker Setup Guide

## Quick Start (Simplified Setup)

For local development, you can start with just the essential services:

```bash
# 1. Copy environment file
cp .env.example .env

# 2. Start core services only (faster startup)
docker-compose up -d postgres redis

# 3. Build and start the API
docker-compose up -d --build api

# 4. Check if API is running
curl http://localhost:8000/health
```

## Full Platform Setup

To run the complete platform with all services:

```bash
# 1. Ensure you have copied .env file
cp .env.example .env

# 2. Start all services
docker-compose up -d

# 3. Wait for services to be healthy (may take 2-3 minutes)
docker-compose ps

# 4. Initialize database
docker-compose exec api python -m backend.scripts.init_db

# 5. Access services
# API: http://localhost:8000/docs
# Frontend: http://localhost:3000
# Airflow: http://localhost:8080 (admin/admin)
# Grafana: http://localhost:3001 (admin/admin)
# Jupyter: http://localhost:8888 (token: analytics123)
```

## Service-by-Service Startup

If you want to start services individually:

```bash
# Core databases
docker-compose up -d postgres redis clickhouse

# Object storage
docker-compose up -d minio

# Streaming
docker-compose up -d zookeeper kafka

# Application
docker-compose up -d --build api

# Frontend
docker-compose up -d --build frontend

# ML tracking
docker-compose up -d mlflow

# Workflow orchestration
docker-compose up -d airflow-webserver airflow-scheduler

# Data science
docker-compose up -d jupyter

# Monitoring
docker-compose up -d prometheus grafana
```

## Troubleshooting

### API Build Fails

If you see errors about missing `pyproject.toml`:

```bash
# Ensure you're in the project root directory
pwd  # Should show .../automatic-broccoli

# Rebuild with no cache
docker-compose build --no-cache api
```

### Port Conflicts

If ports are already in use:

```bash
# Check what's using the port
# Windows:
netstat -ano | findstr ":8000"

# Linux/Mac:
lsof -i :8000

# Either stop that service or change the port in docker-compose.yml
```

### Database Connection Issues

```bash
# Check if PostgreSQL is running
docker-compose ps postgres

# Check logs
docker-compose logs postgres

# Restart PostgreSQL
docker-compose restart postgres
```

### Clean Start

If you want to start fresh:

```bash
# Stop all services
docker-compose down

# Remove volumes (WARNING: This deletes all data)
docker-compose down -v

# Remove images to force rebuild
docker-compose down --rmi all

# Start fresh
docker-compose up -d
```

## Development Workflow

### Backend Development

```bash
# API runs with hot-reload enabled
# Edit files in backend/ and changes will auto-reload

# View logs
docker-compose logs -f api

# Run tests
docker-compose exec api pytest

# Access Python shell
docker-compose exec api python

# Run migrations
docker-compose exec api alembic upgrade head
```

### Frontend Development

```bash
# Frontend runs with hot-reload enabled
# Edit files in frontend/src/ and changes will auto-reload

# View logs
docker-compose logs -f frontend

# Install new package
docker-compose exec frontend npm install package-name

# Run tests
docker-compose exec frontend npm test
```

### Database Access

```bash
# PostgreSQL
docker-compose exec postgres psql -U analytics_user -d analytics_db

# ClickHouse
docker-compose exec clickhouse clickhouse-client

# Redis
docker-compose exec redis redis-cli -a redis_pass123
```

## Production Deployment

For production deployment:

1. Use `docker-compose.prod.yml` (to be created)
2. Set proper environment variables in `.env.production`
3. Use external managed databases instead of Docker databases
4. Enable TLS/SSL certificates
5. Set up proper backup strategies
6. Configure monitoring and alerting

## Resource Requirements

Minimum recommended resources:
- **RAM**: 8GB (16GB recommended for full stack)
- **CPU**: 4 cores (8 cores recommended)
- **Disk**: 20GB free space
- **Network**: Stable internet for image downloads

Individual service resources:
- PostgreSQL: ~512MB RAM
- ClickHouse: ~1GB RAM
- Kafka + Zookeeper: ~1GB RAM
- API: ~256MB RAM
- Airflow: ~512MB RAM
- Frontend: ~256MB RAM
- MLflow: ~256MB RAM
- Jupyter: ~512MB RAM

## Service Health Checks

```bash
# Check all service health
docker-compose ps

# Check specific service health
docker inspect --format='{{json .State.Health}}' analytics_api | jq

# View all service logs
docker-compose logs

# Follow logs for specific service
docker-compose logs -f api
```

## Common Commands

```bash
# View running containers
docker-compose ps

# Stop all services
docker-compose stop

# Start stopped services
docker-compose start

# Restart a service
docker-compose restart api

# View logs
docker-compose logs -f api

# Execute command in container
docker-compose exec api bash

# Rebuild specific service
docker-compose up -d --build api

# Scale a service
docker-compose up -d --scale api=3

# Remove stopped containers
docker-compose rm

# Show disk usage
docker system df
```

## Environment Variables

Key environment variables in `.env`:

```bash
# Database
POSTGRES_DB=analytics_db
POSTGRES_USER=analytics_user
POSTGRES_PASSWORD=analytics_pass123

# API
SECRET_KEY=your-secret-key-change-in-production
DEBUG=true

# Kafka
KAFKA_BOOTSTRAP_SERVERS=kafka:9092

# S3/MinIO
S3_ACCESS_KEY=minioadmin
S3_SECRET_KEY=minioadmin123
```

## Next Steps

After successful setup:

1. **Create a user**: Visit http://localhost:8000/docs and use the `/auth/register` endpoint
2. **Explore Jupyter**: Open http://localhost:8888 and run the sample notebooks
3. **Run ETL**: Access Airflow at http://localhost:8080 and trigger the sales pipeline
4. **View dashboards**: Open http://localhost:3000 for the React dashboard
5. **Monitor**: Check Grafana at http://localhost:3001 for system metrics

## Support

For issues:
- Check logs: `docker-compose logs <service-name>`
- View documentation in `/docs` directory
- Check GitHub issues
- Ensure Docker and Docker Compose are up to date
