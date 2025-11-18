"""
Analytics and Data Warehouse Models

Star/Snowflake schema models for the data warehouse.
Includes fact tables, dimension tables, and analytical views.
"""

from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    JSON,
    Numeric,
    String,
    Text,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import JSONB

from backend.api.database import Base


# ==================== Dimension Tables ====================


class DimDate(Base):
    """Date dimension table for time-based analysis."""

    __tablename__ = "dim_date"

    date_id = Column(Integer, primary_key=True)
    full_date = Column(DateTime(timezone=True), unique=True, nullable=False)
    day = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)
    year = Column(Integer, nullable=False)
    quarter = Column(Integer, nullable=False)
    day_of_week = Column(Integer, nullable=False)
    day_name = Column(String(20), nullable=False)
    month_name = Column(String(20), nullable=False)
    is_weekend = Column(Boolean, default=False)
    is_holiday = Column(Boolean, default=False)
    week_of_year = Column(Integer)
    fiscal_year = Column(Integer)
    fiscal_quarter = Column(Integer)


class DimCustomer(Base):
    """Customer dimension table (SCD Type 2)."""

    __tablename__ = "dim_customer"

    customer_key = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(String(100), nullable=False, index=True)
    customer_name = Column(String(255), nullable=False)
    email = Column(String(255))
    phone = Column(String(50))
    country = Column(String(100))
    state = Column(String(100))
    city = Column(String(100))
    postal_code = Column(String(20))
    customer_segment = Column(String(50))  # VIP, Regular, New
    lifetime_value_tier = Column(String(20))  # High, Medium, Low

    # SCD Type 2 columns
    effective_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True))
    is_current = Column(Boolean, default=True, index=True)
    version = Column(Integer, default=1)

    # Relationships
    sales = relationship("FactSales", back_populates="customer")


class DimProduct(Base):
    """Product dimension table."""

    __tablename__ = "dim_product"

    product_key = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(String(100), unique=True, nullable=False, index=True)
    product_name = Column(String(255), nullable=False)
    sku = Column(String(100), unique=True)
    category = Column(String(100), index=True)
    subcategory = Column(String(100))
    brand = Column(String(100))
    supplier = Column(String(255))
    unit_cost = Column(Numeric(10, 2))
    unit_price = Column(Numeric(10, 2))
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    sales = relationship("FactSales", back_populates="product")


class DimLocation(Base):
    """Location/Store dimension table."""

    __tablename__ = "dim_location"

    location_key = Column(Integer, primary_key=True, autoincrement=True)
    location_id = Column(String(100), unique=True, nullable=False)
    store_name = Column(String(255))
    store_type = Column(String(50))  # Physical, Online, Warehouse
    country = Column(String(100), index=True)
    region = Column(String(100))
    state = Column(String(100))
    city = Column(String(100))
    postal_code = Column(String(20))
    latitude = Column(Float)
    longitude = Column(Float)
    opened_date = Column(DateTime(timezone=True))
    is_active = Column(Boolean, default=True)

    # Relationships
    sales = relationship("FactSales", back_populates="location")


# ==================== Fact Tables ====================


class FactSales(Base):
    """Sales fact table - Core transactional data."""

    __tablename__ = "fact_sales"

    sale_id = Column(Integer, primary_key=True, autoincrement=True)
    transaction_id = Column(String(100), unique=True, nullable=False, index=True)

    # Foreign keys to dimensions
    date_key = Column(Integer, ForeignKey("dim_date.date_id"), nullable=False, index=True)
    customer_key = Column(
        Integer, ForeignKey("dim_customer.customer_key"), nullable=False, index=True
    )
    product_key = Column(
        Integer, ForeignKey("dim_product.product_key"), nullable=False, index=True
    )
    location_key = Column(
        Integer, ForeignKey("dim_location.location_key"), nullable=False, index=True
    )

    # Measures
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)
    discount_amount = Column(Numeric(10, 2), default=0)
    tax_amount = Column(Numeric(10, 2), default=0)
    total_amount = Column(Numeric(12, 2), nullable=False)
    cost_amount = Column(Numeric(12, 2))
    profit_amount = Column(Numeric(12, 2))

    # Degenerate dimensions (attributes in fact table)
    payment_method = Column(String(50))
    shipping_method = Column(String(50))
    order_status = Column(String(50))

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    customer = relationship("DimCustomer", back_populates="sales")
    product = relationship("DimProduct", back_populates="sales")
    location = relationship("DimLocation", back_populates="sales")


class FactWebAnalytics(Base):
    """Web analytics fact table - Clickstream data."""

    __tablename__ = "fact_web_analytics"

    event_id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(100), nullable=False, index=True)
    user_id = Column(String(100), index=True)
    date_key = Column(Integer, ForeignKey("dim_date.date_id"), nullable=False)

    # Event details
    event_type = Column(String(50), nullable=False)  # page_view, click, purchase, etc.
    event_timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    page_url = Column(String(500))
    page_title = Column(String(255))
    referrer_url = Column(String(500))

    # User context
    device_type = Column(String(50))  # Desktop, Mobile, Tablet
    browser = Column(String(50))
    os = Column(String(50))
    country = Column(String(100))
    city = Column(String(100))

    # Engagement metrics
    time_on_page = Column(Integer)  # seconds
    scroll_depth = Column(Integer)  # percentage

    # Additional data
    custom_properties = Column(JSONB)

    created_at = Column(DateTime(timezone=True), server_default=func.now())


class FactInventory(Base):
    """Inventory fact table - Daily inventory snapshots."""

    __tablename__ = "fact_inventory"

    inventory_id = Column(Integer, primary_key=True, autoincrement=True)
    date_key = Column(Integer, ForeignKey("dim_date.date_id"), nullable=False, index=True)
    product_key = Column(
        Integer, ForeignKey("dim_product.product_key"), nullable=False, index=True
    )
    location_key = Column(
        Integer, ForeignKey("dim_location.location_key"), nullable=False, index=True
    )

    # Inventory measures
    quantity_on_hand = Column(Integer, nullable=False)
    quantity_reserved = Column(Integer, default=0)
    quantity_available = Column(Integer, nullable=False)
    reorder_point = Column(Integer)
    safety_stock = Column(Integer)

    # Cost measures
    unit_cost = Column(Numeric(10, 2))
    total_value = Column(Numeric(12, 2))

    snapshot_timestamp = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


# ==================== Analytical Models ====================


class Query(Base):
    """User-defined analytical queries."""

    __tablename__ = "queries"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    sql_query = Column(Text, nullable=False)
    query_type = Column(String(50))  # adhoc, scheduled, saved
    is_public = Column(Boolean, default=False)
    execution_count = Column(Integer, default=0)
    avg_execution_time = Column(Float)  # milliseconds
    last_executed_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="queries")


class Dashboard(Base):
    """Interactive dashboards."""

    __tablename__ = "dashboards"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    layout = Column(JSONB)  # Dashboard layout configuration
    widgets = Column(JSONB)  # Widget configurations
    refresh_interval = Column(Integer)  # seconds
    is_public = Column(Boolean, default=False)
    is_favorite = Column(Boolean, default=False)
    view_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="dashboards")
