"""
Analytics Router

Provides endpoints for analytical queries, KPIs, and business metrics.
"""

from datetime import datetime, timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from api.database import get_db
from api.models import (
    DimCustomer,
    DimProduct,
    FactSales,
    User,
)
from api.routers.auth import get_current_active_user

router = APIRouter()


# Pydantic models
class SalesMetrics(BaseModel):
    """Sales metrics response."""

    total_revenue: float
    total_orders: int
    avg_order_value: float
    total_profit: float
    profit_margin: float


class TopProduct(BaseModel):
    """Top product by sales."""

    product_id: str
    product_name: str
    total_revenue: float
    units_sold: int
    order_count: int


class CustomerSegment(BaseModel):
    """Customer segment analysis."""

    segment: str
    customer_count: int
    total_revenue: float
    avg_customer_value: float


class TimeSeriesPoint(BaseModel):
    """Time series data point."""

    date: datetime
    value: float
    label: str | None = None


@router.get("/metrics/sales", response_model=SalesMetrics)
async def get_sales_metrics(
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> dict[str, Any]:
    """
    Get overall sales metrics.

    Args:
        start_date: Start date filter
        end_date: End date filter
        db: Database session
        current_user: Current authenticated user

    Returns:
        Sales metrics including revenue, orders, and profit
    """
    # Default date range: last 30 days
    if not end_date:
        end_date = datetime.utcnow()
    if not start_date:
        start_date = end_date - timedelta(days=30)

    # Build query
    query = select(
        func.sum(FactSales.total_amount).label("total_revenue"),
        func.count(FactSales.sale_id).label("total_orders"),
        func.avg(FactSales.total_amount).label("avg_order_value"),
        func.sum(FactSales.profit_amount).label("total_profit"),
    ).where(FactSales.created_at.between(start_date, end_date))

    result = await db.execute(query)
    row = result.one()

    total_revenue = float(row.total_revenue or 0)
    total_profit = float(row.total_profit or 0)
    profit_margin = (total_profit / total_revenue * 100) if total_revenue > 0 else 0

    return {
        "total_revenue": total_revenue,
        "total_orders": row.total_orders or 0,
        "avg_order_value": float(row.avg_order_value or 0),
        "total_profit": total_profit,
        "profit_margin": round(profit_margin, 2),
    }


@router.get("/products/top", response_model=list[TopProduct])
async def get_top_products(
    limit: int = Query(default=10, ge=1, le=100),
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> list[dict[str, Any]]:
    """
    Get top products by revenue.

    Args:
        limit: Number of top products to return
        start_date: Start date filter
        end_date: End date filter
        db: Database session
        current_user: Current authenticated user

    Returns:
        List of top products
    """
    if not end_date:
        end_date = datetime.utcnow()
    if not start_date:
        start_date = end_date - timedelta(days=30)

    query = (
        select(
            DimProduct.product_id,
            DimProduct.product_name,
            func.sum(FactSales.total_amount).label("total_revenue"),
            func.sum(FactSales.quantity).label("units_sold"),
            func.count(FactSales.sale_id).label("order_count"),
        )
        .join(DimProduct, FactSales.product_key == DimProduct.product_key)
        .where(FactSales.created_at.between(start_date, end_date))
        .group_by(DimProduct.product_id, DimProduct.product_name)
        .order_by(func.sum(FactSales.total_amount).desc())
        .limit(limit)
    )

    result = await db.execute(query)
    rows = result.all()

    return [
        {
            "product_id": row.product_id,
            "product_name": row.product_name,
            "total_revenue": float(row.total_revenue),
            "units_sold": row.units_sold,
            "order_count": row.order_count,
        }
        for row in rows
    ]


@router.get("/customers/segments", response_model=list[CustomerSegment])
async def get_customer_segments(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> list[dict[str, Any]]:
    """
    Get customer segmentation analysis.

    Args:
        db: Database session
        current_user: Current authenticated user

    Returns:
        Customer segments with metrics
    """
    query = (
        select(
            DimCustomer.customer_segment.label("segment"),
            func.count(func.distinct(DimCustomer.customer_key)).label("customer_count"),
            func.sum(FactSales.total_amount).label("total_revenue"),
            func.avg(FactSales.total_amount).label("avg_customer_value"),
        )
        .join(DimCustomer, FactSales.customer_key == DimCustomer.customer_key)
        .where(DimCustomer.is_current == True)  # noqa: E712
        .group_by(DimCustomer.customer_segment)
        .order_by(func.sum(FactSales.total_amount).desc())
    )

    result = await db.execute(query)
    rows = result.all()

    return [
        {
            "segment": row.segment or "Unknown",
            "customer_count": row.customer_count,
            "total_revenue": float(row.total_revenue or 0),
            "avg_customer_value": float(row.avg_customer_value or 0),
        }
        for row in rows
    ]


@router.get("/revenue/timeseries", response_model=list[TimeSeriesPoint])
async def get_revenue_timeseries(
    granularity: str = Query(default="day", regex="^(day|week|month)$"),
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> list[dict[str, Any]]:
    """
    Get revenue time series data.

    Args:
        granularity: Time granularity (day, week, month)
        start_date: Start date
        end_date: End date
        db: Database session
        current_user: Current authenticated user

    Returns:
        Time series data points
    """
    if not end_date:
        end_date = datetime.utcnow()
    if not start_date:
        start_date = end_date - timedelta(days=90)

    # Use PostgreSQL date_trunc for time series aggregation
    trunc_format = granularity
    query_text = f"""
        SELECT
            date_trunc('{trunc_format}', created_at) as date,
            SUM(total_amount) as value
        FROM fact_sales
        WHERE created_at BETWEEN :start_date AND :end_date
        GROUP BY date_trunc('{trunc_format}', created_at)
        ORDER BY date
    """

    result = await db.execute(
        text(query_text), {"start_date": start_date, "end_date": end_date}
    )
    rows = result.all()

    return [{"date": row.date, "value": float(row.value), "label": None} for row in rows]


@router.post("/query/adhoc")
async def execute_adhoc_query(
    sql_query: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> dict[str, Any]:
    """
    Execute ad-hoc SQL query (restricted to SELECT only for security).

    Args:
        sql_query: SQL query to execute
        db: Database session
        current_user: Current authenticated user

    Returns:
        Query results

    Raises:
        HTTPException: If query is not a SELECT statement
    """
    # Security: Only allow SELECT queries
    if not sql_query.strip().upper().startswith("SELECT"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only SELECT queries are allowed",
        )

    try:
        result = await db.execute(text(sql_query))
        rows = result.fetchall()

        # Convert to dict
        columns = result.keys()
        data = [dict(zip(columns, row)) for row in rows]

        return {
            "columns": list(columns),
            "data": data,
            "row_count": len(data),
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Query execution failed: {str(e)}",
        )
