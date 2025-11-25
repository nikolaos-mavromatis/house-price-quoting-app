"""Unit tests for RidgeRegressionModel."""

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from ames_house_price_prediction.core.model import RidgeRegressionModel


@pytest.mark.unit
class TestRidgeRegressionModel:
    """Test suite for RidgeRegressionModel."""

    @pytest.fixture
    def model(self):
        """Create a model instance."""
        return RidgeRegressionModel()

    @pytest.fixture
    def sample_X(self):
        """Sample training features."""
        return np.array(
            [[1, 2, 3, 4, 5], [2, 3, 4, 5, 6], [3, 4, 5, 6, 7], [4, 5, 6, 7, 8]]
        )

    @pytest.fixture
    def sample_y(self):
        """Sample training targets."""
        return pd.Series([100000, 150000, 200000, 250000])

    def test_initialization_default_alpha(self, model):
        """Test that model initializes with default alpha."""
        from ames_house_price_prediction.config.models import RIDGE_ALPHA

        assert model.alpha == RIDGE_ALPHA
        assert model._model is None

    def test_initialization_custom_alpha(self):
        """Test initialization with custom alpha."""
        model = RidgeRegressionModel(alpha=5.0)

        assert model.alpha == 5.0

    def test_fit_creates_internal_model(self, model, sample_X, sample_y):
        """Test that fit creates the internal Ridge model."""
        model.fit(sample_X, sample_y)

        assert model._model is not None
        from sklearn.linear_model import Ridge

        assert isinstance(model._model, Ridge)

    def test_fit_returns_self(self, model, sample_X, sample_y):
        """Test that fit returns self for method chaining."""
        result = model.fit(sample_X, sample_y)

        assert result is model

    def test_predict_before_fit_raises_error(self, model, sample_X):
        """Test that predict before fit raises ValueError."""
        with pytest.raises(ValueError, match="must be fitted"):
            model.predict(sample_X)

    def test_predict_after_fit_returns_series(self, model, sample_X, sample_y):
        """Test that predict returns a pandas Series."""
        model.fit(sample_X, sample_y)
        predictions = model.predict(sample_X)

        assert isinstance(predictions, pd.Series)
        assert len(predictions) == len(sample_X)

    def test_predict_reasonable_values(self, model, sample_X, sample_y):
        """Test that predictions are in reasonable range."""
        model.fit(sample_X, sample_y)
        predictions = model.predict(sample_X)

        # Predictions should be positive
        assert all(predictions > 0)
        # Should be in ballpark of training data
        assert predictions.min() >= sample_y.min() * 0.5
        assert predictions.max() <= sample_y.max() * 2.0

    def test_save_before_fit_raises_error(self, model, tmp_path):
        """Test that save before fit raises ValueError."""
        path = tmp_path / "model.pkl"

        with pytest.raises(ValueError, match="Cannot save unfitted"):
            model.save(str(path))

    def test_save_after_fit(self, model, sample_X, sample_y, tmp_path):
        """Test that model can be saved after fitting."""
        model.fit(sample_X, sample_y)
        path = tmp_path / "model.pkl"

        model.save(str(path))

        assert path.exists()
        assert path.stat().st_size > 0

    def test_load_saved_model(self, model, sample_X, sample_y, tmp_path):
        """Test that saved model can be loaded."""
        # Fit and save
        model.fit(sample_X, sample_y)
        path = tmp_path / "model.pkl"
        model.save(str(path))

        # Load
        loaded = RidgeRegressionModel.load(str(path))

        assert loaded._model is not None
        assert isinstance(loaded, RidgeRegressionModel)

    def test_save_load_predictions_match(self, model, sample_X, sample_y, tmp_path):
        """Test that loaded model produces same predictions."""
        # Fit and predict
        model.fit(sample_X, sample_y)
        original_predictions = model.predict(sample_X)

        # Save and load
        path = tmp_path / "model.pkl"
        model.save(str(path))
        loaded = RidgeRegressionModel.load(str(path))

        # Predict with loaded model
        loaded_predictions = loaded.predict(sample_X)

        # Predictions should match
        pd.testing.assert_series_equal(original_predictions, loaded_predictions)

    def test_save_creates_parent_directory(self, model, sample_X, sample_y, tmp_path):
        """Test that save creates parent directories if needed."""
        model.fit(sample_X, sample_y)
        path = tmp_path / "nested" / "dir" / "model.pkl"

        model.save(str(path))

        assert path.exists()

    def test_alpha_extraction_from_simple_model(
        self, model, sample_X, sample_y, tmp_path
    ):
        """Test alpha extraction from simple Ridge model."""
        model.fit(sample_X, sample_y)
        path = tmp_path / "model.pkl"
        model.save(str(path))

        loaded = RidgeRegressionModel.load(str(path))

        assert loaded.alpha == model.alpha

    def test_alpha_extraction_from_transformed_target_regressor(
        self, sample_X, sample_y, tmp_path
    ):
        """Test alpha extraction from TransformedTargetRegressor."""
        import pickle

        from sklearn.compose import TransformedTargetRegressor
        from sklearn.linear_model import Ridge
        from sklearn.preprocessing import QuantileTransformer

        # Create a TransformedTargetRegressor (like in training script)
        transformer = QuantileTransformer()
        ridge = Ridge(alpha=8.5)
        wrapped_model = TransformedTargetRegressor(
            regressor=ridge, transformer=transformer
        )
        wrapped_model.fit(sample_X, sample_y)

        # Save it
        path = tmp_path / "wrapped_model.pkl"
        with open(path, "wb") as f:
            pickle.dump(wrapped_model, f)

        # Load with our wrapper
        loaded = RidgeRegressionModel.load(str(path))

        # Should extract alpha from inner regressor
        assert loaded.alpha == 8.5

    def test_prediction_flattening_for_2d_output(self, sample_X, sample_y, tmp_path):
        """Test that 2D predictions are flattened to 1D Series."""
        import pickle

        from sklearn.compose import TransformedTargetRegressor
        from sklearn.linear_model import Ridge
        from sklearn.preprocessing import QuantileTransformer

        # Create wrapped model that returns 2D predictions
        transformer = QuantileTransformer()
        ridge = Ridge(alpha=8.5)
        wrapped_model = TransformedTargetRegressor(
            regressor=ridge, transformer=transformer
        )
        wrapped_model.fit(sample_X, sample_y)

        # Save and load
        path = tmp_path / "model.pkl"
        with open(path, "wb") as f:
            pickle.dump(wrapped_model, f)

        model = RidgeRegressionModel.load(str(path))

        # Predict
        predictions = model.predict(sample_X)

        # Should be 1D Series, not 2D
        assert isinstance(predictions, pd.Series)
        assert predictions.ndim == 1
        assert len(predictions) == len(sample_X)

    def test_fit_with_dataframe_input(self, model, sample_y):
        """Test fitting with DataFrame input."""
        X_df = pd.DataFrame(
            {
                "feature1": [1, 2, 3, 4],
                "feature2": [2, 3, 4, 5],
                "feature3": [3, 4, 5, 6],
            }
        )

        model.fit(X_df, sample_y)
        predictions = model.predict(X_df)

        assert isinstance(predictions, pd.Series)
        assert len(predictions) == len(X_df)

    def test_predict_single_sample(self, model, sample_X, sample_y):
        """Test prediction with single sample."""
        model.fit(sample_X, sample_y)

        single_sample = sample_X[[0]]  # Single row as 2D array
        predictions = model.predict(single_sample)

        assert len(predictions) == 1
        assert isinstance(predictions, pd.Series)

    def test_regularization_effect(self, sample_X, sample_y):
        """Test that different alpha values produce different models."""
        model_weak = RidgeRegressionModel(alpha=0.1)
        model_strong = RidgeRegressionModel(alpha=100.0)

        model_weak.fit(sample_X, sample_y)
        model_strong.fit(sample_X, sample_y)

        pred_weak = model_weak.predict(sample_X)
        pred_strong = model_strong.predict(sample_X)

        # Different regularization should produce different predictions
        assert not pred_weak.equals(pred_strong)
