"""
Sales Data ETL Pipeline

Extracts sales data from various sources, transforms it according to business rules,
and loads it into the data warehouse.
"""

from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.providers.postgres.operators.postgres import PostgresOperator

import pandas as pd
from loguru import logger


# Default arguments
default_args = {
    "owner": "data_engineering",
    "depends_on_past": False,
    "email": ["data-team@company.com"],
    "email_on_failure": True,
    "email_on_retry": False,
    "retries": 3,
    "retry_delay": timedelta(minutes=5),
    "execution_timeout": timedelta(minutes=30),
}

# DAG definition
dag = DAG(
    dag_id="sales_etl_pipeline",
    default_args=default_args,
    description="ETL pipeline for sales data from multiple sources",
    schedule_interval="0 2 * * *",  # Daily at 2 AM
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["sales", "etl", "daily"],
)


def extract_sales_data(**context):
    """
    Extract sales data from source systems.

    In production, this would connect to actual data sources.
    For demo purposes, we'll generate sample data.
    """
    logger.info("Extracting sales data...")

    execution_date = context["execution_date"]

    # Simulate extraction from multiple sources
    # In production: extract from MySQL, MongoDB, APIs, etc.

    sales_data = []
    for i in range(1000):
        sales_data.append(
            {
                "transaction_id": f"TXN{execution_date.strftime('%Y%m%d')}{i:06d}",
                "customer_id": f"CUST{(i % 100):04d}",
                "product_id": f"PROD{(i % 50):04d}",
                "location_id": f"LOC{(i % 10):03d}",
                "quantity": (i % 5) + 1,
                "unit_price": 10.00 + (i % 100),
                "discount_amount": (i % 10) * 0.5,
                "transaction_date": execution_date,
            }
        )

    df = pd.DataFrame(sales_data)

    # Save to XCom for next task
    output_path = f"/tmp/sales_extract_{execution_date.strftime('%Y%m%d')}.parquet"
    df.to_parquet(output_path, index=False)

    logger.info(f"Extracted {len(df)} sales records")

    return output_path


def transform_sales_data(**context):
    """
    Transform sales data according to business rules.

    Applies data quality checks, enrichment, and calculations.
    """
    logger.info("Transforming sales data...")

    # Get extracted data path from XCom
    ti = context["ti"]
    input_path = ti.xcom_pull(task_ids="extract_sales_data")

    # Load data
    df = pd.read_parquet(input_path)

    # Data quality checks
    df = df.dropna()  # Remove null values
    df = df.drop_duplicates(subset=["transaction_id"])  # Remove duplicates

    # Calculate derived fields
    df["subtotal"] = df["quantity"] * df["unit_price"]
    df["tax_amount"] = df["subtotal"] * 0.08  # 8% tax
    df["total_amount"] = df["subtotal"] - df["discount_amount"] + df["tax_amount"]

    # Calculate profit (assume 40% margin)
    df["cost_amount"] = df["subtotal"] * 0.6
    df["profit_amount"] = df["total_amount"] - df["cost_amount"]

    # Add metadata
    df["created_at"] = datetime.utcnow()
    df["payment_method"] = "CREDIT_CARD"
    df["shipping_method"] = "STANDARD"
    df["order_status"] = "COMPLETED"

    # Save transformed data
    output_path = f"/tmp/sales_transform_{context['execution_date'].strftime('%Y%m%d')}.parquet"
    df.to_parquet(output_path, index=False)

    logger.info(f"Transformed {len(df)} sales records")

    return output_path


def load_sales_data(**context):
    """
    Load transformed sales data into data warehouse.
    """
    logger.info("Loading sales data into warehouse...")

    # Get transformed data
    ti = context["ti"]
    input_path = ti.xcom_pull(task_ids="transform_sales_data")

    df = pd.read_parquet(input_path)

    # Load to PostgreSQL
    hook = PostgresHook(postgres_conn_id="warehouse_db")
    engine = hook.get_sqlalchemy_engine()

    # In production, this would use proper dimension lookups
    # For now, we'll simulate the load
    df.to_sql("fact_sales", engine, if_exists="append", index=False, method="multi", chunksize=1000)

    logger.info(f"Loaded {len(df)} sales records to warehouse")

    return len(df)


def validate_data_quality(**context):
    """
    Validate data quality after load.
    """
    logger.info("Validating data quality...")

    execution_date = context["execution_date"]

    hook = PostgresHook(postgres_conn_id="warehouse_db")

    # Check for duplicate transactions
    dup_query = """
        SELECT COUNT(*) as dup_count
        FROM (
            SELECT transaction_id, COUNT(*) as cnt
            FROM fact_sales
            WHERE DATE(created_at) = %(date)s
            GROUP BY transaction_id
            HAVING COUNT(*) > 1
        ) duplicates
    """

    result = hook.get_first(dup_query, parameters={"date": execution_date.date()})

    if result[0] > 0:
        raise ValueError(f"Found {result[0]} duplicate transactions!")

    # Check for negative amounts
    neg_query = """
        SELECT COUNT(*) FROM fact_sales
        WHERE total_amount < 0 AND DATE(created_at) = %(date)s
    """

    result = hook.get_first(neg_query, parameters={"date": execution_date.date()})

    if result[0] > 0:
        raise ValueError(f"Found {result[0]} records with negative amounts!")

    logger.info("Data quality validation passed")

    return True


# Define tasks
extract_task = PythonOperator(
    task_id="extract_sales_data",
    python_callable=extract_sales_data,
    dag=dag,
)

transform_task = PythonOperator(
    task_id="transform_sales_data",
    python_callable=transform_sales_data,
    dag=dag,
)

load_task = PythonOperator(
    task_id="load_sales_data",
    python_callable=load_sales_data,
    dag=dag,
)

validate_task = PythonOperator(
    task_id="validate_data_quality",
    python_callable=validate_data_quality,
    dag=dag,
)

# Update summary statistics
update_stats_task = PostgresOperator(
    task_id="update_summary_statistics",
    postgres_conn_id="warehouse_db",
    sql="""
        REFRESH MATERIALIZED VIEW CONCURRENTLY sales_daily_summary;
        REFRESH MATERIALIZED VIEW CONCURRENTLY product_performance;
    """,
    dag=dag,
)

# Define task dependencies
extract_task >> transform_task >> load_task >> validate_task >> update_stats_task
