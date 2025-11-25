"""Feature engineering transformations."""

import numpy as np
import pandas as pd

from ames_house_price_prediction.core.interfaces import FeatureTransformer


class HouseFeaturesTransformer(FeatureTransformer):
    """Transformer for creating house price prediction features."""

    def transform(self, data: pd.DataFrame) -> pd.DataFrame:
        """Transform input data by creating derived features.

        Args:
            data: Input DataFrame with raw house features

        Returns:
            DataFrame with additional engineered features
        """
        df = data.copy()

        # Calculate lot age (years between built and sold)
        df["LotAge"] = df["YrSold"] - df["YearBuilt"]

        # Calculate years since remodel (-1 if never remodeled)
        df["YearsSinceRemod"] = np.where(
            df["YearRemodAdd"] > df["YearBuilt"], df["YrSold"] - df["YearRemodAdd"], -1
        )

        return df
