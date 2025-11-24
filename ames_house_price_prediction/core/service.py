"""Prediction service that orchestrates feature transformation, preprocessing, and prediction."""

from pathlib import Path
from typing import Union

import pandas as pd

from ames_house_price_prediction.config.models import MODEL_PATH, PREPROCESSOR_PATH
from ames_house_price_prediction.core.feature_transformer import (
    HouseFeaturesTransformer,
)
from ames_house_price_prediction.core.interfaces import (
    FeatureTransformer,
    Model,
    Preprocessor,
)
from ames_house_price_prediction.core.model import RidgeRegressionModel
from ames_house_price_prediction.core.preprocessing import SklearnPreprocessor


class PredictionService:
    """Service for making house price predictions."""

    def __init__(
        self,
        feature_transformer: FeatureTransformer = None,
        preprocessor: Preprocessor = None,
        model: Model = None,
    ):
        """Initialize the prediction service.

        Args:
            feature_transformer: Feature engineering transformer
            preprocessor: Data preprocessor
            model: Prediction model
        """
        self.feature_transformer = feature_transformer or HouseFeaturesTransformer()
        self.preprocessor = preprocessor
        self.model = model

    @classmethod
    def from_files(
        cls,
        model_path: Union[str, Path] = MODEL_PATH,
        preprocessor_path: Union[str, Path] = PREPROCESSOR_PATH,
    ) -> "PredictionService":
        """Load a prediction service from saved model artifacts.

        Args:
            model_path: Path to the saved model
            preprocessor_path: Path to the saved preprocessor

        Returns:
            Initialized prediction service
        """
        preprocessor = SklearnPreprocessor.load(str(preprocessor_path))
        model = RidgeRegressionModel.load(str(model_path))

        return cls(
            feature_transformer=HouseFeaturesTransformer(),
            preprocessor=preprocessor,
            model=model,
        )

    def predict(self, data: pd.DataFrame) -> pd.Series:
        """Make predictions on input data.

        Args:
            data: Input DataFrame with raw house features

        Returns:
            Predicted house prices

        Raises:
            ValueError: If preprocessor or model is not initialized
        """
        if self.preprocessor is None:
            raise ValueError("Preprocessor must be initialized before prediction")
        if self.model is None:
            raise ValueError("Model must be initialized before prediction")

        # Apply feature engineering
        features = self.feature_transformer.transform(data)

        # Apply preprocessing
        processed = self.preprocessor.transform(features)

        # Make predictions
        predictions = self.model.predict(processed)

        return predictions

    def predict_single(self, **kwargs) -> float:
        """Make a prediction for a single house.

        Args:
            **kwargs: House features as keyword arguments

        Returns:
            Predicted house price
        """
        data = pd.DataFrame([kwargs])
        predictions = self.predict(data)
        return float(predictions.iloc[0])
