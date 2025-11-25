# Architecture Documentation

## Overview

This project implements a modular house price prediction system with clear separation of concerns, making it easy to maintain, test, and extend.

## Project Structure

```
house-price-quoting-app/
├── ames_house_price_prediction/    # Core ML library
│   ├── config/                     # Configuration modules
│   │   ├── paths.py               # Directory paths
│   │   ├── features.py            # Feature definitions
│   │   ├── models.py              # Model configurations
│   │   └── settings.py            # Application settings
│   ├── core/                      # Core abstractions and implementations
│   │   ├── interfaces.py          # Abstract base classes
│   │   ├── feature_transformer.py # Feature engineering
│   │   ├── preprocessing.py       # Data preprocessing
│   │   ├── model.py              # Model implementation
│   │   └── service.py            # Prediction service
│   ├── data/                      # Data preparation
│   │   ├── dataset.py            # Dataset preparation script
│   │   └── utils.py              # Data cleaning utilities
│   ├── features/                  # Feature engineering scripts
│   │   ├── features.py           # Feature generation script
│   │   └── utils.py              # Feature transformation functions (deprecated)
│   ├── modeling/                  # Model training and inference
│   │   ├── train.py              # Training script
│   │   └── predict.py            # Prediction script
│   ├── utils/                     # Utility modules
│   │   └── logging.py            # Logging configuration
│   ├── engine.py                  # Pipeline orchestration
│   └── plots.py                   # Visualization utilities
├── api/                           # FastAPI service
│   └── main.py                   # REST API endpoints
├── app/                           # Streamlit frontend
│   └── main.py                   # User interface
├── data/                          # Data artifacts
│   ├── raw/                      # Original datasets
│   ├── processed/                # Processed outputs
│   ├── interim/                  # Intermediate transformations
│   └── external/                 # Third-party data
└── models/                        # Trained model artifacts
    ├── model.pkl                 # Trained model
    └── preprocessor.pkl          # Fitted preprocessor
```

## Core Architecture

### 1. Configuration Layer (`config/`)

Separated configuration into logical modules:

- **paths.py**: All directory and file paths
- **features.py**: Feature definitions and lists
- **models.py**: Model hyperparameters and artifact paths
- **settings.py**: Application settings (logging, environment)

**Benefits:**
- Easy to modify specific configurations without touching unrelated settings
- Clear separation of concerns
- Can be extended with environment-specific configs

### 2. Core Abstractions (`core/`)

#### Interfaces (`interfaces.py`)

Defines abstract base classes for key components:

- **FeatureTransformer**: Interface for feature engineering
- **Preprocessor**: Interface for data preprocessing (fit, transform, save, load)
- **Model**: Interface for prediction models (fit, predict, save, load)

**Benefits:**
- Enables dependency injection and testing
- Makes it easy to swap implementations
- Enforces consistent APIs across components

#### Implementations

- **HouseFeaturesTransformer** (`feature_transformer.py`): Implements feature engineering logic
- **SklearnPreprocessor** (`preprocessing.py`): Implements scikit-learn based preprocessing
- **RidgeRegressionModel** (`model.py`): Implements Ridge regression model
- **PredictionService** (`service.py`): Orchestrates the complete prediction pipeline

### 3. Prediction Service (`core/service.py`)

Central service that combines all components:

```python
service = PredictionService.from_files()
prediction = service.predict(data)
```

**Features:**
- Single point of entry for predictions
- Handles feature engineering, preprocessing, and model prediction
- Can be initialized from files or with custom components
- Used by both API and CLI scripts

### 4. API Layer (`api/main.py`)

FastAPI service with:
- **Pydantic models** for request/response validation
- **Error handling** with proper HTTP status codes
- **Service layer** integration via PredictionService
- **Health checks** and structured responses
- **Both GET and POST** endpoints for flexibility

### 5. Data Layer (`data/`)

- **dataset.py**: Loads and prepares raw data
- **utils.py**: Reusable data cleaning functions

### 6. Feature Layer (`features/`)

- **features.py**: Uses new modular components (FeatureTransformer, Preprocessor)
- **utils.py**: Legacy functions (kept for backward compatibility)

### 7. Modeling Layer (`modeling/`)

- **train.py**: Uses RidgeRegressionModel for training
- **predict.py**: Uses PredictionService for inference

## Key Improvements

### 1. Modularity

**Before:**
- Single monolithic config file
- Preprocessing logic embedded in feature script
- Duplicated feature engineering across files
- Direct pickle file loading everywhere

**After:**
- Separated config modules by concern
- Abstract interfaces for all components
- Centralized feature engineering
- Service layer for orchestration

### 2. Reusability

Components can be easily reused:

```python
# Use preprocessor anywhere
from ames_house_price_prediction.core.preprocessing import SklearnPreprocessor
preprocessor = SklearnPreprocessor.load("path/to/preprocessor.pkl")

# Use prediction service anywhere
from ames_house_price_prediction.core.service import PredictionService
service = PredictionService.from_files()
prediction = service.predict_single(LotArea=8450, YearBuilt=2003, ...)
```

### 3. Testability

Abstract interfaces enable easy mocking and testing:

```python
# Mock components for testing
class MockPreprocessor(Preprocessor):
    def transform(self, X):
        return X  # Simple pass-through for testing

service = PredictionService(
    feature_transformer=MockFeatureTransformer(),
    preprocessor=MockPreprocessor(),
    model=MockModel()
)
```

### 4. Extensibility

Easy to add new features:

- **New model types**: Implement the Model interface
- **New preprocessing strategies**: Implement the Preprocessor interface
- **New feature engineering**: Implement the FeatureTransformer interface
- **A/B testing**: Create multiple services with different components

### 5. Error Handling

- API validates inputs with Pydantic
- Proper error messages and HTTP status codes
- Service layer handles exceptions gracefully
- Streamlit app shows user-friendly error messages

### 6. Documentation

- Docstrings on all classes and methods
- Type hints throughout
- This architecture document
- Clear module organization

## Usage Examples

### Running the Complete Pipeline

```bash
python -m ames_house_price_prediction.engine
```

### Individual Steps

```bash
# Data preparation
python -m ames_house_price_prediction.data.dataset

# Feature generation
python -m ames_house_price_prediction.features.features

# Model training
python -m ames_house_price_prediction.modeling.train

# Predictions
python -m ames_house_price_prediction.modeling.predict
```

### Using the API

```bash
# Start the API
cd api && uvicorn main:app --reload

# Make a prediction
curl "http://localhost:8000/quote/?LotArea=8450&YearBuilt=2003&YearRemodAdd=2003&OverallQual=7&OverallCond=5"
```

### Using the Streamlit App

```bash
cd app && streamlit run main.py
```

### Using the Service Programmatically

```python
from ames_house_price_prediction.core.service import PredictionService
import pandas as pd

# Load service from saved artifacts
service = PredictionService.from_files()

# Single prediction
price = service.predict_single(
    LotArea=8450,
    YearBuilt=2003,
    YearRemodAdd=2003,
    YrSold=2024,
    OverallQual=7,
    OverallCond=5
)

# Batch predictions
data = pd.DataFrame([...])
prices = service.predict(data)
```

## Migration Guide

### Old Way (Before Refactoring)

```python
# Old config import
from ames_house_price_prediction.config import MODELS_DIR, FEATURES

# Old feature engineering (duplicated everywhere)
from ames_house_price_prediction.features.utils import make_features
df = df.pipe(make_features)

# Old preprocessing (manual pickle loading)
import pickle
with open("preprocessor.pkl", "rb") as f:
    preprocessor = pickle.load(f)

# Old prediction (manual steps)
features = make_features(data)
processed = preprocessor.transform(features)
predictions = model.predict(processed)
```

### New Way (After Refactoring)

```python
# New config imports (specific modules)
from ames_house_price_prediction.config.paths import MODELS_DIR
from ames_house_price_prediction.config.features import FEATURES

# New unified service
from ames_house_price_prediction.core.service import PredictionService
service = PredictionService.from_files()
predictions = service.predict(data)
```

## Design Principles

1. **Separation of Concerns**: Each module has a single, well-defined responsibility
2. **DRY (Don't Repeat Yourself)**: Shared logic is centralized
3. **Interface Segregation**: Small, focused interfaces
4. **Dependency Injection**: Components receive dependencies rather than creating them
5. **Single Source of Truth**: Configuration, feature engineering, and preprocessing logic exist in one place
6. **Fail Fast**: Validate inputs early and provide clear error messages

## Future Enhancements

Potential areas for further improvement:

1. **Model Registry**: Track multiple model versions
2. **Feature Store**: Centralized feature definitions and computation
3. **A/B Testing**: Framework for comparing different models
4. **Data Validation**: Schema validation with libraries like Great Expectations
5. **Monitoring**: Model performance tracking and drift detection
6. **Async Processing**: Support for batch predictions
7. **Unit Tests**: Comprehensive test coverage
8. **CI/CD Pipeline**: Automated testing and deployment
