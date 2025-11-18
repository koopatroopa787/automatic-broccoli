# 🚀 Quick Start Guide

Get the Enterprise Data Analytics Platform running in 5 minutes!

## Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop) installed and running
- At least 4GB RAM available
- Git installed

## Option 1: Minimal Setup (Fastest - Recommended for First Time)

Start with just the essential services to verify everything works:

```bash
# 1. Navigate to project directory
cd automatic-broccoli

# 2. Copy environment file
cp .env.example .env

# 3. Start core services (PostgreSQL, Redis, API)
docker-compose -f docker-compose.dev.yml up -d

# 4. Wait 30 seconds for services to start, then test
curl http://localhost:8000/health

# Should return: {"status":"healthy","version":"1.0.0",...}
```

### Access the API

Open http://localhost:8000/docs in your browser to see the interactive API documentation (Swagger UI).

### Create Your First User

1. Go to http://localhost:8000/docs
2. Find the `POST /api/v1/auth/register` endpoint
3. Click "Try it out"
4. Enter:
   ```json
   {
     "username": "admin",
     "email": "admin@example.com",
     "password": "securepassword123",
     "full_name": "Admin User"
   }
   ```
5. Click "Execute"
6. You should see a 201 response with your user details!

### Login and Get Token

1. Find the `POST /api/v1/auth/login` endpoint
2. Click "Try it out"
3. Enter username: `admin`, password: `securepassword123`
4. Click "Execute"
5. Copy the `access_token` from the response
6. Click the "Authorize" button at the top
7. Enter: `Bearer YOUR_TOKEN_HERE`
8. Now you can access protected endpoints!

### Stop Services

```bash
docker-compose -f docker-compose.dev.yml down
```

## Option 2: Full Platform

Once the minimal setup works, try the full platform:

```bash
# Start all services (12 containers)
docker-compose up -d

# This will start:
# - PostgreSQL (database)
# - ClickHouse (analytics database)
# - Redis (cache)
# - Kafka + Zookeeper (streaming)
# - MinIO (object storage)
# - FastAPI (backend)
# - React (frontend)
# - Airflow (ETL orchestration)
# - MLflow (ML tracking)
# - Jupyter (notebooks)
# - Prometheus + Grafana (monitoring)
```

### Access All Services

| Service | URL | Credentials |
|---------|-----|-------------|
| **API Docs** | http://localhost:8000/docs | - |
| **Frontend** | http://localhost:3000 | - |
| **Airflow** | http://localhost:8080 | admin / admin |
| **Grafana** | http://localhost:3001 | admin / admin |
| **Jupyter** | http://localhost:8888 | token: analytics123 |
| **MinIO Console** | http://localhost:9001 | minioadmin / minioadmin123 |
| **MinIO API** | http://localhost:9002 | - |
| **Prometheus** | http://localhost:9090 | - |

### Check Service Health

```bash
# View all running services
docker-compose ps

# View logs
docker-compose logs api
docker-compose logs -f api  # Follow logs

# Check API health
curl http://localhost:8000/health
```

## Common Issues & Solutions

### Issue: Port Already in Use

**Error**: `Bind for 0.0.0.0:8000 failed: port is already allocated`

**Solution**:
```bash
# Windows - Find what's using the port
netstat -ano | findstr ":8000"

# Kill the process or change port in docker-compose.yml
```

### Issue: Docker Build Fails

**Error**: `failed to compute cache key: "/pyproject.toml": not found`

**Solution**:
```bash
# Make sure you're in the project root directory
cd automatic-broccoli

# Verify pyproject.toml exists
ls pyproject.toml  # Should show the file

# Clean build
docker-compose down
docker-compose build --no-cache api
docker-compose up -d api
```

### Issue: Services Won't Start

**Solution**:
```bash
# Check Docker is running
docker info

# Check available resources
docker system df

# Clean up and restart
docker-compose down -v
docker-compose up -d
```

### Issue: API Returns 500 Error

**Solution**:
```bash
# Check API logs
docker-compose logs api

# Restart API
docker-compose restart api

# Check database is running
docker-compose ps postgres
```

## Next Steps

### 1. Explore the API

Visit http://localhost:8000/docs and try these endpoints:

- `GET /health` - Health check
- `POST /api/v1/auth/register` - Create user
- `POST /api/v1/auth/login` - Get JWT token
- `GET /api/v1/analytics/metrics/sales` - View sales metrics (requires auth)

### 2. Run Sample Data Import

```bash
# Enter the API container
docker-compose exec api bash

# Run sample data script (to be created)
python scripts/load_sample_data.py

# Exit container
exit
```

### 3. Explore Jupyter Notebooks

1. Open http://localhost:8888
2. Token: `analytics123`
3. Navigate to `work/01_exploratory_data_analysis.ipynb`
4. Run the cells to see data analysis examples

### 4. View Airflow DAGs

1. Open http://localhost:8080
2. Login: admin / admin
3. Find the `sales_etl_pipeline` DAG
4. Click to view and trigger it

### 5. Build the Frontend

```bash
# If frontend doesn't start automatically
docker-compose up -d --build frontend

# Wait a minute for build to complete
docker-compose logs -f frontend

# Visit http://localhost:3000
```

## Development Workflow

### Backend Development

```bash
# Make changes to files in backend/
# Changes auto-reload (watch the logs)
docker-compose logs -f api

# Run tests
docker-compose exec api pytest

# Access Python shell
docker-compose exec api python
```

### Frontend Development

```bash
# Make changes to files in frontend/src/
# Changes auto-reload in browser

# Install new package
docker-compose exec frontend npm install package-name

# View build output
docker-compose logs -f frontend
```

### Database Access

```bash
# PostgreSQL
docker-compose exec postgres psql -U analytics_user -d analytics_db

# Example queries
SELECT COUNT(*) FROM fact_sales;
```

## Performance Tips

1. **Allocate more resources to Docker**:
   - Docker Desktop → Settings → Resources
   - Increase RAM to 8GB
   - Increase CPUs to 4 cores

2. **Start only needed services**:
   ```bash
   # Just database and API
   docker-compose -f docker-compose.dev.yml up -d
   ```

3. **Use Docker BuildKit**:
   ```bash
   # Faster builds
   DOCKER_BUILDKIT=1 docker-compose build
   ```

## Clean Up

### Stop All Services
```bash
docker-compose down
```

### Remove All Data (Fresh Start)
```bash
# WARNING: This deletes all database data!
docker-compose down -v
```

### Free Up Disk Space
```bash
# Remove unused containers and images
docker system prune -a

# Check space
docker system df
```

## Getting Help

If you encounter issues:

1. Check logs: `docker-compose logs <service>`
2. Review [DOCKER_SETUP.md](DOCKER_SETUP.md) for detailed troubleshooting
3. Check [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for system architecture
4. Search GitHub issues
5. Create a new issue with:
   - Your OS and Docker version
   - Error messages
   - Output of `docker-compose ps`
   - Relevant logs

## What's Next?

- **Learn the Architecture**: Read [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- **Explore Notebooks**: Try Jupyter notebooks at http://localhost:8888
- **Build Features**: Add your own endpoints and models
- **Deploy**: Check production deployment guides
- **Customize**: Modify for your own data analytics use cases

---

**Congratulations!** 🎉 You now have a full enterprise data analytics platform running locally!
