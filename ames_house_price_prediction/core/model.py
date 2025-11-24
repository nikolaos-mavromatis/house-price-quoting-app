"""Model implementation."""

import pickle
from pathlib import Path
from typing import Any

import pandas as pd
from sklearn.linear_model import Ridge

from ames_house_price_prediction.config import RIDGE_ALPHA
from ames_house_price_prediction.core.interfaces import Model


class RidgeRegressionModel(Model):
    """Ridge regression model for house price prediction."""

    def __init__(self, alpha: float = RIDGE_ALPHA):
        """Initialize the Ridge regression model.

        Args:
            alpha: Regularization strength
        """
        self.alpha = alpha
        self._model = None

    def fit(self, X: Any, y: pd.Series) -> "RidgeRegressionModel":
        """Fit the model on training data.

        Args:
            X: Training features (DataFrame or array)
            y: Training target

        Returns:
            Fitted model instance
        """
        self._model = Ridge(alpha=self.alpha)
        self._model.fit(X, y)
        return self

    def predict(self, X: Any) -> pd.Series:
        """Make predictions on input data.

        Args:
            X: Input features

        Returns:
            Predictions as Series
        """
        if self._model is None:
            raise ValueError("Model must be fitted before predict")

        predictions = self._model.predict(X)

        # Flatten predictions if necessary (handles TransformedTargetRegressor)
        if predictions.ndim > 1:
            predictions = predictions.flatten()

        return pd.Series(predictions)

    def save(self, path: str) -> None:
        """Save the fitted model to disk.

        Args:
            path: File path to save the model
        """
        if self._model is None:
            raise ValueError("Cannot save unfitted model")

        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, "wb") as f:
            pickle.dump(self._model, f, protocol=5)

    @staticmethod
    def load(path: str) -> "RidgeRegressionModel":
        """Load a fitted model from disk.

        Args:
            path: File path to load the model from

        Returns:
            Loaded model instance
        """
        with open(path, "rb") as f:
            sklearn_model = pickle.load(f)

        model = RidgeRegressionModel()
        model._model = sklearn_model

        # Extract alpha from the underlying model
        # Handle both Ridge and TransformedTargetRegressor
        if hasattr(sklearn_model, "alpha"):
            model.alpha = sklearn_model.alpha
        elif hasattr(sklearn_model, "regressor_") and hasattr(
            sklearn_model.regressor_, "alpha"
        ):
            model.alpha = sklearn_model.regressor_.alpha
        else:
            # Default to config value if can't extract
            model.alpha = RIDGE_ALPHA

        return model
