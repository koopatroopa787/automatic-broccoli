"""
Machine Learning Models

Models for ML model registry, experiments, and predictions.
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
    String,
    Text,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import JSONB

from api.database import Base


class ModelType(str, PyEnum):
    """ML model type enumeration."""

    REGRESSION = "regression"
    CLASSIFICATION = "classification"
    CLUSTERING = "clustering"
    TIME_SERIES = "time_series"
    ANOMALY_DETECTION = "anomaly_detection"
    RECOMMENDATION = "recommendation"


class ModelStatus(str, PyEnum):
    """Model lifecycle status."""

    TRAINING = "training"
    TRAINED = "trained"
    DEPLOYED = "deployed"
    ARCHIVED = "archived"
    FAILED = "failed"


class MLModel(Base):
    """Machine learning model registry."""

    __tablename__ = "ml_models"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), unique=True, nullable=False, index=True)
    description = Column(Text)
    model_type = Column(Enum(ModelType), nullable=False)
    status = Column(Enum(ModelStatus), nullable=False, default=ModelStatus.TRAINING)

    # Model details
    algorithm = Column(String(100))  # RandomForest, XGBoost, LSTM, etc.
    framework = Column(String(50))  # sklearn, xgboost, tensorflow, pytorch
    version = Column(String(50), nullable=False)

    # Hyperparameters and configuration
    hyperparameters = Column(JSONB)
    feature_columns = Column(JSONB)  # List of features used
    target_column = Column(String(255))

    # Training details
    training_dataset_size = Column(Integer)
    training_duration_seconds = Column(Integer)
    trained_at = Column(DateTime(timezone=True))

    # Performance metrics
    metrics = Column(JSONB)  # accuracy, precision, recall, f1, rmse, mae, etc.
    cross_validation_scores = Column(JSONB)

    # Model artifacts
    model_path = Column(String(500))  # S3 path or local path
    artifact_uri = Column(String(500))  # MLflow artifact URI
    mlflow_run_id = Column(String(100), unique=True)

    # Deployment
    is_deployed = Column(Boolean, default=False)
    deployed_at = Column(DateTime(timezone=True))
    endpoint_url = Column(String(500))

    # Usage statistics
    prediction_count = Column(Integer, default=0)
    avg_prediction_time_ms = Column(Float)

    # Metadata
    tags = Column(JSONB)
    created_by = Column(String(100))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    predictions = relationship("Prediction", back_populates="model", cascade="all, delete-orphan")
    experiments = relationship(
        "MLExperiment", back_populates="model", cascade="all, delete-orphan"
    )


class MLExperiment(Base):
    """ML experiment tracking."""

    __tablename__ = "ml_experiments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    model_id = Column(Integer, ForeignKey("ml_models.id", ondelete="CASCADE"), nullable=False)
    experiment_name = Column(String(255), nullable=False)
    run_id = Column(String(100), unique=True)

    # Experiment configuration
    parameters = Column(JSONB)
    data_config = Column(JSONB)

    # Results
    metrics = Column(JSONB)
    artifacts = Column(JSONB)

    # Status
    status = Column(String(50))
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    duration_seconds = Column(Integer)

    # Notes
    notes = Column(Text)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    model = relationship("MLModel", back_populates="experiments")


class Prediction(Base):
    """Model prediction log."""

    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    model_id = Column(Integer, ForeignKey("ml_models.id", ondelete="CASCADE"), nullable=False)

    # Input data
    input_data = Column(JSONB, nullable=False)

    # Prediction output
    prediction = Column(JSONB, nullable=False)
    prediction_probability = Column(Float)  # For classification models
    confidence_score = Column(Float)

    # Performance
    prediction_time_ms = Column(Float)

    # Metadata
    request_id = Column(String(100), unique=True)
    user_id = Column(String(100))
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    # Relationships
    model = relationship("MLModel", back_populates="predictions")


class FeatureStore(Base):
    """Feature store for ML features."""

    __tablename__ = "feature_store"

    id = Column(Integer, primary_key=True, autoincrement=True)
    feature_name = Column(String(255), unique=True, nullable=False, index=True)
    description = Column(Text)

    # Feature details
    feature_type = Column(String(50))  # numerical, categorical, text, datetime
    data_type = Column(String(50))  # int, float, string, bool
    transformation = Column(Text)  # SQL or Python code for feature generation

    # Source
    source_table = Column(String(255))
    source_columns = Column(JSONB)

    # Statistics
    statistics = Column(JSONB)  # mean, std, min, max, unique_values, etc.

    # Versioning
    version = Column(Integer, default=1)
    is_active = Column(Boolean, default=True)

    # Metadata
    tags = Column(JSONB)
    created_by = Column(String(100))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
