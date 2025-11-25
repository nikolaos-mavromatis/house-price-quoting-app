"""
Great Expectations suite definitions for house price data validation.

This module defines expectation suites for validating data at different stages
of the ML pipeline:
1. Raw data validation (after CSV load)
2. Engineered features validation (after feature transformation)
3. Preprocessed features validation (model-ready data)
"""

from datetime import datetime
from typing import Optional

import great_expectations as gx
from great_expectations.core import ExpectationConfiguration, ExpectationSuite

from ames_house_price_prediction.config.features import (
    FEATURES,
    NUM_FEATURES,
    TARGET,
)


def create_raw_data_suite(
    suite_name: str = "raw_housing_data",
    include_target: bool = True,
) -> ExpectationSuite:
    """
    Create expectation suite for raw housing data validation.

    Validates:
    - Schema (column presence and order)
    - Data types
    - Value ranges
    - Non-null constraints
    - Cross-field dependencies

    Args:
        suite_name: Name for the expectation suite
        include_target: Whether to include SalePrice validation (True for training, False for prediction)

    Returns:
        ExpectationSuite configured for raw data validation
    """
    suite = ExpectationSuite(expectation_suite_name=suite_name)
    current_year = datetime.now().year

    # Expected columns for training data
    if include_target:
        expected_columns = FEATURES + [TARGET]
    else:
        expected_columns = FEATURES.copy()

    # 1. Schema Validation - Column presence
    suite.add_expectation(
        ExpectationConfiguration(
            expectation_type="expect_table_columns_to_match_set",
            kwargs={
                "column_set": expected_columns,
                "exact_match": False,  # Allow extra columns
            },
        )
    )

    # 2. Data Type Validation
    suite.add_expectation(
        ExpectationConfiguration(
            expectation_type="expect_column_values_to_be_of_type",
            kwargs={
                "column": "LotArea",
                "type_": "float64",
            },
        )
    )

    for year_col in ["YearBuilt", "YearRemodAdd", "YrSold"]:
        suite.add_expectation(
            ExpectationConfiguration(
                expectation_type="expect_column_values_to_be_of_type",
                kwargs={
                    "column": year_col,
                    "type_": "int64",
                },
            )
        )

    for quality_col in ["OverallQual", "OverallCond"]:
        suite.add_expectation(
            ExpectationConfiguration(
                expectation_type="expect_column_values_to_be_of_type",
                kwargs={
                    "column": quality_col,
                    "type_": "int64",
                },
            )
        )

    if include_target:
        suite.add_expectation(
            ExpectationConfiguration(
                expectation_type="expect_column_values_to_be_of_type",
                kwargs={
                    "column": TARGET,
                    "type_": "float64",
                },
            )
        )

    # 3. Range Validation
    suite.add_expectation(
        ExpectationConfiguration(
            expectation_type="expect_column_values_to_be_between",
            kwargs={
                "column": "LotArea",
                "min_value": 1000,
                "max_value": 250000,
                "mostly": 0.95,  # Allow 5% outliers
            },
        )
    )

    suite.add_expectation(
        ExpectationConfiguration(
            expectation_type="expect_column_values_to_be_between",
            kwargs={
                "column": "YearBuilt",
                "min_value": 1800,
                "max_value": current_year,
            },
        )
    )

    suite.add_expectation(
        ExpectationConfiguration(
            expectation_type="expect_column_values_to_be_between",
            kwargs={
                "column": "YearRemodAdd",
                "min_value": 1800,
                "max_value": current_year,
            },
        )
    )

    suite.add_expectation(
        ExpectationConfiguration(
            expectation_type="expect_column_values_to_be_between",
            kwargs={
                "column": "YrSold",
                "min_value": 2000,
                "max_value": current_year,
            },
        )
    )

    suite.add_expectation(
        ExpectationConfiguration(
            expectation_type="expect_column_values_to_be_between",
            kwargs={
                "column": "OverallQual",
                "min_value": 1,
                "max_value": 10,
            },
        )
    )

    suite.add_expectation(
        ExpectationConfiguration(
            expectation_type="expect_column_values_to_be_between",
            kwargs={
                "column": "OverallCond",
                "min_value": 1,
                "max_value": 10,
            },
        )
    )

    if include_target:
        suite.add_expectation(
            ExpectationConfiguration(
                expectation_type="expect_column_values_to_be_between",
                kwargs={
                    "column": TARGET,
                    "min_value": 10000,
                    "max_value": 1000000,
                    "mostly": 0.95,  # Allow outliers
                },
            )
        )

    # 4. Non-null Validation
    for col in ["LotArea", "YearBuilt", "YearRemodAdd", "OverallQual", "OverallCond"]:
        suite.add_expectation(
            ExpectationConfiguration(
                expectation_type="expect_column_values_to_not_be_null",
                kwargs={
                    "column": col,
                },
            )
        )

    # 5. Cross-field Validation
    # YearRemodAdd must be >= YearBuilt
    suite.add_expectation(
        ExpectationConfiguration(
            expectation_type="expect_column_pair_values_A_to_be_greater_than_or_equal_to_B",
            kwargs={
                "column_A": "YearRemodAdd",
                "column_B": "YearBuilt",
            },
        )
    )

    # YrSold must be >= YearBuilt
    suite.add_expectation(
        ExpectationConfiguration(
            expectation_type="expect_column_pair_values_A_to_be_greater_than_or_equal_to_B",
            kwargs={
                "column_A": "YrSold",
                "column_B": "YearBuilt",
            },
        )
    )

    # YrSold must be >= YearRemodAdd
    suite.add_expectation(
        ExpectationConfiguration(
            expectation_type="expect_column_pair_values_A_to_be_greater_than_or_equal_to_B",
            kwargs={
                "column_A": "YrSold",
                "column_B": "YearRemodAdd",
            },
        )
    )

    return suite


def create_engineered_features_suite(
    suite_name: str = "engineered_housing_features",
    include_target: bool = True,
) -> ExpectationSuite:
    """
    Create expectation suite for engineered features validation.

    Validates:
    - Derived feature ranges (LotAge, YearsSinceRemod)
    - Feature engineering logic correctness
    - Cross-field consistency

    Args:
        suite_name: Name for the expectation suite
        include_target: Whether to include target variable

    Returns:
        ExpectationSuite configured for engineered features validation
    """
    suite = ExpectationSuite(expectation_suite_name=suite_name)

    # Expected columns after feature engineering
    expected_columns = FEATURES + ["LotAge", "YearsSinceRemod"]
    if include_target:
        expected_columns.append(TARGET)

    # 1. Schema Validation
    suite.add_expectation(
        ExpectationConfiguration(
            expectation_type="expect_table_columns_to_match_set",
            kwargs={
                "column_set": expected_columns,
                "exact_match": False,
            },
        )
    )

    # 2. LotAge Validation
    suite.add_expectation(
        ExpectationConfiguration(
            expectation_type="expect_column_values_to_be_between",
            kwargs={
                "column": "LotAge",
                "min_value": 0,
                "max_value": 200,  # Houses older than 200 years are unlikely
            },
        )
    )

    suite.add_expectation(
        ExpectationConfiguration(
            expectation_type="expect_column_values_to_not_be_null",
            kwargs={
                "column": "LotAge",
            },
        )
    )

    # 3. YearsSinceRemod Validation
    suite.add_expectation(
        ExpectationConfiguration(
            expectation_type="expect_column_values_to_be_between",
            kwargs={
                "column": "YearsSinceRemod",
                "min_value": -1,  # -1 indicates never remodeled
                "max_value": 200,
            },
        )
    )

    suite.add_expectation(
        ExpectationConfiguration(
            expectation_type="expect_column_values_to_not_be_null",
            kwargs={
                "column": "YearsSinceRemod",
            },
        )
    )

    # 4. Logical Consistency
    # When YearsSinceRemod != -1, it should be <= LotAge
    # This is a custom validation that requires manual checking in the validator

    return suite


def create_preprocessed_features_suite(
    suite_name: str = "preprocessed_housing_features",
    expected_feature_count: Optional[int] = None,
) -> ExpectationSuite:
    """
    Create expectation suite for preprocessed (model-ready) features validation.

    Validates:
    - No null values
    - No infinite values
    - Correct shape
    - Reasonable scaled values

    Args:
        suite_name: Name for the expectation suite
        expected_feature_count: Expected number of features after polynomial expansion

    Returns:
        ExpectationSuite configured for preprocessed features validation
    """
    suite = ExpectationSuite(expectation_suite_name=suite_name)

    # 1. Table-level Validation
    suite.add_expectation(
        ExpectationConfiguration(
            expectation_type="expect_table_row_count_to_be_between",
            kwargs={
                "min_value": 10,  # At least 10 samples
                "max_value": 10000,  # Reasonable upper bound
            },
        )
    )

    if expected_feature_count:
        suite.add_expectation(
            ExpectationConfiguration(
                expectation_type="expect_table_column_count_to_equal",
                kwargs={
                    "value": expected_feature_count,
                },
            )
        )

    # 2. Value Quality Checks (applied to all numeric columns)
    # Note: These will be applied dynamically to whatever columns exist
    # in the preprocessed data

    return suite


def create_api_monitoring_suite(
    suite_name: str = "api_housing_data",
) -> ExpectationSuite:
    """
    Create lightweight expectation suite for API request monitoring.

    This suite is designed for non-blocking validation that logs metrics
    without failing requests.

    Args:
        suite_name: Name for the expectation suite

    Returns:
        ExpectationSuite configured for API monitoring
    """
    suite = ExpectationSuite(expectation_suite_name=suite_name)
    current_year = datetime.now().year

    # Basic range checks only (lightweight)
    suite.add_expectation(
        ExpectationConfiguration(
            expectation_type="expect_column_values_to_be_between",
            kwargs={
                "column": "LotArea",
                "min_value": 0,
                "max_value": 1000000,  # Very permissive
            },
        )
    )

    suite.add_expectation(
        ExpectationConfiguration(
            expectation_type="expect_column_values_to_be_between",
            kwargs={
                "column": "YearBuilt",
                "min_value": 1800,
                "max_value": current_year + 1,  # Allow future dates
            },
        )
    )

    suite.add_expectation(
        ExpectationConfiguration(
            expectation_type="expect_column_values_to_be_between",
            kwargs={
                "column": "OverallQual",
                "min_value": 1,
                "max_value": 10,
            },
        )
    )

    suite.add_expectation(
        ExpectationConfiguration(
            expectation_type="expect_column_values_to_be_between",
            kwargs={
                "column": "OverallCond",
                "min_value": 1,
                "max_value": 10,
            },
        )
    )

    return suite
