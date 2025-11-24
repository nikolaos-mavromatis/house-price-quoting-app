"""Model configurations and hyperparameters."""

from pathlib import Path

from ames_house_price_prediction.config.paths import MODELS_DIR

# Model artifact paths
MODEL_PATH = MODELS_DIR / "model.pkl"
PREPROCESSOR_PATH = MODELS_DIR / "preprocessor.pkl"

# Ridge regression hyperparameters
RIDGE_ALPHA = 8.5

# Polynomial features configuration
POLY_DEGREE = 2
POLY_INCLUDE_BIAS = False
POLY_INTERACTION_ONLY = False

# Train/test split configuration
TEST_SIZE = 0.2
RANDOM_STATE = 42
