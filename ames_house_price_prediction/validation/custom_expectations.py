"""
Custom Great Expectations for business-specific validation rules.

This module defines custom expectations that are specific to the house price
prediction domain and cannot be expressed with standard GE expectations.
"""

from typing import Optional

import pandas as pd
from great_expectations.core import ExpectationConfiguration
from great_expectations.execution_engine import PandasExecutionEngine
from great_expectations.expectations.expectation import ColumnMapExpectation
from great_expectations.expectations.metrics import (
    ColumnMapMetricProvider,
    column_condition_partial,
)


class ColumnValuesLotAgeMatchCalculation(ColumnMapMetricProvider):
    """
    Metric provider for validating LotAge calculation.

    LotAge should equal YrSold - YearBuilt
    """

    condition_metric_name = "column_values.lot_age_match_calculation"
    condition_domain_keys = (
        "batch_id",
        "table",
        "column",
        "row_condition",
        "condition_parser",
    )

    @column_condition_partial(engine=PandasExecutionEngine)
    def _pandas(cls, column, **kwargs):
        """Check if LotAge matches YrSold - YearBuilt."""
        df = kwargs.get("table")
        if df is None or "YrSold" not in df.columns or "YearBuilt" not in df.columns:
            return pd.Series([True] * len(column))

        expected_lot_age = df["YrSold"] - df["YearBuilt"]
        return column == expected_lot_age


class ExpectColumnValuesLotAgeToMatchCalculation(ColumnMapExpectation):
    """
    Expect LotAge column to equal YrSold - YearBuilt.

    This validates that the derived feature calculation is correct.

    Example:
        >>> suite.add_expectation(
        ...     ExpectationConfiguration(
        ...         expectation_type="expect_column_values_lot_age_to_match_calculation",
        ...         kwargs={"column": "LotAge"}
        ...     )
        ... )
    """

    map_metric = "column_values.lot_age_match_calculation"
    success_keys = ("column", "mostly")
    default_kwarg_values = {
        "row_condition": None,
        "condition_parser": None,
        "mostly": 1.0,
        "result_format": "BASIC",
        "include_config": True,
        "catch_exceptions": False,
    }

    library_metadata = {
        "maturity": "experimental",
        "package": "ames_house_price_prediction.validation",
        "tags": ["custom", "business_rule", "derived_feature"],
    }


class ColumnValuesYearsSinceRemodLogic(ColumnMapMetricProvider):
    """
    Metric provider for validating YearsSinceRemod logic.

    YearsSinceRemod should be:
    - -1 if YearRemodAdd == YearBuilt (never remodeled)
    - YrSold - YearRemodAdd if YearRemodAdd > YearBuilt (remodeled)
    """

    condition_metric_name = "column_values.years_since_remod_logic"
    condition_domain_keys = (
        "batch_id",
        "table",
        "column",
        "row_condition",
        "condition_parser",
    )

    @column_condition_partial(engine=PandasExecutionEngine)
    def _pandas(cls, column, **kwargs):
        """Check if YearsSinceRemod follows the business logic."""
        df = kwargs.get("table")
        if df is None:
            return pd.Series([True] * len(column))

        required_cols = ["YrSold", "YearBuilt", "YearRemodAdd"]
        if not all(col in df.columns for col in required_cols):
            return pd.Series([True] * len(column))

        # Calculate expected value
        never_remodeled = df["YearRemodAdd"] == df["YearBuilt"]
        expected_value = pd.Series(index=df.index, dtype="int64")
        expected_value[never_remodeled] = -1
        expected_value[~never_remodeled] = (
            df.loc[~never_remodeled, "YrSold"]
            - df.loc[~never_remodeled, "YearRemodAdd"]
        )

        return column == expected_value


class ExpectColumnValuesYearsSinceRemodToFollowLogic(ColumnMapExpectation):
    """
    Expect YearsSinceRemod to follow the remodel logic.

    Validates:
    - YearsSinceRemod == -1 when house was never remodeled
    - YearsSinceRemod == YrSold - YearRemodAdd when remodeled

    Example:
        >>> suite.add_expectation(
        ...     ExpectationConfiguration(
        ...         expectation_type="expect_column_values_years_since_remod_to_follow_logic",
        ...         kwargs={"column": "YearsSinceRemod"}
        ...     )
        ... )
    """

    map_metric = "column_values.years_since_remod_logic"
    success_keys = ("column", "mostly")
    default_kwarg_values = {
        "row_condition": None,
        "condition_parser": None,
        "mostly": 1.0,
        "result_format": "BASIC",
        "include_config": True,
        "catch_exceptions": False,
    }

    library_metadata = {
        "maturity": "experimental",
        "package": "ames_house_price_prediction.validation",
        "tags": ["custom", "business_rule", "derived_feature"],
    }


class ColumnValuesReasonableHouseAge(ColumnMapMetricProvider):
    """
    Metric provider for validating reasonable house age.

    Houses older than 200 years are extremely unlikely and probably data errors.
    """

    condition_metric_name = "column_values.reasonable_house_age"
    condition_domain_keys = (
        "batch_id",
        "table",
        "column",
        "row_condition",
        "condition_parser",
    )
    condition_value_keys = ("max_age",)

    @column_condition_partial(engine=PandasExecutionEngine)
    def _pandas(cls, column, max_age=200, **kwargs):
        """Check if LotAge is within reasonable bounds."""
        return (column >= 0) & (column <= max_age)


class ExpectColumnValuesHouseAgeToBeReasonable(ColumnMapExpectation):
    """
    Expect LotAge to be within reasonable bounds (0 to max_age years).

    This is a business rule that houses older than 200 years are unlikely
    to be in the dataset and probably indicate data quality issues.

    Example:
        >>> suite.add_expectation(
        ...     ExpectationConfiguration(
        ...         expectation_type="expect_column_values_house_age_to_be_reasonable",
        ...         kwargs={"column": "LotAge", "max_age": 200}
        ...     )
        ... )
    """

    map_metric = "column_values.reasonable_house_age"
    success_keys = ("column", "max_age", "mostly")
    default_kwarg_values = {
        "max_age": 200,
        "row_condition": None,
        "condition_parser": None,
        "mostly": 1.0,
        "result_format": "BASIC",
        "include_config": True,
        "catch_exceptions": False,
    }

    library_metadata = {
        "maturity": "experimental",
        "package": "ames_house_price_prediction.validation",
        "tags": ["custom", "business_rule", "data_quality"],
    }


def register_custom_expectations():
    """
    Register all custom expectations with Great Expectations.

    This should be called once at the start of the application to make
    custom expectations available for use in validation suites.
    """
    # Custom expectations are automatically registered when imported
    # This function is a placeholder for explicit registration if needed
    pass
