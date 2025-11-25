"""Unit tests for HouseFeaturesTransformer."""

import numpy as np
import pandas as pd
import pytest

from ames_house_price_prediction.core.feature_transformer import (
    HouseFeaturesTransformer,
)


@pytest.mark.unit
class TestHouseFeaturesTransformer:
    """Test suite for HouseFeaturesTransformer."""

    @pytest.fixture
    def transformer(self):
        """Create a transformer instance."""
        return HouseFeaturesTransformer()

    @pytest.fixture
    def basic_input_data(self):
        """Basic input data for transformation."""
        return pd.DataFrame(
            {
                "YrSold": [2008, 2007, 2008],
                "YearBuilt": [2003, 1976, 2001],
                "YearRemodAdd": [2003, 1976, 2002],
            }
        )

    def test_lot_age_calculation(self, transformer, basic_input_data):
        """Test that LotAge is correctly calculated as YrSold - YearBuilt."""
        result = transformer.transform(basic_input_data)

        assert "LotAge" in result.columns
        expected = pd.Series([5, 31, 7], name="LotAge")
        pd.testing.assert_series_equal(result["LotAge"], expected)

    def test_years_since_remod_when_remodeled(self, transformer):
        """Test YearsSinceRemod when house was actually remodeled."""
        data = pd.DataFrame(
            {
                "YrSold": [2008],
                "YearBuilt": [2000],
                "YearRemodAdd": [2005],  # Remodeled 5 years after built
            }
        )

        result = transformer.transform(data)

        assert result["YearsSinceRemod"].iloc[0] == 3  # 2008 - 2005

    def test_years_since_remod_when_not_remodeled(self, transformer):
        """Test YearsSinceRemod when house was never remodeled (same year as built)."""
        data = pd.DataFrame(
            {
                "YrSold": [2008],
                "YearBuilt": [2000],
                "YearRemodAdd": [2000],  # Same as YearBuilt = not remodeled
            }
        )

        result = transformer.transform(data)

        assert result["YearsSinceRemod"].iloc[0] == -1

    def test_years_since_remod_recent_remodel(self, transformer):
        """Test YearsSinceRemod when house was recently remodeled."""
        data = pd.DataFrame(
            {
                "YrSold": [2010],
                "YearBuilt": [1990],
                "YearRemodAdd": [2008],  # Remodeled 2 years before sale
            }
        )

        result = transformer.transform(data)

        assert result["YearsSinceRemod"].iloc[0] == 2  # 2010 - 2008

    def test_data_immutability(self, transformer, basic_input_data):
        """Test that original data is not modified during transformation."""
        original = basic_input_data.copy()

        result = transformer.transform(basic_input_data)

        # Original should be unchanged
        pd.testing.assert_frame_equal(basic_input_data, original)
        # Result should have new columns
        assert "LotAge" not in basic_input_data.columns
        assert "LotAge" in result.columns

    def test_all_input_columns_preserved(self, transformer, basic_input_data):
        """Test that all original columns are preserved in output."""
        result = transformer.transform(basic_input_data)

        for col in basic_input_data.columns:
            assert col in result.columns

    def test_missing_year_sold_raises_error(self, transformer):
        """Test that missing YrSold column raises KeyError."""
        data = pd.DataFrame({"YearBuilt": [2003], "YearRemodAdd": [2003]})

        with pytest.raises(KeyError, match="YrSold"):
            transformer.transform(data)

    def test_missing_year_built_raises_error(self, transformer):
        """Test that missing YearBuilt column raises KeyError."""
        data = pd.DataFrame({"YrSold": [2008], "YearRemodAdd": [2003]})

        with pytest.raises(KeyError, match="YearBuilt"):
            transformer.transform(data)

    def test_missing_year_remod_add_raises_error(self, transformer):
        """Test that missing YearRemodAdd column raises KeyError."""
        data = pd.DataFrame({"YrSold": [2008], "YearBuilt": [2003]})

        with pytest.raises(KeyError, match="YearRemodAdd"):
            transformer.transform(data)

    def test_multiple_rows_transformation(self, transformer):
        """Test transformation with multiple rows."""
        data = pd.DataFrame(
            {
                "YrSold": [2008, 2009, 2010, 2007, 2006],
                "YearBuilt": [2000, 1990, 2005, 1985, 2000],
                "YearRemodAdd": [2000, 1995, 2008, 1985, 2003],
            }
        )

        result = transformer.transform(data)

        assert len(result) == 5
        assert "LotAge" in result.columns
        assert "YearsSinceRemod" in result.columns

        # Verify calculations for each row
        assert result["LotAge"].iloc[0] == 8  # 2008 - 2000
        assert result["LotAge"].iloc[1] == 19  # 2009 - 1990
        assert result["YearsSinceRemod"].iloc[0] == -1  # Not remodeled
        assert result["YearsSinceRemod"].iloc[1] == 14  # 2009 - 1995

    def test_edge_case_same_year_built_and_sold(self, transformer):
        """Test edge case where house is built and sold in same year."""
        data = pd.DataFrame(
            {"YrSold": [2008], "YearBuilt": [2008], "YearRemodAdd": [2008]}
        )

        result = transformer.transform(data)

        assert result["LotAge"].iloc[0] == 0
        assert result["YearsSinceRemod"].iloc[0] == -1  # Not remodeled

    def test_empty_dataframe(self, transformer):
        """Test transformation with empty DataFrame."""
        data = pd.DataFrame({"YrSold": [], "YearBuilt": [], "YearRemodAdd": []})

        result = transformer.transform(data)

        assert len(result) == 0
        assert "LotAge" in result.columns
        assert "YearsSinceRemod" in result.columns

    def test_output_data_types(self, transformer, basic_input_data):
        """Test that output columns have correct data types."""
        result = transformer.transform(basic_input_data)

        # LotAge should be numeric (int or int64)
        assert pd.api.types.is_integer_dtype(result["LotAge"])
        # YearsSinceRemod should be numeric
        assert pd.api.types.is_integer_dtype(result["YearsSinceRemod"])

    def test_with_additional_columns(self, transformer):
        """Test that transformer works even with additional columns present."""
        data = pd.DataFrame(
            {
                "YrSold": [2008],
                "YearBuilt": [2003],
                "YearRemodAdd": [2003],
                "LotArea": [8450],
                "OverallQual": [7],
                "OverallCond": [5],
            }
        )

        result = transformer.transform(data)

        # Should have all original columns plus new ones
        assert "LotArea" in result.columns
        assert "OverallQual" in result.columns
        assert "LotAge" in result.columns
        assert "YearsSinceRemod" in result.columns
