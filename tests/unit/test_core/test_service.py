"""Unit tests for PredictionService."""

import pandas as pd
import pytest

from ames_house_price_prediction.core.service import PredictionService


@pytest.mark.unit
class TestPredictionService:
    """Test suite for PredictionService."""

    def test_initialization_with_components(
        self, mock_feature_transformer, mock_preprocessor, mock_model
    ):
        """Test initialization with provided components."""
        service = PredictionService(
            feature_transformer=mock_feature_transformer,
            preprocessor=mock_preprocessor,
            model=mock_model,
        )

        assert service.feature_transformer is mock_feature_transformer
        assert service.preprocessor is mock_preprocessor
        assert service.model is mock_model

    def test_initialization_with_default_transformer(
        self, mock_preprocessor, mock_model
    ):
        """Test that default feature transformer is created if not provided."""
        service = PredictionService(preprocessor=mock_preprocessor, model=mock_model)

        from ames_house_price_prediction.core.feature_transformer import (
            HouseFeaturesTransformer,
        )

        assert isinstance(service.feature_transformer, HouseFeaturesTransformer)

    def test_predict_without_preprocessor_raises_error(
        self, mock_feature_transformer, mock_model, sample_input_dataframe
    ):
        """Test that predict without preprocessor raises ValueError."""
        service = PredictionService(
            feature_transformer=mock_feature_transformer,
            preprocessor=None,
            model=mock_model,
        )

        with pytest.raises(ValueError, match="Preprocessor must be initialized"):
            service.predict(sample_input_dataframe)

    def test_predict_without_model_raises_error(
        self, mock_feature_transformer, mock_preprocessor, sample_input_dataframe
    ):
        """Test that predict without model raises ValueError."""
        mock_preprocessor.fit(sample_input_dataframe)
        service = PredictionService(
            feature_transformer=mock_feature_transformer,
            preprocessor=mock_preprocessor,
            model=None,
        )

        with pytest.raises(ValueError, match="Model must be initialized"):
            service.predict(sample_input_dataframe)

    def test_predict_returns_series(
        self, mock_prediction_service, sample_input_dataframe
    ):
        """Test that predict returns a pandas Series."""
        predictions = mock_prediction_service.predict(sample_input_dataframe)

        assert isinstance(predictions, pd.Series)

    def test_predict_correct_length(self, mock_prediction_service):
        """Test that predict returns correct number of predictions."""
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
            ]
        )

        predictions = mock_prediction_service.predict(data)

        assert len(predictions) == 2

    def test_predict_single_returns_float(self, mock_prediction_service):
        """Test that predict_single returns a single float value."""
        prediction = mock_prediction_service.predict_single(
            LotArea=8450,
            YearBuilt=2003,
            YearRemodAdd=2003,
            YrSold=2008,
            OverallQual=7,
            OverallCond=5,
        )

        assert isinstance(prediction, float)

    def test_predict_single_with_kwargs(self, mock_prediction_service):
        """Test that predict_single works with keyword arguments."""
        prediction = mock_prediction_service.predict_single(
            LotArea=8450,
            YearBuilt=2003,
            YearRemodAdd=2003,
            YrSold=2008,
            OverallQual=7,
            OverallCond=5,
        )

        assert prediction > 0

    def test_prediction_pipeline_integration(
        self,
        mock_feature_transformer,
        mock_preprocessor,
        mock_model,
        sample_input_dataframe,
    ):
        """Test that prediction flows through all components."""
        # Track if components are called
        transform_called = False
        preprocess_called = False
        predict_called = False

        original_transform = mock_feature_transformer.transform
        original_preprocess_transform = mock_preprocessor.transform
        original_predict = mock_model.predict

        def track_transform(data):
            nonlocal transform_called
            transform_called = True
            return original_transform(data)

        def track_preprocess(data):
            nonlocal preprocess_called
            preprocess_called = True
            return original_preprocess_transform(data)

        def track_predict(data):
            nonlocal predict_called
            predict_called = True
            return original_predict(data)

        mock_feature_transformer.transform = track_transform
        mock_preprocessor.transform = track_preprocess
        mock_model.predict = track_predict

        # Fit preprocessor first
        mock_preprocessor.fit(sample_input_dataframe)

        service = PredictionService(
            feature_transformer=mock_feature_transformer,
            preprocessor=mock_preprocessor,
            model=mock_model,
        )

        service.predict(sample_input_dataframe)

        assert transform_called, "Feature transformer was not called"
        assert preprocess_called, "Preprocessor was not called"
        assert predict_called, "Model was not called"

    def test_from_files_loads_components(self, monkeypatch, temp_model_dir):
        """Test that from_files class method loads components."""
        # Create dummy files
        (temp_model_dir / "model.pkl").touch()
        (temp_model_dir / "preprocessor.pkl").touch()

        # Mock the load methods
        load_preprocessor_called = False
        load_model_called = False

        def mock_load_preprocessor(path):
            nonlocal load_preprocessor_called
            load_preprocessor_called = True
            from tests.conftest import pytest

            # Return a mock preprocessor
            class MockPrep:
                def transform(self, X):
                    return X.values if hasattr(X, "values") else X

            return MockPrep()

        def mock_load_model(path):
            nonlocal load_model_called
            load_model_called = True

            class MockMod:
                def predict(self, X):
                    return pd.Series([200000.0])

            return MockMod()

        monkeypatch.setattr(
            "ames_house_price_prediction.core.preprocessing.SklearnPreprocessor.load",
            mock_load_preprocessor,
        )
        monkeypatch.setattr(
            "ames_house_price_prediction.core.model.RidgeRegressionModel.load",
            mock_load_model,
        )

        service = PredictionService.from_files(
            model_path=temp_model_dir / "model.pkl",
            preprocessor_path=temp_model_dir / "preprocessor.pkl",
        )

        assert load_preprocessor_called
        assert load_model_called
        assert service.preprocessor is not None
        assert service.model is not None

    def test_predict_single_converts_to_dataframe(self, mock_prediction_service):
        """Test that predict_single internally converts kwargs to DataFrame."""
        # This implicitly tests the conversion by verifying it works
        result = mock_prediction_service.predict_single(
            LotArea=8450,
            YearBuilt=2003,
            YearRemodAdd=2003,
            YrSold=2008,
            OverallQual=7,
            OverallCond=5,
        )

        assert isinstance(result, float)
        assert result == 200000.0  # Mock model returns this value

    def test_multiple_predictions_same_service(self, mock_prediction_service):
        """Test that same service can make multiple predictions."""
        data1 = pd.DataFrame(
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
        data2 = pd.DataFrame(
            [
                {
                    "LotArea": 9600,
                    "YearBuilt": 1976,
                    "YearRemodAdd": 1976,
                    "YrSold": 2007,
                    "OverallQual": 6,
                    "OverallCond": 8,
                }
            ]
        )

        pred1 = mock_prediction_service.predict(data1)
        pred2 = mock_prediction_service.predict(data2)

        assert isinstance(pred1, pd.Series)
        assert isinstance(pred2, pd.Series)
        assert len(pred1) == 1
        assert len(pred2) == 1
