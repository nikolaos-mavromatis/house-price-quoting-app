"""Prediction script using the new modular architecture."""

from pathlib import Path

import pandas as pd
import typer
from loguru import logger

from ames_house_price_prediction.config import (
    MODEL_PATH,
    MODELS_DIR,
    PREPROCESSOR_PATH,
    PROCESSED_DATA_DIR,
    RAW_DATA_DIR,
    TARGET,
)
from ames_house_price_prediction.core.service import PredictionService
from ames_house_price_prediction.validation import ValidationError, validate_test_data

app = typer.Typer()


@app.command()
def main(
    features_path: Path = RAW_DATA_DIR / "test.csv",
    preprocessor_path: Path = PREPROCESSOR_PATH,
    model_path: Path = MODEL_PATH,
    predictions_path: Path = PROCESSED_DATA_DIR / "submissions.csv",
    skip_validation: bool = False,
):
    """Perform inference using the trained model.

    Args:
        features_path: Path to the raw test data
        preprocessor_path: Path to the fitted preprocessor
        model_path: Path to the trained model
        predictions_path: Path to save predictions
        skip_validation: Skip Great Expectations validation
    """
    logger.info("Performing inference for model...")

    # Load raw input data
    raw_input_df = pd.read_csv(features_path)

    # Validate test data schema
    if not skip_validation:
        try:
            # Extract only the feature columns for validation (exclude Id)
            feature_cols = [col for col in raw_input_df.columns if col != "Id"]
            test_data_for_validation = raw_input_df[feature_cols]

            validation_result = validate_test_data(
                test_data_for_validation, fail_on_error=True
            )
            logger.info(f"Test data validation: {validation_result}")
        except ValidationError as e:
            logger.error(f"Test data validation failed: {e}")
            logger.error(e.validation_result.get_failure_summary())
            raise typer.Exit(code=1)
    else:
        logger.warning("Skipping test data validation (--skip-validation flag set)")

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
