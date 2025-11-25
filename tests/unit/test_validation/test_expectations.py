"""
Tests for Great Expectations suite definitions.
"""

from datetime import datetime

import pandas as pd
import pytest

from ames_house_price_prediction.validation.expectations import (
    create_api_monitoring_suite,
    create_engineered_features_suite,
    create_preprocessed_features_suite,
    create_raw_data_suite,
)


class TestRawDataSuite:
    """Tests for raw data validation suite."""

    def test_suite_creation_with_target(self):
        """Test creating suite with target variable."""
        suite = create_raw_data_suite(include_target=True)

        assert suite.expectation_suite_name == "raw_housing_data"
        assert len(suite.expectations) > 0

        # Check that some key expectations are present
        expectation_types = [exp.expectation_type for exp in suite.expectations]
        assert "expect_table_columns_to_match_set" in expectation_types
        assert "expect_column_values_to_be_of_type" in expectation_types
        assert "expect_column_values_to_be_between" in expectation_types

    def test_suite_creation_without_target(self):
        """Test creating suite without target variable (for test data)."""
        suite = create_raw_data_suite(include_target=False)

        assert suite.expectation_suite_name == "raw_housing_data"

        # Check that target-related expectations are not present
        for exp in suite.expectations:
            if exp.expectation_type == "expect_table_columns_to_match_set":
                columns = exp.kwargs.get("column_set", [])
                assert "SalePrice" not in columns

    def test_suite_has_range_validation(self):
        """Test that suite includes range validation for features."""
        suite = create_raw_data_suite()

        range_expectations = [
            exp
            for exp in suite.expectations
            if exp.expectation_type == "expect_column_values_to_be_between"
        ]

        assert len(range_expectations) > 0

        # Check specific ranges
        lot_area_exp = next(
            (
                exp
                for exp in range_expectations
                if exp.kwargs.get("column") == "LotArea"
            ),
            None,
        )
        assert lot_area_exp is not None
        assert lot_area_exp.kwargs["min_value"] == 1000
        assert lot_area_exp.kwargs["max_value"] == 250000

    def test_suite_has_cross_field_validation(self):
        """Test that suite includes cross-field validation."""
        suite = create_raw_data_suite()

        cross_field_expectations = [
            exp
            for exp in suite.expectations
            if exp.expectation_type
            == "expect_column_pair_values_A_to_be_greater_than_or_equal_to_B"
        ]

        assert len(cross_field_expectations) >= 3  # YearRemodAdd >= YearBuilt, etc.

    def test_suite_uses_current_year_for_validation(self):
        """Test that suite uses current year for upper bound validation."""
        suite = create_raw_data_suite()
        current_year = datetime.now().year

        year_built_exp = next(
            (
                exp
                for exp in suite.expectations
                if exp.expectation_type == "expect_column_values_to_be_between"
                and exp.kwargs.get("column") == "YearBuilt"
            ),
            None,
        )

        assert year_built_exp is not None
        assert year_built_exp.kwargs["max_value"] == current_year


class TestEngineeredFeaturesSuite:
    """Tests for engineered features validation suite."""

    def test_suite_creation(self):
        """Test creating engineered features suite."""
        suite = create_engineered_features_suite()

        assert suite.expectation_suite_name == "engineered_housing_features"
        assert len(suite.expectations) > 0

    def test_suite_validates_derived_features(self):
        """Test that suite validates LotAge and YearsSinceRemod."""
        suite = create_engineered_features_suite()

        # Check LotAge validation
        lot_age_expectations = [
            exp for exp in suite.expectations if exp.kwargs.get("column") == "LotAge"
        ]
        assert len(lot_age_expectations) > 0

        # Check YearsSinceRemod validation
        years_since_remod_expectations = [
            exp
            for exp in suite.expectations
            if exp.kwargs.get("column") == "YearsSinceRemod"
        ]
        assert len(years_since_remod_expectations) > 0

    def test_suite_has_reasonable_age_bounds(self):
        """Test that derived features have reasonable bounds."""
        suite = create_engineered_features_suite()

        lot_age_range = next(
            (
                exp
                for exp in suite.expectations
                if exp.expectation_type == "expect_column_values_to_be_between"
                and exp.kwargs.get("column") == "LotAge"
            ),
            None,
        )

        assert lot_age_range is not None
        assert lot_age_range.kwargs["min_value"] == 0
        assert lot_age_range.kwargs["max_value"] == 200  # Reasonable upper bound


class TestPreprocessedFeaturesSuite:
    """Tests for preprocessed features validation suite."""

    def test_suite_creation(self):
        """Test creating preprocessed features suite."""
        suite = create_preprocessed_features_suite()

        assert suite.expectation_suite_name == "preprocessed_housing_features"
        assert len(suite.expectations) > 0

    def test_suite_with_feature_count(self):
        """Test suite with expected feature count."""
        expected_count = 21  # Example: 5 features * 2 (polynomial) + 1
        suite = create_preprocessed_features_suite(
            expected_feature_count=expected_count
        )

        column_count_exp = next(
            (
                exp
                for exp in suite.expectations
                if exp.expectation_type == "expect_table_column_count_to_equal"
            ),
            None,
        )

        assert column_count_exp is not None
        assert column_count_exp.kwargs["value"] == expected_count

    def test_suite_validates_row_count(self):
        """Test that suite validates minimum and maximum row counts."""
        suite = create_preprocessed_features_suite()

        row_count_exp = next(
            (
                exp
                for exp in suite.expectations
                if exp.expectation_type == "expect_table_row_count_to_be_between"
            ),
            None,
        )

        assert row_count_exp is not None
        assert row_count_exp.kwargs["min_value"] == 10
        assert row_count_exp.kwargs["max_value"] == 10000


class TestAPIMonitoringSuite:
    """Tests for API monitoring suite."""

    def test_suite_creation(self):
        """Test creating API monitoring suite."""
        suite = create_api_monitoring_suite()

        assert suite.expectation_suite_name == "api_housing_data"
        assert len(suite.expectations) > 0

    def test_suite_has_permissive_ranges(self):
        """Test that API suite has more permissive ranges than training suite."""
        api_suite = create_api_monitoring_suite()
        raw_suite = create_raw_data_suite()

        # API suite should have fewer strict validations
        api_lot_area = next(
            (
                exp
                for exp in api_suite.expectations
                if exp.kwargs.get("column") == "LotArea"
            ),
            None,
        )
        raw_lot_area = next(
            (
                exp
                for exp in raw_suite.expectations
                if exp.expectation_type == "expect_column_values_to_be_between"
                and exp.kwargs.get("column") == "LotArea"
            ),
            None,
        )

        assert api_lot_area is not None
        assert raw_lot_area is not None
        # API should have wider range
        assert api_lot_area.kwargs["max_value"] > raw_lot_area.kwargs["max_value"]


class TestSuiteConfiguration:
    """Tests for overall suite configuration and consistency."""

    def test_all_suites_have_unique_names(self):
        """Test that all suites have unique names."""
        suites = [
            create_raw_data_suite(),
            create_engineered_features_suite(),
            create_preprocessed_features_suite(),
            create_api_monitoring_suite(),
        ]

        names = [suite.expectation_suite_name for suite in suites]
        assert len(names) == len(set(names)), "Suite names must be unique"

    def test_suites_are_json_serializable(self):
        """Test that all suites can be serialized to JSON."""
        suites = [
            create_raw_data_suite(),
            create_engineered_features_suite(),
            create_preprocessed_features_suite(),
            create_api_monitoring_suite(),
        ]

        for suite in suites:
            # This will raise if not serializable
            suite_dict = suite.to_json_dict()
            assert isinstance(suite_dict, dict)
            assert "expectation_suite_name" in suite_dict
            assert "expectations" in suite_dict
