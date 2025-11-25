# 🏠 AMES House Price Prediction

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.12-blue.svg" alt="Python 3.12"/>
  <img src="https://img.shields.io/badge/FastAPI-0.122-009688.svg" alt="FastAPI"/>
  <img src="https://img.shields.io/badge/Streamlit-1.51-FF4B4B.svg" alt="Streamlit"/>
  <img src="https://img.shields.io/badge/coverage-83%25-brightgreen.svg" alt="Test Coverage: 83%"/>
</p>

<p align="center">
  <strong>A production-ready machine learning system for predicting house prices using the AMES Housing dataset.</strong>
</p>

---

## 🚀 Quick Start

Get up and running in 30 seconds with Docker:

```bash
git clone <repository-url>
cd house-price-quoting-app
docker compose up
```

Access the services:
- **📚 Documentation**: http://localhost:8002
- **🖥️ Streamlit UI**: http://localhost:8501
- **🔌 API**: http://localhost:8000
- **📖 API Docs**: http://localhost:8000/docs

## ✨ What's Included

- **Machine Learning Pipeline**: Ridge regression with engineered features
- **RESTful API**: FastAPI service with automatic OpenAPI documentation
- **Web Interface**: Streamlit app for interactive predictions
- **Data Validation**: Great Expectations for data quality checks
- **Comprehensive Testing**: 136 tests with 83% coverage
- **Docker Deployment**: One-command setup for all services

## 📖 Documentation

For detailed information, visit the full documentation at **http://localhost:8002** after starting the services.

The documentation includes:
- **[Tutorials](http://localhost:8002/tutorials/)** - Step-by-step guides to get started
- **[How-To Guides](http://localhost:8002/how-to/)** - Practical recipes for common tasks
- **[Reference](http://localhost:8002/reference/)** - Technical API and configuration details
- **[Explanation](http://localhost:8002/explanation/)** - Deep dives into architecture and design decisions

## 🛠️ Development

### Local Setup (Without Docker)

Requires Python 3.12+ and [uv](https://github.com/astral-sh/uv) package manager:

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create environment and install dependencies
python -m venv .venv
source .venv/bin/activate
uv pip sync requirements-dev.lock

# Run tests
pytest

# Start services
cd api && uvicorn main:app --reload &
cd app && streamlit run main.py
```

### Running Tests

```bash
pytest                    # Run all tests
pytest -v                 # Verbose output
pytest --cov              # With coverage report
```

See the [Testing Guide](http://localhost:8002/how-to/run-tests/) for more details.

## 📦 Project Structure

```
├── api/                          # FastAPI service
├── app/                          # Streamlit web interface
├── ames_house_price_prediction/  # Core ML package
│   ├── core/                     # Model training and prediction
│   ├── data/                     # Data loading and preprocessing
│   ├── features/                 # Feature engineering
│   └── validation/               # Data validation with Great Expectations
├── data/                         # Dataset storage
├── docs/                         # MkDocs documentation
├── models/                       # Trained model artifacts
└── tests/                        # Test suite
```

## 🤝 Contributing

Contributions are welcome! See the [Contributing Guide](http://localhost:8002/contributing/) in the documentation.

## 📝 License

This project is open source. See [LICENSE](LICENSE) for details.

## 🔗 Links

- **Documentation**: http://localhost:8002 (after running `docker compose up`)
- **API Documentation**: http://localhost:8000/docs
- **Dataset**: [Ames Housing Dataset](http://jse.amstat.org/v19n3/decock.pdf)

---

<p align="center">
  Made with ❤️ using modern ML engineering practices
</p>
