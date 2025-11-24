# 🏠 AMES House Price Prediction

<p align="center">
  <img src="https://img.shields.io/badge/CCDS-Project%20template-328F97?logo=cookiecutter" alt="CCDS"/>
  <img src="https://img.shields.io/badge/code%20style-black-000000.svg" alt="Code style: black"/>
  <img src="https://img.shields.io/badge/Python-3.12-blue.svg" alt="Python 3.12"/>
  <img src="https://img.shields.io/badge/FastAPI-0.104-009688.svg" alt="FastAPI"/>
  <img src="https://img.shields.io/badge/Streamlit-1.28-FF4B4B.svg" alt="Streamlit"/>
</p>

<p align="center">
  <strong>A production-ready machine learning system for predicting house prices with a modern, modular architecture.</strong>
</p>

<p align="center">
  <a href="#-features">Features</a> •
  <a href="#-quick-start">Quick Start</a> •
  <a href="#-architecture">Architecture</a> •
  <a href="#-usage">Usage</a> •
  <a href="#-api-documentation">API</a> •
  <a href="#-development">Development</a>
</p>

---

## 🌟 Features

- **🎯 Accurate Predictions**: Ridge regression with polynomial features for robust price predictions
- **🔌 RESTful API**: FastAPI-based service with automatic OpenAPI documentation
- **🖥️ Interactive UI**: Beautiful Streamlit web interface for easy predictions
- **🏗️ Modular Architecture**: Clean abstractions with dependency injection for easy testing and extension
- **🐳 Docker Ready**: One-command deployment with Docker Compose
- **📊 Feature Engineering**: Automated feature transformation pipeline
- **✅ Production Ready**: Input validation, error handling, and comprehensive logging

---

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose (recommended)
- OR Python 3.12+ and pip

### Option 1: Docker Compose (Recommended)

**Get up and running in 30 seconds:**

```bash
# Clone the repository
git clone <repository-url>
cd house-price-quoting-app

# Start all services
docker-compose up --build
```

That's it! 🎉 The application is now running:

- **Streamlit UI**: http://localhost:8501
- **FastAPI**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

### Option 2: Local Development Setup

```bash
# Clone the repository
git clone <repository-url>
cd house-price-quoting-app

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the complete ML pipeline (optional - pre-trained models included)
python -m ames_house_price_prediction.engine

# Start the API
cd api
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# In a new terminal, start the Streamlit app
cd app
streamlit run main.py
```

---

## 🏗️ Architecture

### System Overview

```
┌─────────────────┐      HTTP       ┌──────────────┐
│  Streamlit UI   │ ◄──────────────► │   FastAPI    │
│  (Port 8501)    │                  │  (Port 8000) │
└─────────────────┘                  └───────┬──────┘
                                             │
                                             ▼
                                    ┌────────────────┐
                                    │   Prediction   │
                                    │    Service     │
                                    └────────┬───────┘
                                             │
                    ┌────────────────────────┼────────────────────────┐
                    ▼                        ▼                        ▼
            ┌───────────────┐      ┌─────────────────┐     ┌──────────────┐
            │   Feature     │      │  Preprocessor   │     │    Model     │
            │  Transformer  │      │   (Pipeline)    │     │   (Ridge)    │
            └───────────────┘      └─────────────────┘     └──────────────┘
```

### Modular Design

The project follows a clean, layered architecture:

- **`config/`** - Separated configuration (paths, features, models, settings)
- **`core/`** - Reusable abstractions and implementations
  - Abstract interfaces (Model, Preprocessor, FeatureTransformer)
  - PredictionService for orchestration
- **`data/`** - Data preparation and cleaning
- **`features/`** - Feature engineering pipeline
- **`modeling/`** - Model training and inference
- **`api/`** - FastAPI REST service
- **`app/`** - Streamlit web interface

📖 **[Read the full architecture documentation](ARCHITECTURE.md)**

---

## 📦 Project Structure

```
house-price-quoting-app/
├── ames_house_price_prediction/    # Core ML library
│   ├── config/                     # Configuration modules
│   │   ├── paths.py               # Directory paths
│   │   ├── features.py            # Feature definitions
│   │   ├── models.py              # Model configurations
│   │   └── settings.py            # Application settings
│   ├── core/                      # Core abstractions
│   │   ├── interfaces.py          # Abstract base classes
│   │   ├── feature_transformer.py # Feature engineering
│   │   ├── preprocessing.py       # Data preprocessing
│   │   ├── model.py              # Model implementation
│   │   └── service.py            # Prediction service
│   ├── data/                      # Data preparation
│   ├── features/                  # Feature engineering scripts
│   ├── modeling/                  # Training & inference
│   └── utils/                     # Utilities (logging, etc.)
├── api/                           # FastAPI service
│   ├── main.py                   # REST API endpoints
│   └── Dockerfile-fastapi        # API container
├── app/                           # Streamlit frontend
│   ├── main.py                   # Web UI
│   └── Dockerfile-streamlit      # UI container
├── data/                          # Data artifacts
│   ├── raw/                      # Original datasets
│   ├── processed/                # Processed outputs
│   └── interim/                  # Intermediate data
├── models/                        # Trained models
│   ├── model.pkl                 # Ridge regression model
│   └── preprocessor.pkl          # Preprocessing pipeline
├── docs/                          # Documentation
├── notebooks/                     # Jupyter notebooks
├── docker-compose.yml            # Multi-container orchestration
└── requirements.txt              # Python dependencies
```

---

## 💻 Usage

### Using the Web Interface

1. Open http://localhost:8501 in your browser
2. Fill in the house characteristics:
   - **Lot Area**: Size in square feet
   - **Year Built**: Original construction date
   - **Remodeled Year**: Year of last remodel (optional)
   - **Overall Quality**: Rating from 1-10
   - **Overall Condition**: Rating from 1-10
3. Click "Quote me now!" to get your prediction

### Using the API

#### cURL Example

```bash
curl -X GET "http://localhost:8000/quote/?LotArea=8450&YearBuilt=2003&YearRemodAdd=2003&OverallQual=7&OverallCond=5"
```

#### Python Example

```python
import requests

response = requests.get(
    "http://localhost:8000/quote/",
    params={
        "LotArea": 8450,
        "YearBuilt": 2003,
        "YearRemodAdd": 2003,
        "OverallQual": 7,
        "OverallCond": 5,
    }
)

result = response.json()
print(f"Predicted price: ${result['predicted_price']:,.2f}")
```

#### POST Request with JSON

```python
import requests

response = requests.post(
    "http://localhost:8000/quote/",
    json={
        "LotArea": 8450,
        "YearBuilt": 2003,
        "YearRemodAdd": 2003,
        "OverallQual": 7,
        "OverallCond": 5,
    }
)
```

### Using the Prediction Service Programmatically

```python
from ames_house_price_prediction.core.service import PredictionService

# Load the service with trained models
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
print(f"Predicted price: ${price:,.2f}")

# Batch predictions
import pandas as pd
data = pd.DataFrame([...])
predictions = service.predict(data)
```

---

## 📚 API Documentation

### Interactive API Documentation

Visit http://localhost:8000/docs for the auto-generated Swagger UI documentation.

### Endpoints

#### `GET /`
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "message": "House Price Quoting Service is running"
}
```

#### `GET /quote/`
Get a house price prediction using query parameters.

**Parameters:**
- `LotArea` (float): Lot size in square feet
- `YearBuilt` (int): Original construction year
- `YearRemodAdd` (int): Remodel year
- `OverallQual` (int): Overall quality (1-10)
- `OverallCond` (int): Overall condition (1-10)

**Response:**
```json
{
  "predicted_price": 184408.00,
  "input_features": {
    "LotArea": 8450,
    "YearBuilt": 2003,
    "YearRemodAdd": 2003,
    "OverallQual": 7,
    "OverallCond": 5
  }
}
```

#### `POST /quote/`
Get a house price prediction using JSON body (same parameters as GET).

---

## 🛠️ Development

### Running the ML Pipeline

```bash
# Complete pipeline (data prep → features → training → predictions)
python -m ames_house_price_prediction.engine

# Individual steps
python -m ames_house_price_prediction.data.dataset        # Prepare data
python -m ames_house_price_prediction.features.features   # Generate features
python -m ames_house_price_prediction.modeling.train      # Train model
python -m ames_house_price_prediction.modeling.predict    # Make predictions
```

### Running Tests

```bash
# Import verification tests
python -c "from ames_house_price_prediction.core.service import PredictionService; print('✓ All imports work')"

# Component tests
python -c "
from ames_house_price_prediction.core.service import PredictionService
service = PredictionService.from_files()
price = service.predict_single(LotArea=8450, YearBuilt=2003, YearRemodAdd=2003, YrSold=2024, OverallQual=7, OverallCond=5)
print(f'✓ Prediction: \${price:,.2f}')
"
```

### Code Style

This project uses:
- **Black** for code formatting
- **Type hints** throughout
- **Docstrings** for all public APIs

```bash
# Format code
black ames_house_price_prediction/

# Type checking (if mypy is installed)
mypy ames_house_price_prediction/
```

---

## 🐳 Docker Commands

```bash
# Start all services
docker-compose up

# Start in detached mode
docker-compose up -d

# Rebuild images
docker-compose up --build

# Stop all services
docker-compose down

# View logs
docker-compose logs -f

# View logs for specific service
docker-compose logs -f api
docker-compose logs -f app
```

---

## 📊 Model Information

### Algorithm
- **Ridge Regression** with polynomial features (degree 2)
- **Target transformation**: QuantileTransformer for better distribution

### Features Used
- Lot Area (square feet)
- Year Built
- Year Remodeled/Added
- Overall Quality (1-10 scale)
- Overall Condition (1-10 scale)
- **Engineered Features**:
  - Lot Age (YrSold - YearBuilt)
  - Years Since Remodel (YrSold - YearRemodAdd)

### Preprocessing Pipeline
1. Feature engineering (create derived features)
2. Missing value imputation (median strategy)
3. Robust scaling (handles outliers)
4. Polynomial feature generation (degree 2)

---

## 📖 Documentation

- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Detailed architecture documentation
- **[REFACTORING_SUMMARY.md](REFACTORING_SUMMARY.md)** - Migration guide and changes
- **[DEBUGGING_LOG.md](DEBUGGING_LOG.md)** - Issues resolved during development
- **API Docs**: http://localhost:8000/docs (when running)

---

## 🤝 Contributing

Contributions are welcome! This project follows a modular architecture that makes it easy to:

- Add new model types (implement the `Model` interface)
- Add new preprocessing strategies (implement the `Preprocessor` interface)
- Add new features (extend the `FeatureTransformer`)
- Add new endpoints to the API

---

## 📝 License

This project is open source. See [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgments

- Built with the [Cookiecutter Data Science](https://drivendata.org/cookiecutter-data-science/) template
- Uses the [Ames Housing Dataset](http://jse.amstat.org/v19n3/decock.pdf)
- Powered by scikit-learn, FastAPI, and Streamlit

---

## 📧 Contact

For questions or feedback, please open an issue on GitHub.

---

<p align="center">
  Made with ❤️ using modern ML engineering practices
</p>
