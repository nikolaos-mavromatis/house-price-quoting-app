"""Preprocessing pipeline implementation."""

import pickle
from pathlib import Path
from typing import Any

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import (
    OneHotEncoder,
    OrdinalEncoder,
    PolynomialFeatures,
    RobustScaler,
)

from ames_house_price_prediction.config import (
    CAT_FEATURES,
    NUM_FEATURES,
    ORD_FEATURES,
    POLY_DEGREE,
    POLY_INCLUDE_BIAS,
)
from ames_house_price_prediction.core.interfaces import Preprocessor


class SklearnPreprocessor(Preprocessor):
    """Scikit-learn based preprocessing pipeline."""

    def __init__(
        self,
        num_features: list[str] = None,
        ord_features: list[str] = None,
        cat_features: list[str] = None,
        poly_degree: int = POLY_DEGREE,
        poly_include_bias: bool = POLY_INCLUDE_BIAS,
    ):
        """Initialize the preprocessor.

        Args:
            num_features: List of numerical feature names
            ord_features: List of ordinal feature names
            cat_features: List of categorical feature names
            poly_degree: Degree for polynomial features
            poly_include_bias: Whether to include bias term in polynomial features
        """
        self.num_features = num_features or NUM_FEATURES
        self.ord_features = ord_features or ORD_FEATURES
        self.cat_features = cat_features or CAT_FEATURES
        self.poly_degree = poly_degree
        self.poly_include_bias = poly_include_bias
        self._pipeline = None

    def _build_pipeline(self) -> Pipeline:
        """Build the preprocessing pipeline."""
        # Numerical features: impute missing values and scale
        numeric_transformer = Pipeline(
            steps=[
                ("imputer", SimpleImputer(strategy="median")),
                ("scaler", RobustScaler()),
            ]
        )

        # Ordinal features: encode ordinal categories
        ordinal_transformer = Pipeline(
            steps=[
                (
                    "ord_encoding",
                    OrdinalEncoder(
                        dtype=int,
                        categories=len(self.ord_features)
                        * [["Po", "Fa", "TA", "Gd", "Ex"]],
                        handle_unknown="use_encoded_value",
                        unknown_value=-1,
                    ),
                )
            ]
        )

        # Categorical features: one-hot encode
        categorical_transformer = Pipeline(
            steps=[
                ("oh_encoding", OneHotEncoder(drop="first", sparse_output=False)),
            ]
        )

        # Combine transformers
        preprocessor = ColumnTransformer(
            transformers=[
                ("num", numeric_transformer, self.num_features),
                ("ord", ordinal_transformer, self.ord_features),
                ("cat", categorical_transformer, self.cat_features),
            ],
            remainder="drop",
            verbose_feature_names_out=False,
        )

        # Full pipeline with polynomial features
        pipeline = Pipeline(
            steps=[
                ("preprocessor", preprocessor),
                (
                    "poly",
                    PolynomialFeatures(
                        degree=self.poly_degree, include_bias=self.poly_include_bias
                    ),
                ),
            ]
        )

        return pipeline

    def fit(self, X: pd.DataFrame, y: pd.Series = None) -> "SklearnPreprocessor":
        """Fit the preprocessor on training data.

        Args:
            X: Training features
            y: Training target (optional, not used)

        Returns:
            Fitted preprocessor instance
        """
        self._pipeline = self._build_pipeline()
        self._pipeline.fit(X, y)
        return self

    def transform(self, X: pd.DataFrame) -> Any:
        """Transform the input data.

        Args:
            X: Input features

        Returns:
            Transformed features as DataFrame
        """
        if self._pipeline is None:
            raise ValueError("Preprocessor must be fitted before transform")

        transformed = self._pipeline.transform(X)
        feature_names = self._pipeline.get_feature_names_out()
        return pd.DataFrame(transformed, columns=feature_names)

    def save(self, path: str) -> None:
        """Save the fitted preprocessor to disk.

        Args:
            path: File path to save the preprocessor
        """
        if self._pipeline is None:
            raise ValueError("Cannot save unfitted preprocessor")

        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, "wb") as f:
            pickle.dump(self._pipeline, f, protocol=5)

    @staticmethod
    def load(path: str) -> "SklearnPreprocessor":
        """Load a fitted preprocessor from disk.

        Args:
            path: File path to load the preprocessor from

        Returns:
            Loaded preprocessor instance
        """
        with open(path, "rb") as f:
            pipeline = pickle.load(f)

        preprocessor = SklearnPreprocessor()
        preprocessor._pipeline = pipeline

        # Extract configuration from loaded pipeline
        if hasattr(pipeline, "named_steps"):
            column_transformer = pipeline.named_steps.get("preprocessor")
            if column_transformer:
                for name, transformer, features in column_transformer.transformers_:
                    if name == "num":
                        preprocessor.num_features = features
                    elif name == "ord":
                        preprocessor.ord_features = features
                    elif name == "cat":
                        preprocessor.cat_features = features

            poly = pipeline.named_steps.get("poly")
            if poly:
                preprocessor.poly_degree = poly.degree
                preprocessor.poly_include_bias = poly.include_bias

        return preprocessor
