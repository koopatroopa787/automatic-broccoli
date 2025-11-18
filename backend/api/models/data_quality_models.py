"""
Data Quality Models

Models for data quality checks, validation rules, and quality metrics.
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
    String,
    Text,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import JSONB

from api.database import Base


class CheckType(str, PyEnum):
    """Data quality check type."""

    NULL_CHECK = "null_check"
    RANGE_CHECK = "range_check"
    UNIQUENESS_CHECK = "uniqueness_check"
    SCHEMA_CHECK = "schema_check"
    FRESHNESS_CHECK = "freshness_check"
    COMPLETENESS_CHECK = "completeness_check"
    CONSISTENCY_CHECK = "consistency_check"
    CUSTOM_CHECK = "custom_check"


class CheckStatus(str, PyEnum):
    """Data quality check status."""

    PASSED = "passed"
    FAILED = "failed"
    WARNING = "warning"
    SKIPPED = "skipped"


class Severity(str, PyEnum):
    """Issue severity level."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class DataQualityRule(Base):
    """Data quality validation rules."""

    __tablename__ = "data_quality_rules"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), unique=True, nullable=False, index=True)
    description = Column(Text)

    # Target
    target_table = Column(String(255), nullable=False, index=True)
    target_column = Column(String(255))  # Null for table-level checks

    # Check configuration
    check_type = Column(Enum(CheckType), nullable=False)
    check_config = Column(JSONB, nullable=False)  # Check parameters
    severity = Column(Enum(Severity), nullable=False, default=Severity.MEDIUM)

    # Thresholds
    warning_threshold = Column(Float)  # Percentage or absolute value
    failure_threshold = Column(Float)

    # Scheduling
    is_active = Column(Boolean, default=True)
    schedule_cron = Column(String(100))

    # Metadata
    created_by = Column(String(100))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    check_results = relationship(
        "DataQualityCheckResult", back_populates="rule", cascade="all, delete-orphan"
    )


class DataQualityCheckResult(Base):
    """Data quality check execution results."""

    __tablename__ = "data_quality_check_results"

    id = Column(Integer, primary_key=True, autoincrement=True)
    rule_id = Column(
        Integer,
        ForeignKey("data_quality_rules.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Execution details
    execution_id = Column(String(100), nullable=False)
    status = Column(Enum(CheckStatus), nullable=False)
    executed_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    # Results
    passed_count = Column(Integer, default=0)
    failed_count = Column(Integer, default=0)
    total_count = Column(Integer, default=0)
    pass_rate = Column(Float)  # Percentage

    # Details
    error_message = Column(Text)
    failed_records = Column(JSONB)  # Sample of failed records
    statistics = Column(JSONB)

    # Metadata
    execution_time_ms = Column(Integer)

    # Relationships
    rule = relationship("DataQualityRule", back_populates="check_results")


class DataProfile(Base):
    """Data profiling statistics."""

    __tablename__ = "data_profiles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    table_name = Column(String(255), nullable=False, index=True)
    column_name = Column(String(255), nullable=False, index=True)

    # Basic statistics
    row_count = Column(Integer)
    null_count = Column(Integer)
    null_percentage = Column(Float)
    distinct_count = Column(Integer)
    distinct_percentage = Column(Float)

    # Numerical statistics
    min_value = Column(Float)
    max_value = Column(Float)
    mean_value = Column(Float)
    median_value = Column(Float)
    std_dev = Column(Float)

    # String statistics
    min_length = Column(Integer)
    max_length = Column(Integer)
    avg_length = Column(Float)

    # Distribution
    value_distribution = Column(JSONB)  # Top N values with frequencies
    quantiles = Column(JSONB)  # 25th, 50th, 75th percentiles

    # Data types
    inferred_type = Column(String(50))
    type_counts = Column(JSONB)  # Different types found in the column

    # Patterns
    pattern_matches = Column(JSONB)  # Email, phone, URL, etc.

    # Metadata
    profiled_at = Column(DateTime(timezone=True), server_default=func.now())
    profile_version = Column(Integer, default=1)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class DataAnomaly(Base):
    """Detected data anomalies."""

    __tablename__ = "data_anomalies"

    id = Column(Integer, primary_key=True, autoincrement=True)
    table_name = Column(String(255), nullable=False, index=True)
    column_name = Column(String(255))

    # Anomaly details
    anomaly_type = Column(String(100), nullable=False)  # outlier, drift, missing_spike, etc.
    severity = Column(Enum(Severity), nullable=False)
    description = Column(Text)

    # Detection details
    detection_method = Column(String(100))  # statistical, ml_based, rule_based
    anomaly_score = Column(Float)
    threshold = Column(Float)

    # Context
    affected_records = Column(Integer)
    sample_records = Column(JSONB)

    # Status
    is_resolved = Column(Boolean, default=False)
    resolved_at = Column(DateTime(timezone=True))
    resolution_notes = Column(Text)

    # Metadata
    detected_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    detected_by = Column(String(100))  # system or user

    created_at = Column(DateTime(timezone=True), server_default=func.now())


class DataCatalog(Base):
    """Data catalog for metadata management."""

    __tablename__ = "data_catalog"

    id = Column(Integer, primary_key=True, autoincrement=True)
    table_name = Column(String(255), unique=True, nullable=False, index=True)
    schema_name = Column(String(100), default="public")

    # Description
    display_name = Column(String(255))
    description = Column(Text)
    business_owner = Column(String(100))
    technical_owner = Column(String(100))

    # Classification
    data_domain = Column(String(100))  # Sales, Marketing, Finance, etc.
    sensitivity_level = Column(String(50))  # Public, Internal, Confidential, Restricted
    retention_policy = Column(String(255))

    # Schema
    columns_metadata = Column(JSONB)  # Column definitions with descriptions
    primary_keys = Column(JSONB)
    foreign_keys = Column(JSONB)
    indexes = Column(JSONB)

    # Statistics
    total_rows = Column(Integer)
    total_size_mb = Column(Float)
    last_updated_at = Column(DateTime(timezone=True))

    # Usage
    query_count = Column(Integer, default=0)
    avg_query_time_ms = Column(Float)

    # Tags and lineage
    tags = Column(JSONB)
    upstream_tables = Column(JSONB)  # Dependencies
    downstream_tables = Column(JSONB)  # Dependents

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
