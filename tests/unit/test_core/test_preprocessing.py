"""Unit tests for SklearnPreprocessor."""

import pickle
from pathlib import Path

import pandas as pd
import pytest

from ames_house_price_prediction.core.preprocessing import SklearnPreprocessor


@pytest.mark.unit
class TestSklearnPreprocessor:
    """Test suite for SklearnPreprocessor."""

    @pytest.fixture
    def preprocessor(self):
        """Create a preprocessor instance."""
        return SklearnPreprocessor()

    @pytest.fixture
    def sample_data(self):
        """Sample data for fitting."""
        return pd.DataFrame(
            {
                "LotArea": [8450, 9600, 11250],
                "LotAge": [5, 31, 7],
                "OverallQual": [7, 6, 7],
                "OverallCond": [5, 8, 5],
                "YearsSinceRemod": [5, -1, 6],
            }
        )

    def test_initialization_default_features(self, preprocessor):
        """Test that preprocessor initializes with default features."""
        from ames_house_price_prediction.config.features import NUM_FEATURES

        assert preprocessor.num_features == NUM_FEATURES
        assert preprocessor.poly_degree == 2
        assert preprocessor._pipeline is None

    def test_initialization_custom_features(self):
        """Test initialization with custom feature lists."""
        custom_features = ["feature1", "feature2"]
        preprocessor = SklearnPreprocessor(num_features=custom_features)

        assert preprocessor.num_features == custom_features

    def test_fit_creates_pipeline(self, preprocessor, sample_data):
        """Test that fit creates the internal pipeline."""
        preprocessor.fit(sample_data)

        assert preprocessor._pipeline is not None
        assert hasattr(preprocessor._pipeline, "named_steps")

    def test_fit_returns_self(self, preprocessor, sample_data):
        """Test that fit returns self for method chaining."""
        result = preprocessor.fit(sample_data)

        assert result is preprocessor

    def test_transform_before_fit_raises_error(self, preprocessor, sample_data):
        """Test that transform before fit raises ValueError."""
        with pytest.raises(ValueError, match="must be fitted"):
            preprocessor.transform(sample_data)

    def test_transform_after_fit(self, preprocessor, sample_data):
        """Test that transform works after fitting."""
        preprocessor.fit(sample_data)
        result = preprocessor.transform(sample_data)

        assert isinstance(result, pd.DataFrame)
        assert len(result) == len(sample_data)

    def test_fit_transform_combined(self, preprocessor, sample_data):
        """Test fit_transform method."""
        result = preprocessor.fit_transform(sample_data)

        assert isinstance(result, pd.DataFrame)
        assert len(result) == len(sample_data)
        assert preprocessor._pipeline is not None

    def test_polynomial_features_generated(self, preprocessor, sample_data):
        """Test that polynomial features are generated."""
        result = preprocessor.fit_transform(sample_data)

        # With degree=2, we should have more features than input
        assert result.shape[1] > sample_data.shape[1]

    def test_feature_names_out(self, preprocessor, sample_data):
        """Test that feature names are generated correctly."""
        result = preprocessor.fit_transform(sample_data)

        # Should have column names
        assert len(result.columns) > 0
        # Column names should be strings
        assert all(isinstance(col, str) for col in result.columns)

    def test_save_before_fit_raises_error(self, preprocessor, tmp_path):
        """Test that save before fit raises ValueError."""
        path = tmp_path / "preprocessor.pkl"

        with pytest.raises(ValueError, match="Cannot save unfitted"):
            preprocessor.save(str(path))

    def test_save_after_fit(self, preprocessor, sample_data, tmp_path):
        """Test that preprocessor can be saved after fitting."""
        preprocessor.fit(sample_data)
        path = tmp_path / "preprocessor.pkl"

        preprocessor.save(str(path))

        assert path.exists()
        assert path.stat().st_size > 0

    def test_load_saved_preprocessor(self, preprocessor, sample_data, tmp_path):
        """Test that saved preprocessor can be loaded."""
        # Fit and save
        preprocessor.fit(sample_data)
        path = tmp_path / "preprocessor.pkl"
        preprocessor.save(str(path))

        # Load
        loaded = SklearnPreprocessor.load(str(path))

        assert loaded._pipeline is not None
        assert isinstance(loaded, SklearnPreprocessor)

    def test_save_load_predictions_match(self, preprocessor, sample_data, tmp_path):
        """Test that loaded preprocessor produces same output."""
        # Fit and transform
        original_result = preprocessor.fit_transform(sample_data)

        # Save and load
        path = tmp_path / "preprocessor.pkl"
        preprocessor.save(str(path))
        loaded = SklearnPreprocessor.load(str(path))

        # Transform with loaded
        loaded_result = loaded.transform(sample_data)

        # Results should match
        pd.testing.assert_frame_equal(original_result, loaded_result)

    def test_save_creates_parent_directory(self, preprocessor, sample_data, tmp_path):
        """Test that save creates parent directories if they don't exist."""
        preprocessor.fit(sample_data)
        path = tmp_path / "nested" / "dir" / "preprocessor.pkl"

        preprocessor.save(str(path))

        assert path.exists()

    def test_handles_missing_values(self, preprocessor):
        """Test that preprocessor handles missing values via imputation."""
        import numpy as np

        data = pd.DataFrame(
            {
                "LotArea": [8450, np.nan, 11250],
                "LotAge": [5, 31, np.nan],
                "OverallQual": [7, 6, 7],
                "OverallCond": [5, 8, 5],
                "YearsSinceRemod": [5, -1, 6],
            }
        )

        result = preprocessor.fit_transform(data)

        # Should not have any NaN values after transformation
        assert not result.isna().any().any()

    def test_custom_poly_degree(self):
        """Test preprocessor with custom polynomial degree."""
        preprocessor = SklearnPreprocessor(poly_degree=3)
        data = pd.DataFrame(
            {
                "LotArea": [8450, 9600],
                "LotAge": [5, 31],
                "OverallQual": [7, 6],
                "OverallCond": [5, 8],
                "YearsSinceRemod": [5, -1],
            }
        )

        result = preprocessor.fit_transform(data)

        # Degree 3 should produce more features than degree 2
        assert result.shape[1] > data.shape[1]

    def test_transform_new_data_same_shape(self, preprocessor, sample_data):
        """Test that transform on new data produces consistent shape."""
        preprocessor.fit(sample_data)

        new_data = pd.DataFrame(
            {
                "LotArea": [7500],
                "LotAge": [10],
                "OverallQual": [6],
                "OverallCond": [7],
                "YearsSinceRemod": [3],
            }
        )

        result = preprocessor.transform(new_data)

        # Should have same number of features as training
        train_result = preprocessor.transform(sample_data)
        assert result.shape[1] == train_result.shape[1]

    def test_configuration_extraction_from_loaded(
        self, preprocessor, sample_data, tmp_path
    ):
        """Test that configuration is extracted when loading."""
        preprocessor.fit(sample_data)
        path = tmp_path / "preprocessor.pkl"
        preprocessor.save(str(path))

        loaded = SklearnPreprocessor.load(str(path))

        # Should extract poly_degree
        assert hasattr(loaded, "poly_degree")
        assert loaded.poly_degree == 2
