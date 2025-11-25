"""Abstract interfaces for the prediction pipeline components."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Optional, Self, Union

import pandas as pd


class FeatureTransformer(ABC):
    """Abstract base class for feature transformers."""

    @abstractmethod
    def transform(self, data: pd.DataFrame) -> pd.DataFrame:
        """Transform input data by creating or modifying features.

        Args:
            data: Input DataFrame

        Returns:
            Transformed DataFrame with new/modified features
        """
        pass


class Preprocessor(ABC):
    """Abstract base class for data preprocessors."""

    @abstractmethod
    def fit(self, X: pd.DataFrame, y: Optional[pd.Series] = None) -> Self:
        """Fit the preprocessor on training data.

        Args:
            X: Training features
            y: Training target (optional)

        Returns:
            Fitted preprocessor instance (self)
        """
        pass

    @abstractmethod
    def transform(self, X: pd.DataFrame) -> Any:
        """Transform the input data.

        Args:
            X: Input features

        Returns:
            Transformed features (typically DataFrame or ndarray)
        """
        pass

    def fit_transform(self, X: pd.DataFrame, y: Optional[pd.Series] = None) -> Any:
        """Fit and transform the data in one step.

        Args:
            X: Training features
            y: Training target (optional)

        Returns:
            Transformed features
        """
        return self.fit(X, y).transform(X)

    @abstractmethod
    def save(self, path: Union[str, Path]) -> None:
        """Save the fitted preprocessor to disk.

        Args:
            path: File path to save the preprocessor
        """
        pass

    @staticmethod
    @abstractmethod
    def load(path: Union[str, Path]) -> "Preprocessor":
        """Load a fitted preprocessor from disk.

        Args:
            path: File path to load the preprocessor from

        Returns:
            Loaded preprocessor instance
        """
        pass


class Model(ABC):
    """Abstract base class for prediction models."""

    @abstractmethod
    def fit(self, X: Any, y: pd.Series) -> Self:
        """Fit the model on training data.

        Args:
            X: Training features (can be DataFrame, array, etc.)
            y: Training target

        Returns:
            Fitted model instance (self)
        """
        pass

    @abstractmethod
    def predict(self, X: Any) -> pd.Series:
        """Make predictions on input data.

        Args:
            X: Input features

        Returns:
            Predictions as a pandas Series
        """
        pass

    @abstractmethod
    def save(self, path: Union[str, Path]) -> None:
        """Save the fitted model to disk.

        Args:
            path: File path to save the model
        """
        pass

    @staticmethod
    @abstractmethod
    def load(path: Union[str, Path]) -> "Model":
        """Load a fitted model from disk.

        Args:
            path: File path to load the model from

        Returns:
            Loaded model instance
        """
        pass
