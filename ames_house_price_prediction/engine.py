"""Pipeline orchestration script."""

import typer
from loguru import logger

from ames_house_price_prediction.data import prepare_data
from ames_house_price_prediction.features import generate_features
from ames_house_price_prediction.modeling import make_predictions, train_model

app = typer.Typer()


@app.command()
def engine():
    """Run the complete ML pipeline end-to-end.

    This executes the following steps in sequence:
    1. Data preparation - clean and prepare raw data
    2. Feature generation - engineer features and fit preprocessor
    3. Model training - train the prediction model
    4. Predictions - generate predictions on test data
    """
    logger.info("Running complete ML pipeline...")

    logger.info("Step 1/4: Preparing data...")
    prepare_data()

    logger.info("Step 2/4: Generating features...")
    generate_features()

    logger.info("Step 3/4: Training model...")
    train_model()

    logger.info("Step 4/4: Making predictions...")
    make_predictions()

    logger.success("Pipeline completed successfully.")


if __name__ == "__main__":
    app()
