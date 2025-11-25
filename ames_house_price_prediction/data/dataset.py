"""Dataset preparation script."""

from pathlib import Path

import pandas as pd
import typer
from loguru import logger

from ames_house_price_prediction.config.paths import PROCESSED_DATA_DIR, RAW_DATA_DIR
from ames_house_price_prediction.data.utils import clean_dataset
from ames_house_price_prediction.validation import ValidationError, validate_raw_data

app = typer.Typer()


@app.command()
def main(
    input_path: Path = RAW_DATA_DIR / "train.csv",
    output_path: Path = PROCESSED_DATA_DIR / "dataset.parquet",
    skip_validation: bool = False,
):
    logger.info("Processing dataset...")
    # load
    raw_df = pd.read_csv(input_path, index_col="Id")

    # clean
    df = clean_dataset(raw_df)

    # validate
    if not skip_validation:
        try:
            validation_result = validate_raw_data(
                df, include_target=True, fail_on_error=True
            )
            logger.info(f"Data validation: {validation_result}")
        except ValidationError as e:
            logger.error(f"Data validation failed: {e}")
            logger.error(e.validation_result.get_failure_summary())
            raise typer.Exit(code=1)
    else:
        logger.warning("Skipping data validation (--skip-validation flag set)")

    # write dataset
    df.to_parquet(output_path, index=False)
    logger.success("Processing dataset complete.")


if __name__ == "__main__":
    app()
