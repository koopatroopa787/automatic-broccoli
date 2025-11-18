"""
Database Models Package

Exports all SQLAlchemy models for the application.
"""

from api.models.analytics_models import (
    Dashboard,
    DimCustomer,
    DimDate,
    DimLocation,
    DimProduct,
    FactInventory,
    FactSales,
    FactWebAnalytics,
    Query,
)
from api.models.data_quality_models import (
    CheckStatus,
    CheckType,
    DataAnomaly,
    DataCatalog,
    DataProfile,
    DataQualityCheckResult,
    DataQualityRule,
    Severity,
)
from api.models.etl_models import (
    DataLineage,
    DataSource,
    DataSourceType,
    ETLPipeline,
    PipelineExecution,
    PipelineStatus,
)
from api.models.ml_models import (
    FeatureStore,
    MLExperiment,
    MLModel,
    ModelStatus,
    ModelType,
    Prediction,
)
from api.models.user_models import APIKey, Permission, Role, User, UserRole

__all__ = [
    # User models
    "User",
    "Role",
    "Permission",
    "APIKey",
    "UserRole",
    # Analytics models
    "DimDate",
    "DimCustomer",
    "DimProduct",
    "DimLocation",
    "FactSales",
    "FactWebAnalytics",
    "FactInventory",
    "Query",
    "Dashboard",
    # ETL models
    "DataSource",
    "ETLPipeline",
    "PipelineExecution",
    "DataLineage",
    "DataSourceType",
    "PipelineStatus",
    # ML models
    "MLModel",
    "MLExperiment",
    "Prediction",
    "FeatureStore",
    "ModelType",
    "ModelStatus",
    # Data Quality models
    "DataQualityRule",
    "DataQualityCheckResult",
    "DataProfile",
    "DataAnomaly",
    "DataCatalog",
    "CheckType",
    "CheckStatus",
    "Severity",
]
