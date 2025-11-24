"""Feature generation script using the new modular architecture."""

from pathlib import Path

import pandas as pd
import typer
from loguru import logger

from ames_house_price_prediction.config import (
    PREPROCESSOR_PATH,
    PROCESSED_DATA_DIR,
    TARGET,
)
from ames_house_price_prediction.core.feature_transformer import (
    HouseFeaturesTransformer,
)
from ames_house_price_prediction.core.preprocessing import SklearnPreprocessor

app = typer.Typer()


@app.command()
def main(
    input_path: Path = PROCESSED_DATA_DIR / "dataset.parquet",
    preprocessor_path: Path = PREPROCESSOR_PATH,
    features_path: Path = PROCESSED_DATA_DIR / "features.parquet",
    labels_path: Path = PROCESSED_DATA_DIR / "labels.parquet",
):
    """Generate features from dataset and save the fitted preprocessor.

    Args:
        input_path: Path to input dataset
        preprocessor_path: Path to save the fitted preprocessor
        features_path: Path to save the transformed features
        labels_path: Path to save the target labels
    """
    logger.info("Generating features from dataset...")
    input_df = pd.read_parquet(input_path)

    # Apply feature engineering
    feature_transformer = HouseFeaturesTransformer()
    df = feature_transformer.transform(input_df)

    # Create and fit preprocessor
    preprocessor = SklearnPreprocessor()
    transformed_df = preprocessor.fit_transform(df)

    # Save the fitted preprocessor
    preprocessor.save(preprocessor_path)
    logger.info(f"Saved preprocessor to {preprocessor_path}")

    # Save features and labels
    transformed_df.to_parquet(features_path, index=False)
    df[[TARGET]].to_parquet(labels_path, index=False)

    logger.success("Features generation complete.")


if __name__ == "__main__":
    app()
