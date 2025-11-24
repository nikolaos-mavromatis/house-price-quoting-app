"""Path configurations for the project."""

from pathlib import Path

# Project root
PROJ_ROOT = Path(__file__).resolve().parents[2]

# Data directories
DATA_DIR = PROJ_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
INTERIM_DATA_DIR = DATA_DIR / "interim"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
EXTERNAL_DATA_DIR = DATA_DIR / "external"

# Model directory
MODELS_DIR = PROJ_ROOT / "models"

# Reports directory
REPORTS_DIR = PROJ_ROOT / "reports"
FIGURES_DIR = REPORTS_DIR / "figures"
