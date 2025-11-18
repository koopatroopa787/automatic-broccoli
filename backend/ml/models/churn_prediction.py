"""
Customer Churn Prediction Model

Predicts customer churn using XGBoost with feature engineering and model tracking.
"""

import os
from datetime import datetime
from typing import Any, Dict, Tuple

import mlflow
import mlflow.sklearn
import numpy as np
import pandas as pd
import shap
from loguru import logger
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import cross_val_score, train_test_split
from xgboost import XGBClassifier


class ChurnPredictionModel:
    """Customer churn prediction using XGBoost."""

    def __init__(self, mlflow_tracking_uri: str = "http://localhost:5000"):
        """
        Initialize churn prediction model.

        Args:
            mlflow_tracking_uri: MLflow tracking server URI
        """
        self.model = None
        self.feature_names = None
        mlflow.set_tracking_uri(mlflow_tracking_uri)

    def engineer_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create features for churn prediction.

        Args:
            df: Raw customer data

        Returns:
            DataFrame with engineered features
        """
        logger.info("Engineering features...")

        features = pd.DataFrame()

        # Customer demographics features
        features["customer_age_days"] = (datetime.now() - df["customer_since"]).dt.days
        features["is_vip"] = (df["customer_segment"] == "VIP").astype(int)

        # Transaction features
        features["total_transactions"] = df["transaction_count"]
        features["avg_transaction_value"] = df["total_revenue"] / (df["transaction_count"] + 1)
        features["days_since_last_transaction"] = (
            datetime.now() - df["last_transaction_date"]
        ).dt.days

        # Engagement features
        features["login_frequency"] = df["login_count"] / features["customer_age_days"]
        features["support_tickets"] = df["support_ticket_count"]

        # RFM features (Recency, Frequency, Monetary)
        features["recency"] = features["days_since_last_transaction"]
        features["frequency"] = df["transaction_count"]
        features["monetary"] = df["total_revenue"]

        # Behavioral features
        features["has_mobile_app"] = df["mobile_app_installed"].astype(int)
        features["has_referred_customers"] = (df["referral_count"] > 0).astype(int)
        features["avg_product_rating"] = df["avg_rating"].fillna(0)

        # Trend features (comparing last 30 days vs previous 30 days)
        features["revenue_trend"] = (
            df["revenue_last_30d"] / (df["revenue_prev_30d"] + 1)
        ) - 1
        features["transaction_trend"] = (
            df["transactions_last_30d"] / (df["transactions_prev_30d"] + 1)
        ) - 1

        # Fill missing values
        features = features.fillna(0)

        # Store feature names
        self.feature_names = features.columns.tolist()

        logger.info(f"Created {len(features.columns)} features")

        return features

    def train(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        hyperparameters: Dict[str, Any] | None = None,
        experiment_name: str = "churn_prediction",
    ) -> Dict[str, Any]:
        """
        Train churn prediction model with MLflow tracking.

        Args:
            X: Feature matrix
            y: Target variable (0=retained, 1=churned)
            hyperparameters: Model hyperparameters
            experiment_name: MLflow experiment name

        Returns:
            Training metrics
        """
        logger.info("Training churn prediction model...")

        # Set default hyperparameters
        if hyperparameters is None:
            hyperparameters = {
                "n_estimators": 200,
                "max_depth": 6,
                "learning_rate": 0.1,
                "subsample": 0.8,
                "colsample_bytree": 0.8,
                "random_state": 42,
            }

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )

        # Set MLflow experiment
        mlflow.set_experiment(experiment_name)

        with mlflow.start_run():
            # Log hyperparameters
            mlflow.log_params(hyperparameters)

            # Train model
            self.model = XGBClassifier(**hyperparameters)
            self.model.fit(X_train, y_train)

            # Make predictions
            y_pred = self.model.predict(X_test)
            y_pred_proba = self.model.predict_proba(X_test)[:, 1]

            # Calculate metrics
            metrics = {
                "accuracy": accuracy_score(y_test, y_pred),
                "precision": precision_score(y_test, y_pred),
                "recall": recall_score(y_test, y_pred),
                "f1_score": f1_score(y_test, y_pred),
                "roc_auc": roc_auc_score(y_test, y_pred_proba),
            }

            # Cross-validation
            cv_scores = cross_val_score(self.model, X, y, cv=5, scoring="roc_auc")
            metrics["cv_roc_auc_mean"] = cv_scores.mean()
            metrics["cv_roc_auc_std"] = cv_scores.std()

            # Log metrics
            mlflow.log_metrics(metrics)

            # Log model
            mlflow.sklearn.log_model(self.model, "model")

            # Feature importance
            feature_importance = pd.DataFrame(
                {
                    "feature": X.columns,
                    "importance": self.model.feature_importances_,
                }
            ).sort_values("importance", ascending=False)

            # Log feature importance
            feature_importance.to_csv("/tmp/feature_importance.csv", index=False)
            mlflow.log_artifact("/tmp/feature_importance.csv")

            # SHAP values for model explainability
            explainer = shap.TreeExplainer(self.model)
            shap_values = explainer.shap_values(X_test.iloc[:100])

            # Log classification report
            report = classification_report(y_test, y_pred)
            with open("/tmp/classification_report.txt", "w") as f:
                f.write(report)
            mlflow.log_artifact("/tmp/classification_report.txt")

            logger.info(f"Model trained successfully. ROC-AUC: {metrics['roc_auc']:.4f}")
            logger.info(f"MLflow run ID: {mlflow.active_run().info.run_id}")

            return metrics

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """
        Predict churn probability.

        Args:
            X: Feature matrix

        Returns:
            Churn probabilities
        """
        if self.model is None:
            raise ValueError("Model not trained. Call train() first.")

        return self.model.predict_proba(X)[:, 1]

    def predict_batch(self, customers: pd.DataFrame) -> pd.DataFrame:
        """
        Predict churn for batch of customers.

        Args:
            customers: Customer data

        Returns:
            DataFrame with churn predictions
        """
        features = self.engineer_features(customers)
        churn_prob = self.predict(features)

        results = customers[["customer_id"]].copy()
        results["churn_probability"] = churn_prob
        results["churn_risk"] = pd.cut(
            churn_prob,
            bins=[0, 0.3, 0.7, 1.0],
            labels=["Low", "Medium", "High"],
        )
        results["predicted_at"] = datetime.now()

        return results

    def save(self, path: str) -> None:
        """Save model to disk."""
        import joblib

        joblib.dump(self.model, path)
        logger.info(f"Model saved to {path}")

    def load(self, path: str) -> None:
        """Load model from disk."""
        import joblib

        self.model = joblib.load(path)
        logger.info(f"Model loaded from {path}")


def main():
    """Main training pipeline."""
    logger.info("Starting churn prediction model training...")

    # In production, load data from data warehouse
    # For demo, create synthetic data
    np.random.seed(42)
    n_samples = 10000

    df = pd.DataFrame(
        {
            "customer_id": [f"CUST{i:06d}" for i in range(n_samples)],
            "customer_since": pd.date_range(end=datetime.now(), periods=n_samples, freq="D"),
            "customer_segment": np.random.choice(["VIP", "Regular", "New"], n_samples),
            "transaction_count": np.random.poisson(10, n_samples),
            "total_revenue": np.random.exponential(1000, n_samples),
            "last_transaction_date": pd.date_range(
                end=datetime.now(), periods=n_samples, freq="H"
            ),
            "login_count": np.random.poisson(20, n_samples),
            "support_ticket_count": np.random.poisson(2, n_samples),
            "mobile_app_installed": np.random.choice([True, False], n_samples),
            "referral_count": np.random.poisson(1, n_samples),
            "avg_rating": np.random.uniform(1, 5, n_samples),
            "revenue_last_30d": np.random.exponential(200, n_samples),
            "revenue_prev_30d": np.random.exponential(200, n_samples),
            "transactions_last_30d": np.random.poisson(3, n_samples),
            "transactions_prev_30d": np.random.poisson(3, n_samples),
            "churned": np.random.choice([0, 1], n_samples, p=[0.8, 0.2]),
        }
    )

    # Initialize model
    model = ChurnPredictionModel()

    # Engineer features
    X = model.engineer_features(df)
    y = df["churned"]

    # Train model
    metrics = model.train(X, y)

    logger.info("Training completed successfully!")
    logger.info(f"Metrics: {metrics}")


if __name__ == "__main__":
    main()
