"""End-to-end tests for the complete ML pipeline."""

from pathlib import Path

import pandas as pd
import pytest

from ames_house_price_prediction.core.feature_transformer import (
    HouseFeaturesTransformer,
)
from ames_house_price_prediction.core.model import RidgeRegressionModel
from ames_house_price_prediction.core.preprocessing import SklearnPreprocessor
from ames_house_price_prediction.core.service import PredictionService


@pytest.mark.e2e
@pytest.mark.slow
class TestCompletePipeline:
    """End-to-end tests that simulate the full workflow."""

    def test_complete_training_and_prediction_workflow(
        self, sample_raw_data, temp_model_dir, temp_data_dir
    ):
        """Test the complete workflow from raw data to prediction."""
        # Step 1: Data Preparation
        train_data = sample_raw_data.copy()
        X_train = train_data.drop("SalePrice", axis=1)
        y_train = train_data["SalePrice"]

        # Step 2: Feature Engineering
        transformer = HouseFeaturesTransformer()
        X_features = transformer.transform(X_train)

        # Verify features were created
        assert "LotAge" in X_features.columns
        assert "YearsSinceRemod" in X_features.columns

        # Step 3: Preprocessing
        preprocessor = SklearnPreprocessor()
        X_processed = preprocessor.fit_transform(X_features)

        # Verify preprocessing worked
        assert X_processed.shape[0] == len(X_train)
        assert X_processed.shape[1] > X_features.shape[1]  # Polynomial features

        # Step 4: Model Training
        model = RidgeRegressionModel()
        model.fit(X_processed, y_train)

        # Step 5: Save Artifacts
        model_path = temp_model_dir / "model.pkl"
        preprocessor_path = temp_model_dir / "preprocessor.pkl"

        model.save(str(model_path))
        preprocessor.save(str(preprocessor_path))

        # Verify artifacts were saved
        assert model_path.exists()
        assert preprocessor_path.exists()

        # Step 6: Load Service for Prediction
        service = PredictionService.from_files(
            model_path=model_path, preprocessor_path=preprocessor_path
        )

        # Step 7: Make Predictions on New Data
        new_house = pd.DataFrame(
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

        prediction = service.predict(new_house)

        # Verify prediction
        assert isinstance(prediction, pd.Series)
        assert len(prediction) == 1
        assert prediction.iloc[0] > 0

        # Step 8: Batch Predictions
        batch_data = pd.DataFrame(
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

        batch_predictions = service.predict(batch_data)

        assert len(batch_predictions) == 3
        assert all(batch_predictions > 0)

    def test_pipeline_with_data_persisting(
        self, sample_raw_data, temp_model_dir, temp_data_dir
    ):
        """Test pipeline with saving and loading data at each step."""
        # Step 1: Save raw data
        raw_data_path = temp_data_dir / "raw" / "train.csv"
        sample_raw_data.to_csv(raw_data_path, index=False)

        # Step 2: Load and prepare data
        loaded_data = pd.read_csv(raw_data_path)
        X = loaded_data.drop("SalePrice", axis=1)
        y = loaded_data["SalePrice"]

        # Step 3: Feature engineering and save
        transformer = HouseFeaturesTransformer()
        features = transformer.transform(X)
        features_path = temp_data_dir / "processed" / "features.parquet"
        features.to_parquet(features_path, index=False)

        # Step 4: Load features and preprocess
        loaded_features = pd.read_parquet(features_path)
        preprocessor = SklearnPreprocessor()
        X_processed = preprocessor.fit_transform(loaded_features)

        # Step 5: Train and save model
        model = RidgeRegressionModel()
        model.fit(X_processed, y)

        model_path = temp_model_dir / "model.pkl"
        preprocessor_path = temp_model_dir / "preprocessor.pkl"
        model.save(str(model_path))
        preprocessor.save(str(preprocessor_path))

        # Step 6: Fresh service from files
        service = PredictionService.from_files(
            model_path=model_path, preprocessor_path=preprocessor_path
        )

        # Step 7: Predict
        test_data = pd.DataFrame([X.iloc[0].to_dict()])
        prediction = service.predict(test_data)

        assert len(prediction) == 1
        assert prediction.iloc[0] > 0

    def test_model_quality_on_training_data(self, sample_raw_data):
        """Test that model achieves reasonable performance on training data."""
        X = sample_raw_data.drop("SalePrice", axis=1)
        y = sample_raw_data["SalePrice"]

        # Train pipeline
        transformer = HouseFeaturesTransformer()
        features = transformer.transform(X)

        preprocessor = SklearnPreprocessor()
        X_processed = preprocessor.fit_transform(features)

        model = RidgeRegressionModel()
        model.fit(X_processed, y)

        # Predict on training data
        predictions = model.predict(X_processed)

        # Calculate simple error metrics
        errors = abs(predictions - y)
        mean_error = errors.mean()

        # Mean error should be less than 50% of mean price
        assert mean_error < y.mean() * 0.5

        # At least some predictions should be reasonably close
        close_predictions = (errors < y.mean() * 0.2).sum()
        assert close_predictions > len(y) * 0.3  # At least 30% within 20%

    def test_pipeline_handles_edge_cases(self, temp_model_dir):
        """Test that pipeline handles various edge cases."""
        # Create minimal training data with edge cases
        train_data = pd.DataFrame(
            {
                "LotArea": [5000, 20000, 8450],
                "YearBuilt": [1850, 2020, 2000],
                "YearRemodAdd": [1850, 2022, 2000],
                "YrSold": [2024, 2024, 2024],
                "OverallQual": [1, 10, 5],
                "OverallCond": [1, 10, 5],
                "SalePrice": [100000, 500000, 250000],
            }
        )

        X = train_data.drop("SalePrice", axis=1)
        y = train_data["SalePrice"]

        # Train
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

        # Test edge cases
        edge_cases = [
            # Very old house
            {
                "LotArea": 8000,
                "YearBuilt": 1800,
                "YearRemodAdd": 1800,
                "YrSold": 2024,
                "OverallQual": 3,
                "OverallCond": 3,
            },
            # Brand new house
            {
                "LotArea": 8000,
                "YearBuilt": 2024,
                "YearRemodAdd": 2024,
                "YrSold": 2024,
                "OverallQual": 9,
                "OverallCond": 9,
            },
            # Minimum quality
            {
                "LotArea": 8000,
                "YearBuilt": 2000,
                "YearRemodAdd": 2000,
                "YrSold": 2024,
                "OverallQual": 1,
                "OverallCond": 1,
            },
            # Maximum quality
            {
                "LotArea": 8000,
                "YearBuilt": 2000,
                "YearRemodAdd": 2000,
                "YrSold": 2024,
                "OverallQual": 10,
                "OverallCond": 10,
            },
        ]

        for case in edge_cases:
            prediction = service.predict_single(**case)
            assert prediction > 0, f"Failed on case: {case}"

    def test_reproducibility(self, sample_raw_data, temp_model_dir):
        """Test that the pipeline produces reproducible results."""
        X = sample_raw_data.drop("SalePrice", axis=1)
        y = sample_raw_data["SalePrice"]
        X = sample_raw_data.drop("SalePrice", axis=1)
        y = sample_raw_data["SalePrice"]
        y = sample_raw_data['SalePrice']

        # Train first model
        transformer1 = HouseFeaturesTransformer()
        features1 = transformer1.transform(X)
        preprocessor1 = SklearnPreprocessor()
        X_processed1 = preprocessor1.fit_transform(features1)
        model1 = RidgeRegressionModel(alpha=8.5)
        model1.fit(X_processed1, y)

        # Train second model (same way)
        transformer2 = HouseFeaturesTransformer()
        features2 = transformer2.transform(X)
        preprocessor2 = SklearnPreprocessor()
        X_processed2 = preprocessor2.fit_transform(features2)
        model2 = RidgeRegressionModel(alpha=8.5)
        model2.fit(X_processed2, y)

        # Predictions should be identical
        pred1 = model1.predict(X_processed1)
        pred2 = model2.predict(X_processed2)

        pd.testing.assert_series_equal(pred1, pred2, check_names=False)
