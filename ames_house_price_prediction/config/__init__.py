"""Configuration module for the house price prediction project."""

from ames_house_price_prediction.config.features import (
    CAT_FEATURES,
    FEATURES,
    NUM_FEATURES,
    ORD_FEATURES,
    TARGET,
)
from ames_house_price_prediction.config.models import (
    MODEL_PATH,
    POLY_DEGREE,
    POLY_INCLUDE_BIAS,
    POLY_INTERACTION_ONLY,
    PREPROCESSOR_PATH,
    RANDOM_STATE,
    RIDGE_ALPHA,
    TEST_SIZE,
)
from ames_house_price_prediction.config.paths import (
    DATA_DIR,
    EXTERNAL_DATA_DIR,
    FIGURES_DIR,
    INTERIM_DATA_DIR,
    MODELS_DIR,
    PROCESSED_DATA_DIR,
    PROJ_ROOT,
    RAW_DATA_DIR,
    REPORTS_DIR,
)
from ames_house_price_prediction.config.settings import (
    LOG_FORMAT,
    LOG_LEVEL,
)

__all__ = [
    # Paths
    "PROJ_ROOT",
    "DATA_DIR",
    "RAW_DATA_DIR",
    "INTERIM_DATA_DIR",
    "PROCESSED_DATA_DIR",
    "EXTERNAL_DATA_DIR",
    "MODELS_DIR",
    "REPORTS_DIR",
    "FIGURES_DIR",
    # Features
    "TARGET",
    "FEATURES",
    "CAT_FEATURES",
    "ORD_FEATURES",
    "NUM_FEATURES",
    # Models
    "MODEL_PATH",
    "PREPROCESSOR_PATH",
    "RIDGE_ALPHA",
    "POLY_DEGREE",
    "POLY_INCLUDE_BIAS",
    "POLY_INTERACTION_ONLY",
    "TEST_SIZE",
    "RANDOM_STATE",
    # Settings
    "LOG_LEVEL",
    "LOG_FORMAT",
]
