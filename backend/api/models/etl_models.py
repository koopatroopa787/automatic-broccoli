"""
ETL Pipeline Models

Models for tracking ETL jobs, data sources, and pipeline execution.
"""

from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import JSONB

from backend.api.database import Base


class DataSourceType(str, PyEnum):
    """Data source type enumeration."""

    DATABASE = "database"
    API = "api"
    FILE = "file"
    STREAM = "stream"
    CLOUD_STORAGE = "cloud_storage"


class PipelineStatus(str, PyEnum):
    """Pipeline execution status."""

    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    PAUSED = "paused"
    CANCELLED = "cancelled"


class DataSource(Base):
    """Data source configuration."""

    __tablename__ = "data_sources"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), unique=True, nullable=False, index=True)
    description = Column(Text)
    source_type = Column(Enum(DataSourceType), nullable=False)

    # Connection details (encrypted in production)
    connection_config = Column(JSONB, nullable=False)

    # Metadata
    schema_info = Column(JSONB)  # Table/collection schemas
    is_active = Column(Boolean, default=True)
    last_connected_at = Column(DateTime(timezone=True))
    last_sync_at = Column(DateTime(timezone=True))

    # Statistics
    total_records = Column(Integer, default=0)
    data_size_mb = Column(Integer, default=0)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    pipelines = relationship("ETLPipeline", back_populates="data_source")


class ETLPipeline(Base):
    """ETL pipeline configuration."""

    __tablename__ = "etl_pipelines"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), unique=True, nullable=False, index=True)
    description = Column(Text)

    # Source
    data_source_id = Column(
        Integer, ForeignKey("data_sources.id", ondelete="SET NULL"), index=True
    )

    # Pipeline configuration
    extraction_config = Column(JSONB)  # How to extract data
    transformation_config = Column(JSONB)  # Transformation rules
    loading_config = Column(JSONB)  # Where to load data

    # Scheduling
    schedule_cron = Column(String(100))  # Cron expression
    is_active = Column(Boolean, default=True)
    is_incremental = Column(Boolean, default=True)

    # Execution settings
    timeout_minutes = Column(Integer, default=60)
    retry_count = Column(Integer, default=3)
    parallel_tasks = Column(Integer, default=1)

    # Metadata
    airflow_dag_id = Column(String(255), unique=True)
    last_execution_at = Column(DateTime(timezone=True))
    next_execution_at = Column(DateTime(timezone=True))

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    data_source = relationship("DataSource", back_populates="pipelines")
    executions = relationship(
        "PipelineExecution", back_populates="pipeline", cascade="all, delete-orphan"
    )


class PipelineExecution(Base):
    """ETL pipeline execution log."""

    __tablename__ = "pipeline_executions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    pipeline_id = Column(
        Integer, ForeignKey("etl_pipelines.id", ondelete="CASCADE"), nullable=False, index=True
    )
    execution_id = Column(String(100), unique=True, nullable=False)  # UUID

    # Execution details
    status = Column(Enum(PipelineStatus), nullable=False, default=PipelineStatus.PENDING)
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    duration_seconds = Column(Integer)

    # Metrics
    records_extracted = Column(Integer, default=0)
    records_transformed = Column(Integer, default=0)
    records_loaded = Column(Integer, default=0)
    records_failed = Column(Integer, default=0)
    data_size_mb = Column(Integer, default=0)

    # Error tracking
    error_message = Column(Text)
    error_trace = Column(Text)

    # Execution logs
    logs = Column(Text)
    execution_metadata = Column(JSONB)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    pipeline = relationship("ETLPipeline", back_populates="executions")


class DataLineage(Base):
    """Data lineage tracking."""

    __tablename__ = "data_lineage"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Source
    source_type = Column(String(50), nullable=False)  # table, file, api
    source_name = Column(String(255), nullable=False)

    # Target
    target_type = Column(String(50), nullable=False)
    target_name = Column(String(255), nullable=False)

    # Transformation
    pipeline_id = Column(Integer, ForeignKey("etl_pipelines.id", ondelete="CASCADE"))
    transformation_logic = Column(Text)

    # Metadata
    column_mappings = Column(JSONB)  # Source to target column mappings
    created_at = Column(DateTime(timezone=True), server_default=func.now())
