"""
Validation helper functions for running Great Expectations validations.

This module provides high-level functions for validating data at different
stages of the ML pipeline with appropriate error handling and logging.
"""

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import great_expectations as gx
import pandas as pd
from great_expectations.core import ExpectationSuite
from great_expectations.data_context import AbstractDataContext
from great_expectations.validator.validator import Validator

from ames_house_price_prediction.validation.expectations import (
    create_engineered_features_suite,
    create_preprocessed_features_suite,
    create_raw_data_suite,
)

logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """
    Results from a Great Expectations validation.

    Attributes:
        success: Whether all expectations passed
        statistics: Summary statistics (evaluated, successful, unsuccessful, success_percent)
        failed_expectations: List of failed expectation details
        validation_results: Full GE validation results object
    """

    success: bool
    statistics: Dict[str, Any]
    failed_expectations: List[Dict[str, Any]]
    validation_results: Any  # ExpectationSuiteValidationResult

    def __str__(self) -> str:
        """Human-readable summary of validation results."""
        if self.success:
            return f"✓ Validation passed ({self.statistics['successful']}/{self.statistics['evaluated']} expectations)"
        else:
            failed_count = self.statistics["unsuccessful"]
            return f"✗ Validation failed ({failed_count} expectations failed)"

    def get_failure_summary(self) -> str:
        """Get detailed summary of validation failures."""
        if self.success:
            return "No failures"

        summary_lines = [
            f"Validation Failures ({len(self.failed_expectations)} expectations):"
        ]
        for i, failure in enumerate(self.failed_expectations, 1):
            expectation_type = failure.get("expectation_config", {}).get(
                "expectation_type", "unknown"
            )
            column = (
                failure.get("expectation_config", {})
                .get("kwargs", {})
                .get("column", "N/A")
            )
            summary_lines.append(f"  {i}. {expectation_type} on column '{column}'")
            if "result" in failure:
                summary_lines.append(f"     Details: {failure['result']}")

        return "\n".join(summary_lines)


class ValidationError(Exception):
    """Custom exception for validation failures."""

    def __init__(self, message: str, validation_result: ValidationResult):
        super().__init__(message)
        self.validation_result = validation_result


def _get_or_create_context() -> AbstractDataContext:
    """
    Get or create a Great Expectations data context.

    Returns:
        DataContext instance (ephemeral in-memory context)
    """
    # Use ephemeral context (no file system setup required)
    # This is simpler and doesn't require `great_expectations init`
    try:
        context = gx.get_context()
    except Exception:
        # If no context exists, create an ephemeral one
        context = gx.get_context(mode="ephemeral")

    return context


def _validate_dataframe(
    df: pd.DataFrame,
    suite: ExpectationSuite,
    batch_name: str = "data_batch",
) -> ValidationResult:
    """
    Validate a DataFrame against an expectation suite.

    Args:
        df: DataFrame to validate
        suite: ExpectationSuite to validate against
        batch_name: Name for the data batch

    Returns:
        ValidationResult with success status and details
    """
    context = _get_or_create_context()

    # Create a validator for the DataFrame
    validator = context.sources.pandas_default.read_dataframe(df)
    validator.expectation_suite = suite

    # Run validation
    results = validator.validate()

    # Extract failed expectations
    failed = [result.to_json_dict() for result in results.results if not result.success]

    # Build ValidationResult
    validation_result = ValidationResult(
        success=results.success,
        statistics=results.statistics,
        failed_expectations=failed,
        validation_results=results,
    )

    return validation_result


def validate_raw_data(
    df: pd.DataFrame,
    include_target: bool = True,
    fail_on_error: bool = True,
) -> ValidationResult:
    """
    Validate raw housing data loaded from CSV.

    This should be the first validation step in the pipeline, immediately
    after loading data and before any transformations.

    Args:
        df: Raw DataFrame to validate
        include_target: Whether SalePrice column is expected (True for training, False for prediction)
        fail_on_error: Whether to raise ValidationError on failure

    Returns:
        ValidationResult with validation details

    Raises:
        ValidationError: If validation fails and fail_on_error=True
    """
    logger.info(f"Validating raw data: {len(df)} rows, {len(df.columns)} columns")

    suite = create_raw_data_suite(include_target=include_target)
    result = _validate_dataframe(df, suite, batch_name="raw_data")

    if result.success:
        logger.info(f"✓ Raw data validation passed")
    else:
        logger.error(f"✗ Raw data validation failed")
        logger.error(result.get_failure_summary())

        if fail_on_error:
            raise ValidationError(
                f"Raw data validation failed: {result}",
                validation_result=result,
            )

    return result


def validate_engineered_features(
    df: pd.DataFrame,
    include_target: bool = True,
    fail_on_error: bool = True,
) -> ValidationResult:
    """
    Validate engineered features after feature transformation.

    Validates that derived features (LotAge, YearsSinceRemod) are within
    expected ranges and follow business logic.

    Args:
        df: DataFrame with engineered features
        include_target: Whether target variable is present
        fail_on_error: Whether to raise ValidationError on failure

    Returns:
        ValidationResult with validation details

    Raises:
        ValidationError: If validation fails and fail_on_error=True
    """
    logger.info(
        f"Validating engineered features: {len(df)} rows, {len(df.columns)} columns"
    )

    suite = create_engineered_features_suite(include_target=include_target)
    result = _validate_dataframe(df, suite, batch_name="engineered_features")

    # Additional custom validation: YearsSinceRemod <= LotAge (when not -1)
    if "LotAge" in df.columns and "YearsSinceRemod" in df.columns:
        invalid_rows = df[
            (df["YearsSinceRemod"] != -1) & (df["YearsSinceRemod"] > df["LotAge"])
        ]

        if len(invalid_rows) > 0:
            logger.warning(
                f"Found {len(invalid_rows)} rows where YearsSinceRemod > LotAge "
                f"(should be impossible)"
            )
            # Don't fail, but log the warning

    if result.success:
        logger.info(f"✓ Engineered features validation passed")
    else:
        logger.error(f"✗ Engineered features validation failed")
        logger.error(result.get_failure_summary())

        if fail_on_error:
            raise ValidationError(
                f"Engineered features validation failed: {result}",
                validation_result=result,
            )

    return result


def validate_test_data(
    df: pd.DataFrame,
    fail_on_error: bool = True,
) -> ValidationResult:
    """
    Validate test data for batch predictions.

    Ensures test data has the same schema as training data (without target).

    Args:
        df: Test DataFrame to validate
        fail_on_error: Whether to raise ValidationError on failure

    Returns:
        ValidationResult with validation details

    Raises:
        ValidationError: If validation fails and fail_on_error=True
    """
    logger.info(f"Validating test data: {len(df)} rows, {len(df.columns)} columns")

    # Test data should not have target column
    suite = create_raw_data_suite(include_target=False)
    result = _validate_dataframe(df, suite, batch_name="test_data")

    if result.success:
        logger.info(f"✓ Test data validation passed")
    else:
        logger.error(f"✗ Test data validation failed")
        logger.error(result.get_failure_summary())

        if fail_on_error:
            raise ValidationError(
                f"Test data validation failed: {result}",
                validation_result=result,
            )

    return result


def validate_preprocessed_features(
    data: Any,
    expected_feature_count: Optional[int] = None,
    fail_on_error: bool = False,
) -> ValidationResult:
    """
    Validate preprocessed features ready for model input.

    This validation is optional and typically used for debugging.

    Args:
        data: Preprocessed data (numpy array or DataFrame)
        expected_feature_count: Expected number of features after preprocessing
        fail_on_error: Whether to raise ValidationError on failure

    Returns:
        ValidationResult with validation details

    Raises:
        ValidationError: If validation fails and fail_on_error=True
    """
    # Convert to DataFrame if numpy array
    if isinstance(data, pd.DataFrame):
        df = data
    else:
        # Assume numpy array
        import numpy as np

        if not isinstance(data, np.ndarray):
            data = np.array(data)

        df = pd.DataFrame(
            data,
            columns=[f"feature_{i}" for i in range(data.shape[1])],
        )

    logger.info(
        f"Validating preprocessed features: {len(df)} rows, {len(df.columns)} columns"
    )

    suite = create_preprocessed_features_suite(
        expected_feature_count=expected_feature_count
    )
    result = _validate_dataframe(df, suite, batch_name="preprocessed_features")

    # Additional checks
    if df.isnull().any().any():
        logger.error("Preprocessed features contain NaN values")
        result.success = False

    import numpy as np

    if np.isinf(df.select_dtypes(include=[np.number]).values).any():
        logger.error("Preprocessed features contain infinite values")
        result.success = False

    if result.success:
        logger.info(f"✓ Preprocessed features validation passed")
    else:
        logger.error(f"✗ Preprocessed features validation failed")

        if fail_on_error:
            raise ValidationError(
                f"Preprocessed features validation failed: {result}",
                validation_result=result,
            )

    return result


def monitor_api_prediction(
    df: pd.DataFrame,
) -> Optional[ValidationResult]:
    """
    Non-blocking validation for API prediction monitoring.

    This function logs validation results but never raises exceptions,
    ensuring API requests are never blocked by validation.

    Args:
        df: Single-row DataFrame from API request

    Returns:
        ValidationResult if validation succeeds, None if validation fails
    """
    try:
        from ames_house_price_prediction.validation.expectations import (
            create_api_monitoring_suite,
        )

        suite = create_api_monitoring_suite()
        result = _validate_dataframe(df, suite, batch_name="api_prediction")

        if not result.success:
            logger.warning(f"API prediction validation warning: {result}")
            logger.warning(result.get_failure_summary())

        return result

    except Exception as e:
        logger.warning(f"API validation monitoring failed (non-critical): {e}")
        return None
