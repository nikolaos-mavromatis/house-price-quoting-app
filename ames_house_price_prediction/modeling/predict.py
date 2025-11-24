"""Prediction script using the new modular architecture."""

from pathlib import Path

import typer
from loguru import logger
import pandas as pd

from ames_house_price_prediction.config import (
    MODELS_DIR,
    MODEL_PATH,
    PREPROCESSOR_PATH,
    PROCESSED_DATA_DIR,
    RAW_DATA_DIR,
    TARGET,
)
from ames_house_price_prediction.core.service import PredictionService

app = typer.Typer()


@app.command()
def main(
    features_path: Path = RAW_DATA_DIR / "test.csv",
    preprocessor_path: Path = PREPROCESSOR_PATH,
    model_path: Path = MODEL_PATH,
    predictions_path: Path = PROCESSED_DATA_DIR / "submissions.csv",
):
    """Perform inference using the trained model.

    Args:
        features_path: Path to the raw test data
        preprocessor_path: Path to the fitted preprocessor
        model_path: Path to the trained model
        predictions_path: Path to save predictions
    """
    logger.info("Performing inference for model...")

    # Load raw input data
    raw_input_df = pd.read_csv(features_path)

    # Load prediction service
    prediction_service = PredictionService.from_files(
        model_path=model_path,
        preprocessor_path=preprocessor_path,
    )

    # Make predictions
    predictions = prediction_service.predict(raw_input_df)

    # Create submissions file
    submissions = pd.DataFrame(
        {
            "Id": raw_input_df["Id"],
            TARGET: predictions,
        }
    )

    # Save predictions
    predictions_path.parent.mkdir(parents=True, exist_ok=True)
    submissions.to_csv(predictions_path, index=False)

    logger.info(f"Saved predictions to {predictions_path}")
    logger.success("Inference complete.")


if __name__ == "__main__":
    app()
