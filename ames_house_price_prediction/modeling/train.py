"""Model training script using the new modular architecture."""

from pathlib import Path

from sklearn.preprocessing import QuantileTransformer
import typer
from loguru import logger
import pandas as pd
from sklearn.compose import TransformedTargetRegressor
from sklearn.model_selection import cross_val_score, ShuffleSplit

from ames_house_price_prediction.config import (
    MODEL_PATH,
    PROCESSED_DATA_DIR,
    RIDGE_ALPHA,
    TEST_SIZE,
    RANDOM_STATE,
)
from ames_house_price_prediction.core.model import RidgeRegressionModel

app = typer.Typer()


@app.command()
def main(
    features_path: Path = PROCESSED_DATA_DIR / "features.parquet",
    labels_path: Path = PROCESSED_DATA_DIR / "labels.parquet",
    model_path: Path = MODEL_PATH,
    alpha: float = RIDGE_ALPHA,
    n_splits: int = 5,
    test_size: float = TEST_SIZE,
):
    """Train the house price prediction model.

    Args:
        features_path: Path to the preprocessed features
        labels_path: Path to the target labels
        model_path: Path to save the trained model
        alpha: Ridge regularization parameter
        n_splits: Number of cross-validation splits
        test_size: Test size for cross-validation
    """
    logger.info("Training house price prediction model...")
    X = pd.read_parquet(features_path)
    y = pd.read_parquet(labels_path)

    # Transform target and create model pipeline
    transformer = QuantileTransformer(output_distribution="normal")

    # Create Ridge model with configured alpha
    ridge_model = RidgeRegressionModel(alpha=alpha)

    # Wrap in TransformedTargetRegressor for target transformation
    ml_pipe = TransformedTargetRegressor(
        regressor=ridge_model._model or ridge_model.fit(X.values, y.values)._model,
        transformer=transformer,
    )

    # Perform cross-validation to assess model fit
    logger.info(f"Performing {n_splits}-fold cross-validation...")
    cv = ShuffleSplit(n_splits=n_splits, test_size=test_size, random_state=RANDOM_STATE)
    scores = cross_val_score(ml_pipe, X, y, cv=cv)
    logger.info(
        f"{scores.mean():.2f} accuracy with a standard deviation of {scores.std():.2f}"
    )

    # Train using all available data
    logger.info("Training final model on full dataset...")
    model = ml_pipe.fit(X.values, y.values)

    # Save the trained model
    # Note: We save the TransformedTargetRegressor, not just the Ridge model
    import pickle

    model_path.parent.mkdir(parents=True, exist_ok=True)
    with open(model_path, "wb") as f:
        pickle.dump(model, f, protocol=5)

    logger.info(f"Saved model to {model_path}")
    logger.success("Model training complete.")


if __name__ == "__main__":
    app()
