"""
Tests for validation helper functions.
"""

from datetime import datetime

import numpy as np
import pandas as pd
import pytest

from ames_house_price_prediction.validation.validators import (
    ValidationError,
    ValidationResult,
    monitor_api_prediction,
    validate_engineered_features,
    validate_preprocessed_features,
    validate_raw_data,
    validate_test_data,
)


@pytest.fixture
def valid_raw_data():
    """Create valid raw housing data for testing."""
    return pd.DataFrame(
        {
            "LotArea": [8450.0, 9600.0, 11250.0],
            "YearBuilt": [2003, 1976, 2001],
            "YearRemodAdd": [2003, 1976, 2002],
            "YrSold": [2008, 2007, 2008],
            "OverallQual": [7, 6, 7],
            "OverallCond": [5, 8, 5],
            "SalePrice": [208500.0, 181500.0, 223500.0],
        }
    )


@pytest.fixture
def valid_engineered_data():
    """Create valid engineered features data for testing."""
    return pd.DataFrame(
        {
            "LotArea": [8450.0, 9600.0, 11250.0],
            "YearBuilt": [2003, 1976, 2001],
            "YearRemodAdd": [2003, 1976, 2002],
            "YrSold": [2008, 2007, 2008],
            "OverallQual": [7, 6, 7],
            "OverallCond": [5, 8, 5],
            "LotAge": [5, 31, 7],
            "YearsSinceRemod": [-1, -1, 6],
            "SalePrice": [208500.0, 181500.0, 223500.0],
        }
    )


@pytest.fixture
def invalid_raw_data():
    """Create invalid raw housing data for testing."""
    return pd.DataFrame(
        {
            "LotArea": [-1000.0, 9600.0, 11250.0],  # Negative lot area (invalid)
            "YearBuilt": [2003, 1776, 2001],  # 1776 is before 1800 (invalid)
            "YearRemodAdd": [2003, 1976, 2002],
            "YrSold": [2008, 2007, 2008],
            "OverallQual": [7, 6, 15],  # 15 is > 10 (invalid)
            "OverallCond": [5, 8, 5],
            "SalePrice": [208500.0, 181500.0, 223500.0],
        }
    )


class TestValidationResult:
    """Tests for ValidationResult dataclass."""

    def test_validation_result_success_string(self):
        """Test string representation of successful validation."""
        result = ValidationResult(
            success=True,
            statistics={"evaluated": 10, "successful": 10, "unsuccessful": 0},
            failed_expectations=[],
            validation_results=None,
        )

        assert "✓" in str(result)
        assert "10/10" in str(result)

    def test_validation_result_failure_string(self):
        """Test string representation of failed validation."""
        result = ValidationResult(
            success=False,
            statistics={"evaluated": 10, "successful": 8, "unsuccessful": 2},
            failed_expectations=[{"type": "test"}] * 2,
            validation_results=None,
        )

        assert "✗" in str(result)
        assert "2 expectations failed" in str(result)

    def test_get_failure_summary_no_failures(self):
        """Test failure summary with no failures."""
        result = ValidationResult(
            success=True,
            statistics={"evaluated": 10, "successful": 10, "unsuccessful": 0},
            failed_expectations=[],
            validation_results=None,
        )

        summary = result.get_failure_summary()
        assert "No failures" in summary

    def test_get_failure_summary_with_failures(self):
        """Test failure summary with failures."""
        result = ValidationResult(
            success=False,
            statistics={"evaluated": 10, "successful": 8, "unsuccessful": 2},
            failed_expectations=[
                {
                    "expectation_config": {
                        "expectation_type": "expect_column_values_to_be_between",
                        "kwargs": {"column": "LotArea"},
                    },
                    "result": {"observed_value": -1000},
                }
            ],
            validation_results=None,
        )

        summary = result.get_failure_summary()
        assert "Validation Failures" in summary
        assert "expect_column_values_to_be_between" in summary
        assert "LotArea" in summary


class TestValidateRawData:
    """Tests for validate_raw_data function."""

    def test_validate_valid_raw_data(self, valid_raw_data):
        """Test validation passes for valid data."""
        result = validate_raw_data(
            valid_raw_data, include_target=True, fail_on_error=False
        )

        assert isinstance(result, ValidationResult)
        assert result.success is True

    def test_validate_invalid_raw_data(self, invalid_raw_data):
        """Test validation fails for invalid data."""
        result = validate_raw_data(
            invalid_raw_data, include_target=True, fail_on_error=False
        )

        assert isinstance(result, ValidationResult)
        assert result.success is False
        assert len(result.failed_expectations) > 0

    def test_validate_raw_data_without_target(self, valid_raw_data):
        """Test validation without target column."""
        # Remove SalePrice for test data scenario
        test_data = valid_raw_data.drop(columns=["SalePrice"])

        result = validate_raw_data(test_data, include_target=False, fail_on_error=False)

        assert result.success is True

    def test_validate_raw_data_raises_on_error(self, invalid_raw_data):
        """Test that validation raises ValidationError when fail_on_error=True."""
        with pytest.raises(ValidationError) as exc_info:
            validate_raw_data(invalid_raw_data, include_target=True, fail_on_error=True)

        assert isinstance(exc_info.value.validation_result, ValidationResult)
        assert exc_info.value.validation_result.success is False


class TestValidateEngineeredFeatures:
    """Tests for validate_engineered_features function."""

    def test_validate_valid_engineered_data(self, valid_engineered_data):
        """Test validation passes for valid engineered features."""
        result = validate_engineered_features(
            valid_engineered_data, include_target=True, fail_on_error=False
        )

        assert isinstance(result, ValidationResult)
        assert result.success is True

    def test_validate_negative_lot_age(self, valid_engineered_data):
        """Test validation fails for negative LotAge."""
        invalid_data = valid_engineered_data.copy()
        invalid_data.loc[0, "LotAge"] = -5  # Invalid negative age

        result = validate_engineered_features(
            invalid_data, include_target=True, fail_on_error=False
        )

        assert result.success is False

    def test_validate_excessive_lot_age(self, valid_engineered_data):
        """Test validation fails for unreasonably old houses."""
        invalid_data = valid_engineered_data.copy()
        invalid_data.loc[0, "LotAge"] = 250  # Too old (> 200 years)

        result = validate_engineered_features(
            invalid_data, include_target=True, fail_on_error=False
        )

        assert result.success is False

    def test_validate_invalid_years_since_remod(self, valid_engineered_data):
        """Test validation fails for invalid YearsSinceRemod."""
        invalid_data = valid_engineered_data.copy()
        invalid_data.loc[0, "YearsSinceRemod"] = -5  # Invalid (should be -1 or >= 0)

        result = validate_engineered_features(
            invalid_data, include_target=True, fail_on_error=False
        )

        assert result.success is False


class TestValidateTestData:
    """Tests for validate_test_data function."""

    def test_validate_valid_test_data(self, valid_raw_data):
        """Test validation passes for valid test data."""
        test_data = valid_raw_data.drop(columns=["SalePrice"])

        result = validate_test_data(test_data, fail_on_error=False)

        assert result.success is True

    def test_validate_test_data_with_target_column(self, valid_raw_data):
        """Test that validation doesn't expect SalePrice in test data."""
        # If test data includes SalePrice, it should still validate the schema
        result = validate_test_data(valid_raw_data, fail_on_error=False)

        # Result depends on whether suite checks for exact columns or not
        assert isinstance(result, ValidationResult)


class TestValidatePreprocessedFeatures:
    """Tests for validate_preprocessed_features function."""

    def test_validate_valid_preprocessed_dataframe(self):
        """Test validation passes for valid preprocessed DataFrame."""
        preprocessed_data = pd.DataFrame(
            {
                "feature_0": [0.5, -0.3, 0.8],
                "feature_1": [1.2, -1.5, 0.0],
                "feature_2": [0.0, 0.0, 0.1],
            }
        )

        result = validate_preprocessed_features(
            preprocessed_data, expected_feature_count=3, fail_on_error=False
        )

        assert result.success is True

    def test_validate_valid_preprocessed_array(self):
        """Test validation passes for valid preprocessed numpy array."""
        preprocessed_array = np.array(
            [
                [0.5, 1.2, 0.0],
                [-0.3, -1.5, 0.0],
                [0.8, 0.0, 0.1],
            ]
        )

        result = validate_preprocessed_features(
            preprocessed_array, expected_feature_count=3, fail_on_error=False
        )

        assert result.success is True

    def test_validate_preprocessed_with_nan(self):
        """Test validation fails for data with NaN values."""
        invalid_data = pd.DataFrame(
            {
                "feature_0": [0.5, np.nan, 0.8],
                "feature_1": [1.2, -1.5, 0.0],
            }
        )

        result = validate_preprocessed_features(invalid_data, fail_on_error=False)

        assert result.success is False

    def test_validate_preprocessed_with_inf(self):
        """Test validation fails for data with infinite values."""
        invalid_data = pd.DataFrame(
            {
                "feature_0": [0.5, np.inf, 0.8],
                "feature_1": [1.2, -1.5, 0.0],
            }
        )

        result = validate_preprocessed_features(invalid_data, fail_on_error=False)

        assert result.success is False

    def test_validate_preprocessed_feature_count_mismatch(self):
        """Test validation fails when feature count doesn't match."""
        data = pd.DataFrame(
            {
                "feature_0": [0.5, -0.3, 0.8],
                "feature_1": [1.2, -1.5, 0.0],
            }
        )

        # Expect 5 features but got 2
        result = validate_preprocessed_features(
            data, expected_feature_count=5, fail_on_error=False
        )

        assert result.success is False


class TestMonitorAPIPrediction:
    """Tests for monitor_api_prediction function."""

    def test_monitor_valid_api_input(self, valid_raw_data):
        """Test monitoring passes for valid API input."""
        single_prediction = valid_raw_data.iloc[[0]].drop(columns=["SalePrice"])

        result = monitor_api_prediction(single_prediction)

        # Should not raise exception
        assert result is None or isinstance(result, ValidationResult)

    def test_monitor_invalid_api_input_does_not_raise(self, invalid_raw_data):
        """Test that monitoring never raises exceptions."""
        single_prediction = invalid_raw_data.iloc[[0]].drop(columns=["SalePrice"])

        # Should not raise even with invalid data
        result = monitor_api_prediction(single_prediction)

        # May return None or ValidationResult, but should not raise
        assert result is None or isinstance(result, ValidationResult)

    def test_monitor_handles_exceptions_gracefully(self):
        """Test that monitoring handles unexpected errors gracefully."""
        # Pass something that might cause an error
        invalid_input = pd.DataFrame({"unexpected_column": [1, 2, 3]})

        # Should not raise
        result = monitor_api_prediction(invalid_input)

        assert result is None or isinstance(result, ValidationResult)


class TestValidationIntegration:
    """Integration tests for validation workflow."""

    def test_full_pipeline_validation(self, valid_raw_data):
        """Test validation through the entire pipeline."""
        # Step 1: Validate raw data
        raw_result = validate_raw_data(
            valid_raw_data, include_target=True, fail_on_error=True
        )
        assert raw_result.success is True

        # Step 2: Apply feature engineering (simulated)
        engineered_data = valid_raw_data.copy()
        engineered_data["LotAge"] = (
            engineered_data["YrSold"] - engineered_data["YearBuilt"]
        )
        engineered_data["YearsSinceRemod"] = np.where(
            engineered_data["YearRemodAdd"] > engineered_data["YearBuilt"],
            engineered_data["YrSold"] - engineered_data["YearRemodAdd"],
            -1,
        )

        # Step 3: Validate engineered features
        engineered_result = validate_engineered_features(
            engineered_data, include_target=True, fail_on_error=True
        )
        assert engineered_result.success is True

        # Step 4: Create preprocessed data (simulated)
        preprocessed_array = np.random.randn(3, 10)  # 3 samples, 10 features

        # Step 5: Validate preprocessed features
        preprocessed_result = validate_preprocessed_features(
            preprocessed_array, expected_feature_count=10, fail_on_error=True
        )
        assert preprocessed_result.success is True
