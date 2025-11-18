"""
Unit tests for analytics endpoints.
"""

import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from api.main import app
from api.database import Base, get_db
from api.models import User, FactSales, DimProduct, DimCustomer, DimLocation, DimDate


# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="module")
def test_db():
    """Create test database and tables."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_session(test_db):
    """Create a new database session for each test."""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def client(db_session):
    """Create test client with database override."""

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db_session):
    """Create a test user."""
    from api.routers.auth import get_password_hash

    user = User(
        username="testuser",
        email="test@example.com",
        full_name="Test User",
        hashed_password=get_password_hash("testpassword"),
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def auth_token(client, test_user):
    """Get authentication token for test user."""
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "testuser", "password": "testpassword"},
    )
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.fixture
def sample_sales_data(db_session):
    """Create sample sales data for testing."""
    # Create dimension records
    date = DimDate(
        date_id=20240101,
        full_date=datetime(2024, 1, 1),
        day=1,
        month=1,
        year=2024,
        quarter=1,
        day_of_week=1,
        day_name="Monday",
        month_name="January",
        is_weekend=False,
        is_holiday=False,
        week_of_year=1,
    )
    db_session.add(date)

    customer = DimCustomer(
        customer_id="CUST001",
        customer_name="John Doe",
        email="john@example.com",
        customer_segment="VIP",
        effective_date=datetime.utcnow(),
        is_current=True,
        version=1,
    )
    db_session.add(customer)

    product = DimProduct(
        product_id="PROD001",
        product_name="Test Product",
        sku="SKU001",
        category="Electronics",
        unit_price=100.00,
        is_active=True,
    )
    db_session.add(product)

    location = DimLocation(
        location_id="LOC001",
        store_name="Main Store",
        store_type="Physical",
        country="USA",
        is_active=True,
    )
    db_session.add(location)

    db_session.commit()

    # Create sales fact
    sale = FactSales(
        transaction_id="TXN001",
        date_key=date.date_id,
        customer_key=customer.customer_key,
        product_key=product.product_key,
        location_key=location.location_key,
        quantity=2,
        unit_price=100.00,
        discount_amount=10.00,
        tax_amount=16.00,
        total_amount=206.00,
        cost_amount=120.00,
        profit_amount=86.00,
        payment_method="CREDIT_CARD",
        order_status="COMPLETED",
        created_at=datetime.utcnow(),
    )
    db_session.add(sale)
    db_session.commit()

    return {
        "date": date,
        "customer": customer,
        "product": product,
        "location": location,
        "sale": sale,
    }


class TestAnalyticsEndpoints:
    """Test suite for analytics endpoints."""

    def test_get_sales_metrics_unauthorized(self, client):
        """Test that sales metrics endpoint requires authentication."""
        response = client.get("/api/v1/analytics/metrics/sales")
        assert response.status_code == 401

    def test_get_sales_metrics_success(self, client, auth_token, sample_sales_data):
        """Test successful retrieval of sales metrics."""
        response = client.get(
            "/api/v1/analytics/metrics/sales",
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert response.status_code == 200
        data = response.json()

        assert "total_revenue" in data
        assert "total_orders" in data
        assert "avg_order_value" in data
        assert "total_profit" in data
        assert "profit_margin" in data

        assert data["total_revenue"] > 0
        assert data["total_orders"] > 0

    def test_get_top_products(self, client, auth_token, sample_sales_data):
        """Test retrieval of top products."""
        response = client.get(
            "/api/v1/analytics/products/top?limit=5",
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert response.status_code == 200
        data = response.json()

        assert isinstance(data, list)
        if len(data) > 0:
            product = data[0]
            assert "product_id" in product
            assert "product_name" in product
            assert "total_revenue" in product
            assert "units_sold" in product

    def test_get_customer_segments(self, client, auth_token, sample_sales_data):
        """Test customer segmentation analysis."""
        response = client.get(
            "/api/v1/analytics/customers/segments",
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert response.status_code == 200
        data = response.json()

        assert isinstance(data, list)
        if len(data) > 0:
            segment = data[0]
            assert "segment" in segment
            assert "customer_count" in segment
            assert "total_revenue" in segment

    def test_get_revenue_timeseries(self, client, auth_token, sample_sales_data):
        """Test revenue time series endpoint."""
        response = client.get(
            "/api/v1/analytics/revenue/timeseries?granularity=day",
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert response.status_code == 200
        data = response.json()

        assert isinstance(data, list)

    def test_adhoc_query_select_only(self, client, auth_token):
        """Test that ad-hoc queries only allow SELECT statements."""
        # Should succeed with SELECT
        response = client.post(
            "/api/v1/analytics/query/adhoc",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={"sql_query": "SELECT 1"},
        )
        # May fail due to database schema but should not be rejected for security
        assert response.status_code in [200, 400]

        # Should fail with non-SELECT
        response = client.post(
            "/api/v1/analytics/query/adhoc",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={"sql_query": "DROP TABLE users"},
        )
        assert response.status_code == 400
        assert "Only SELECT queries are allowed" in response.json()["detail"]

    def test_sales_metrics_date_filtering(self, client, auth_token, sample_sales_data):
        """Test date filtering for sales metrics."""
        start_date = (datetime.utcnow() - timedelta(days=7)).isoformat()
        end_date = datetime.utcnow().isoformat()

        response = client.get(
            f"/api/v1/analytics/metrics/sales?start_date={start_date}&end_date={end_date}",
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert response.status_code == 200

    def test_top_products_limit_validation(self, client, auth_token):
        """Test that top products limit is validated."""
        # Valid limit
        response = client.get(
            "/api/v1/analytics/products/top?limit=10",
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert response.status_code == 200

        # Limit too high
        response = client.get(
            "/api/v1/analytics/products/top?limit=1000",
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert response.status_code == 422  # Validation error


class TestAuthenticationEndpoints:
    """Test suite for authentication endpoints."""

    def test_register_user(self, client):
        """Test user registration."""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "username": "newuser",
                "email": "newuser@example.com",
                "password": "securepassword123",
                "full_name": "New User",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == "newuser"
        assert data["email"] == "newuser@example.com"
        assert "hashed_password" not in data

    def test_register_duplicate_user(self, client, test_user):
        """Test that duplicate registration is rejected."""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "username": "testuser",
                "email": "different@example.com",
                "password": "password123",
            },
        )
        assert response.status_code == 400

    def test_login_success(self, client, test_user):
        """Test successful login."""
        response = client.post(
            "/api/v1/auth/login",
            data={"username": "testuser", "password": "testpassword"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_invalid_credentials(self, client, test_user):
        """Test login with invalid credentials."""
        response = client.post(
            "/api/v1/auth/login",
            data={"username": "testuser", "password": "wrongpassword"},
        )
        assert response.status_code == 401

    def test_get_current_user(self, client, auth_token, test_user):
        """Test getting current user information."""
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "testuser"
        assert data["email"] == "test@example.com"


@pytest.mark.integration
class TestHealthEndpoints:
    """Test health check endpoints."""

    def test_root_endpoint(self, client):
        """Test root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data
        assert "status" in data
        assert data["status"] == "operational"

    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    def test_ping(self, client):
        """Test ping endpoint."""
        response = client.get("/api/v1/ping")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "pong"
