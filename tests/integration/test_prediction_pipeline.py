"""Integration tests for the complete prediction pipeline."""

import pandas as pd
import pytest

from ames_house_price_prediction.core.feature_transformer import (
    HouseFeaturesTransformer,
)
from ames_house_price_prediction.core.model import RidgeRegressionModel
from ames_house_price_prediction.core.preprocessing import SklearnPreprocessor
from ames_house_price_prediction.core.service import PredictionService


@pytest.mark.integration
class TestPredictionPipeline:
    """Integration tests for the full prediction pipeline with real components."""

    @pytest.fixture
    def trained_service(self, sample_raw_data):
        """Create a fully trained prediction service with real components."""
        # Extract features and target
        X = sample_raw_data.drop("SalePrice", axis=1)
        y = sample_raw_data["SalePrice"]

        # Create and fit components
        transformer = HouseFeaturesTransformer()
        features = transformer.transform(X)

        preprocessor = SklearnPreprocessor()
        X_processed = preprocessor.fit_transform(features)

        model = RidgeRegressionModel()
        model.fit(X_processed, y)

        # Create service
        service = PredictionService(
            feature_transformer=transformer, preprocessor=preprocessor, model=model
        )

        return service

    def test_predict_returns_series(self, trained_service, sample_raw_data):
        """Test that predict returns a pandas Series."""
        X = sample_raw_data.drop("SalePrice", axis=1).head(2)

        predictions = trained_service.predict(X)

        assert isinstance(predictions, pd.Series)
        assert len(predictions) == len(X)

    def test_predict_single_returns_float(self, trained_service):
        """Test that predict_single returns a float."""
        prediction = trained_service.predict_single(
            LotArea=8450,
            YearBuilt=2003,
            YearRemodAdd=2003,
            YrSold=2008,
            OverallQual=7,
            OverallCond=5,
        )

        assert isinstance(prediction, float)
        assert prediction > 0

    def test_predictions_are_positive(self, trained_service, sample_raw_data):
        """Test that all predictions are positive values."""
        X = sample_raw_data.drop("SalePrice", axis=1)

        predictions = trained_service.predict(X)

        assert all(predictions > 0)

    def test_predictions_in_reasonable_range(self, trained_service, sample_raw_data):
        """Test that predictions are in reasonable price range."""
        X = sample_raw_data.drop("SalePrice", axis=1)
        y = sample_raw_data["SalePrice"]

        predictions = trained_service.predict(X)

        # Predictions should be within reasonable bounds of training data
        assert predictions.min() >= y.min() * 0.3  # Not too low
        assert predictions.max() <= y.max() * 3.0  # Not too high

    def test_save_load_roundtrip(
        self, trained_service, sample_raw_data, temp_model_dir
    ):
        """Test that service components can be saved and loaded."""
        # Save components
        model_path = temp_model_dir / "model.pkl"
        preprocessor_path = temp_model_dir / "preprocessor.pkl"

        trained_service.model.save(str(model_path))
        trained_service.preprocessor.save(str(preprocessor_path))

        # Load new service
        loaded_service = PredictionService.from_files(
            model_path=model_path, preprocessor_path=preprocessor_path
        )

        # Compare predictions
        X = sample_raw_data.drop("SalePrice", axis=1).head(1)
        original_pred = trained_service.predict(X)
        loaded_pred = loaded_service.predict(X)

        pd.testing.assert_series_equal(original_pred, loaded_pred, check_names=False)

    def test_batch_prediction_consistency(self, trained_service):
        """Test that batch and single predictions are consistent."""
        house_data = {
            "LotArea": 8450,
            "YearBuilt": 2003,
            "YearRemodAdd": 2003,
            "YrSold": 2008,
            "OverallQual": 7,
            "OverallCond": 5,
        }

        # Single prediction
        single_pred = trained_service.predict_single(**house_data)

        # Batch prediction
        batch_data = pd.DataFrame([house_data])
        batch_pred = trained_service.predict(batch_data)

        # Should be very close (allowing for floating point differences)
        assert abs(single_pred - batch_pred.iloc[0]) < 0.01

    def test_higher_quality_predicts_higher_price(self, trained_service):
        """Test that higher quality houses predict higher prices."""
        low_quality = trained_service.predict_single(
            LotArea=8000,
            YearBuilt=2000,
            YearRemodAdd=2000,
            YrSold=2010,
            OverallQual=3,  # Low quality
            OverallCond=3,
        )

        high_quality = trained_service.predict_single(
            LotArea=8000,
            YearBuilt=2000,
            YearRemodAdd=2000,
            YrSold=2010,
            OverallQual=9,  # High quality
            OverallCond=9,
        )

        assert high_quality > low_quality

    def test_lot_size_affects_price(self, trained_service):
        """Test that lot size affects price predictions."""
        small_lot = trained_service.predict_single(
            LotArea=5000,  # Small lot
            YearBuilt=2000,
            YearRemodAdd=2000,
            YrSold=2010,
            OverallQual=7,
            OverallCond=7,
        )

        large_lot = trained_service.predict_single(
            LotArea=15000,  # Large lot
            YearBuilt=2000,
            YearRemodAdd=2000,
            YrSold=2010,
            OverallQual=7,
            OverallCond=7,
        )

        # Predictions should be different (lot size is a feature)
        assert small_lot != large_lot

    def test_feature_engineering_applied(self, trained_service):
        """Test that feature engineering is applied before prediction."""
        # Verify that the service has a feature transformer
        assert trained_service.feature_transformer is not None

        # Make a prediction that requires feature engineering
        data = pd.DataFrame(
            [
                {
                    "LotArea": 8450,
                    "YearBuilt": 2003,
                    "YearRemodAdd": 2003,
                    "YrSold": 2008,
                    "OverallQual": 7,
                    "OverallCond": 5,
                }
            ]
        )

        # This should work even though LotAge and YearsSinceRemod aren't in input
        predictions = trained_service.predict(data)

        assert len(predictions) == 1
        assert predictions.iloc[0] > 0

    def test_multiple_houses_prediction(self, trained_service):
        """Test prediction on multiple houses at once."""
        data = pd.DataFrame(
            [
                {
                    "LotArea": 8450,
                    "YearBuilt": 2003,
                    "YearRemodAdd": 2003,
                    "YrSold": 2008,
                    "OverallQual": 7,
                    "OverallCond": 5,
                },
                {
                    "LotArea": 9600,
                    "YearBuilt": 1976,
                    "YearRemodAdd": 1976,
                    "YrSold": 2007,
                    "OverallQual": 6,
                    "OverallCond": 8,
                },
                {
                    "LotArea": 11250,
                    "YearBuilt": 2001,
                    "YearRemodAdd": 2002,
                    "YrSold": 2008,
                    "OverallQual": 7,
                    "OverallCond": 5,
                },
            ]
        )

        predictions = trained_service.predict(data)

        assert len(predictions) == 3
        assert all(predictions > 0)
        # Each prediction should be different
        assert len(predictions.unique()) == 3

    def test_preprocessor_polynomial_features(self, trained_service, sample_raw_data):
        """Test that polynomial features are being generated."""
        X = sample_raw_data.drop("SalePrice", axis=1).head(1)

        # Transform features
        features = trained_service.feature_transformer.transform(X)

        # Preprocess
        processed = trained_service.preprocessor.transform(features)

        # Should have more features than input due to polynomial expansion
        assert processed.shape[1] > features.shape[1]

    def test_service_from_files_integration(
        self, trained_service, sample_raw_data, temp_model_dir
    ):
        """Test loading service from files works end-to-end."""
        # Save components
        model_path = temp_model_dir / "model.pkl"
        preprocessor_path = temp_model_dir / "preprocessor.pkl"

        trained_service.model.save(str(model_path))
        trained_service.preprocessor.save(str(preprocessor_path))

        # Load service from files
        loaded_service = PredictionService.from_files(
            model_path=model_path, preprocessor_path=preprocessor_path
        )

        # Make prediction
        X = sample_raw_data.drop("SalePrice", axis=1).head(1)
        # Make prediction
        X = sample_raw_data.drop("SalePrice", axis=1).head(1)
        prediction = loaded_service.predict(X)

        assert isinstance(prediction, pd.Series)
        assert len(prediction) == 1
        assert prediction.iloc[0] > 0
