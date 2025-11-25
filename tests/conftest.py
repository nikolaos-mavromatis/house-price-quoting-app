"""Shared pytest fixtures for all tests."""

import sys
from pathlib import Path

import pandas as pd
import pytest

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


# ============================================================================
# Sample Data Fixtures
# ============================================================================


@pytest.fixture
def sample_raw_data():
    """Small sample of raw house data with all required features."""
    return pd.DataFrame(
        {
            "LotArea": [8450, 9600, 11250, 7500, 9000],
            "YearBuilt": [2003, 1976, 2001, 1998, 2005],
            "YearRemodAdd": [2003, 1976, 2002, 1998, 2010],
            "YrSold": [2008, 2007, 2008, 2009, 2010],
            "OverallQual": [7, 6, 7, 5, 8],
            "OverallCond": [5, 8, 5, 6, 7],
            "SalePrice": [208500, 181500, 223500, 140000, 250000],
        }
    )


@pytest.fixture
def sample_features():
    """Sample engineered features (after feature transformation)."""
    return pd.DataFrame(
        {
            "LotArea": [8450, 9600, 11250],
            "LotAge": [5, 31, 7],
            "OverallQual": [7, 6, 7],
            "OverallCond": [5, 8, 5],
            "YearsSinceRemod": [5, -1, 6],
        }
    )


@pytest.fixture
def sample_targets():
    """Sample target values (sale prices)."""
    return pd.Series([208500, 181500, 223500], name="SalePrice")


@pytest.fixture
def sample_input_single():
    """Single house input for prediction."""
    return {
        "LotArea": 8450,
        "YearBuilt": 2003,
        "YearRemodAdd": 2003,
        "YrSold": 2008,
        "OverallQual": 7,
        "OverallCond": 5,
    }


@pytest.fixture
def sample_input_dataframe():
    """DataFrame with single house for prediction."""
    return pd.DataFrame(
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


# ============================================================================
# Mock Component Fixtures
# ============================================================================


@pytest.fixture
def mock_feature_transformer():
    """Mock feature transformer that passes data through."""
    from ames_house_price_prediction.core.interfaces import FeatureTransformer

    class MockFeatureTransformer(FeatureTransformer):
        def transform(self, data: pd.DataFrame) -> pd.DataFrame:
            """Pass through transformation."""
            result = data.copy()
            # Add minimal features if not present
            if "LotAge" not in result.columns:
                result["LotAge"] = 5
            if "YearsSinceRemod" not in result.columns:
                result["YearsSinceRemod"] = 5
            return result

    return MockFeatureTransformer()


@pytest.fixture
def mock_preprocessor():
    """Mock preprocessor that returns input as numpy array."""
    from ames_house_price_prediction.core.interfaces import Preprocessor

    class MockPreprocessor(Preprocessor):
        def fit(self, X, y=None):
            self._is_fitted = True
            return self

        def transform(self, X):
            if not hasattr(self, "_is_fitted"):
                raise ValueError("Preprocessor must be fitted before transform")
            return X.values if hasattr(X, "values") else X

        def save(self, path):
            pass

        @staticmethod
        def load(path):
            preprocessor = MockPreprocessor()
            preprocessor._is_fitted = True
            return preprocessor

    return MockPreprocessor()


@pytest.fixture
def mock_model():
    """Mock model that returns constant predictions."""
    from ames_house_price_prediction.core.interfaces import Model

    class MockModel(Model):
        def __init__(self):
            self.mean_ = 200000.0

        def fit(self, X, y):
            self.mean_ = y.mean() if hasattr(y, "mean") else sum(y) / len(y)
            return self

        def predict(self, X):
            n_samples = len(X) if hasattr(X, "__len__") else 1
            return pd.Series([self.mean_] * n_samples)

        def save(self, path):
            pass

        @staticmethod
        def load(path):
            return MockModel()

    return MockModel()


@pytest.fixture
def mock_prediction_service(mock_feature_transformer, mock_preprocessor, mock_model):
    """Mock prediction service for API testing."""
    from ames_house_price_prediction.core.service import PredictionService

    # Fit the mock preprocessor
    mock_preprocessor.fit(pd.DataFrame({"a": [1, 2, 3]}))

    service = PredictionService(
        feature_transformer=mock_feature_transformer,
        preprocessor=mock_preprocessor,
        model=mock_model,
    )

    return service


# ============================================================================
# Temporary Directory Fixtures
# ============================================================================


@pytest.fixture
def temp_model_dir(tmp_path):
    """Temporary directory for model artifacts."""
    model_dir = tmp_path / "models"
    model_dir.mkdir()
    return model_dir


@pytest.fixture
def temp_data_dir(tmp_path):
    """Temporary directory for data files."""
    data_dir = tmp_path / "data"
    (data_dir / "raw").mkdir(parents=True)
    (data_dir / "processed").mkdir(parents=True)
    return data_dir


# ============================================================================
# API Test Client Fixture
# ============================================================================


@pytest.fixture
def api_client(mock_prediction_service):
    """FastAPI test client with mocked service."""
    from unittest.mock import patch

    from fastapi.testclient import TestClient

    # Mock the service loading to avoid file dependencies
    with patch(
        "ames_house_price_prediction.core.service.PredictionService.from_files"
    ) as mock_from_files:
        mock_from_files.return_value = mock_prediction_service

        # Import and create client within the mock context
        from api.main import app

        # Use context manager to handle lifespan
        with TestClient(app) as client:
            yield client


# ============================================================================
# Trained Component Fixtures (for integration tests)
# ============================================================================


@pytest.fixture
def fitted_preprocessor(sample_features, temp_model_dir):
    """Actual fitted preprocessor for integration tests."""
    from ames_house_price_prediction.core.preprocessing import SklearnPreprocessor

    preprocessor = SklearnPreprocessor()
    preprocessor.fit(sample_features)

    # Save to temp directory
    path = temp_model_dir / "preprocessor.pkl"
    preprocessor.save(str(path))

    return path


@pytest.fixture
def fitted_model(sample_features, sample_targets, temp_model_dir):
    """Actual fitted model for integration tests."""
    from ames_house_price_prediction.core.model import RidgeRegressionModel
    from ames_house_price_prediction.core.preprocessing import SklearnPreprocessor

    # Fit preprocessor and transform data
    preprocessor = SklearnPreprocessor()
    X_processed = preprocessor.fit_transform(sample_features)

    # Fit model
    model = RidgeRegressionModel()
    model.fit(X_processed, sample_targets)

    # Save to temp directory
    path = temp_model_dir / "model.pkl"
    model.save(str(path))

    return path
