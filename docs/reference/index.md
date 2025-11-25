# 📖 Reference

Technical reference documentation for the AMES House Price Prediction system.

## 🎯 About Reference Documentation

Reference documentation provides **precise technical descriptions** of the system's components, APIs, and configuration options. This is where you look up exact details when you need them.

## 📚 Reference Sections

<div class="grid cards" markdown>

-   :material-api:{ .lg .middle } __[API Endpoints](api-endpoints.md)__

    ---

    Complete REST API documentation with all endpoints, parameters, and responses

    [:octicons-arrow-right-24: View API docs](api-endpoints.md)

-   :material-cog:{ .lg .middle } __[Configuration](configuration.md)__

    ---

    All configuration options, environment variables, and settings

    [:octicons-arrow-right-24: Configure](configuration.md)

-   :material-console:{ .lg .middle } __[CLI Commands](cli-commands.md)__

    ---

    Command-line interface reference for all scripts and tools

    [:octicons-arrow-right-24: CLI reference](cli-commands.md)

-   :material-database:{ .lg .middle } __[Data Schema](data-schema.md)__

    ---

    Dataset schema, features, types, and validation rules

    [:octicons-arrow-right-24: View schema](data-schema.md)

-   :material-chart-box:{ .lg .middle } __[Model Specifications](model-specs.md)__

    ---

    Model architecture, hyperparameters, and performance metrics

    [:octicons-arrow-right-24: Model specs](model-specs.md)

-   :material-code-braces:{ .lg .middle } __[Code API](code-api/core.md)__

    ---

    Auto-generated documentation for all Python modules and classes

    [:octicons-arrow-right-24: Code API](code-api/core.md)

</div>

## 🔍 Quick Lookup

### API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/` | GET | Health check |
| `/quote/` | GET | Get prediction (query params) |
| `/quote/` | POST | Get prediction (JSON body) |

[Complete API reference →](api-endpoints.md)

### Configuration Files

| File | Purpose |
|------|---------|
| `pyproject.toml` | Project dependencies and settings |
| `mkdocs.yml` | Documentation configuration |
| `docker-compose.yml` | Multi-container orchestration |
| `.uvrc` | UV package manager quick reference |

[Configuration details →](configuration.md)

### Core Modules

| Module | Description |
|--------|-------------|
| `core.service` | Prediction service orchestration |
| `core.model` | ML model implementation |
| `core.preprocessing` | Data preprocessing pipeline |
| `core.feature_transformer` | Feature engineering |
| `validation` | Data validation with Great Expectations |

[Code API documentation →](code-api/core.md)

## 📊 Data Features

### Input Features

| Feature | Type | Range | Description |
|---------|------|-------|-------------|
| `LotArea` | float | 1,300 - 215,245 | Lot size in square feet |
| `YearBuilt` | int | 1872 - 2010 | Original construction year |
| `YearRemodAdd` | int | 1950 - 2010 | Remodel year |
| `OverallQual` | int | 1 - 10 | Overall material/finish quality |
| `OverallCond` | int | 1 - 10 | Overall condition rating |

[Complete data schema →](data-schema.md)

### Engineered Features

| Feature | Calculation | Purpose |
|---------|-------------|---------|
| `LotAge` | YrSold - YearBuilt | House age |
| `YearsSinceRemod` | YrSold - YearRemodAdd | Recency of updates |

## 🎯 Model Specifications

| Specification | Value |
|---------------|-------|
| **Algorithm** | Ridge Regression |
| **Regularization (α)** | 10.0 |
| **Polynomial Degree** | 2 |
| **Target Transform** | QuantileTransformer |
| **Scaler** | RobustScaler |
| **Input Features** | 7 (5 core + 2 engineered) |
| **Preprocessed Features** | 36 (with polynomials) |

[Detailed model specs →](model-specs.md)

## 🔧 CLI Commands

### Training & Prediction

```bash
# Complete ML pipeline
python -m ames_house_price_prediction.engine

# Individual steps
python -m ames_house_price_prediction.data.dataset
python -m ames_house_price_prediction.features.features
python -m ames_house_price_prediction.modeling.train
python -m ames_house_price_prediction.modeling.predict
```

### Testing

```bash
# Run all tests
uv run pytest

# Run specific categories
uv run pytest -m unit
uv run pytest -m integration
uv run pytest -m e2e
```

[Complete CLI reference →](cli-commands.md)

## 📦 Package Management

### Installation

```bash
# Production dependencies
uv pip sync requirements.lock

# Development dependencies
uv pip sync requirements-dev.lock
```

### Adding Dependencies

```bash
# 1. Edit pyproject.toml
# 2. Regenerate lock file
uv pip compile pyproject.toml -o requirements.lock
```

[Configuration guide →](configuration.md#dependencies)

## 🌐 Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `LOG_LEVEL` | `INFO` | Logging verbosity |
| `MODEL_PATH` | `models/model.pkl` | Path to trained model |
| `DATA_PATH` | `data/raw/` | Path to raw data |

[Complete configuration →](configuration.md#environment-variables)

## 🐳 Docker Configuration

### Services

| Service | Port | Image | Purpose |
|---------|------|-------|---------|
| `api` | 8000 | Built from `dockerfile-fastapi` | REST API |
| `app` | 8501 | Built from `dockerfile-streamlit` | Web UI |

### Volumes

```yaml
volumes:
  - ./models:/models           # Trained models
  - ./data:/data               # Datasets
```

[Docker reference →](configuration.md#docker)

## 📝 Type Annotations

The codebase uses comprehensive type hints for better IDE support and type checking:

```python
def predict_single(
    self,
    LotArea: float,
    YearBuilt: int,
    YearRemodAdd: int,
    YrSold: int,
    OverallQual: int,
    OverallCond: int
) -> float:
    """Predict price for a single house."""
    ...
```

[Type annotations guide →](../docs/TYPE_ANNOTATIONS.md)

## 🧪 Test Coverage

Current test coverage: **83%**

| Module | Coverage |
|--------|----------|
| `config/*` | 100% |
| `core/*` | 95% avg |
| `validation/*` | 90% avg |
| `api/main.py` | 88% |

[Testing details →](../explanation/testing-strategy.md)

## 📖 Related Documentation

Looking for something else?

- **[Tutorials](../tutorials/)** - Learn through examples
- **[How-To Guides](../how-to/)** - Solve specific problems
- **[Explanation](../explanation/)** - Understand the design

---

<div align="center">
  <p>Need more details?</p>
  <p>
    <a href="api-endpoints/">API Reference</a> •
    <a href="configuration/">Configuration</a> •
    <a href="code-api/core/">Code API</a>
  </p>
</div>
