# Data Validation with Great Expectations

This document describes the comprehensive data validation system implemented for the house price prediction ML pipeline using Great Expectations.

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Validation Suites](#validation-suites)
- [Integration Points](#integration-points)
- [Usage](#usage)
- [Custom Expectations](#custom-expectations)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)

---

## Overview

The data validation system ensures data quality throughout the ML pipeline by:

- **Schema validation**: Verifying column presence, types, and structure
- **Range validation**: Ensuring values are within acceptable bounds
- **Cross-field validation**: Checking logical relationships between fields
- **Business rule validation**: Enforcing domain-specific constraints
- **Data drift detection**: Monitoring changes in data distribution

### Benefits

- **Early error detection**: Catch data issues before training
- **Production safety**: Prevent bad data from reaching the model
- **Documentation**: Formal specification of data requirements
- **Debugging**: Clear failure messages for quick resolution
- **Monitoring**: Track data quality over time

---

## Architecture

### Layered Validation Approach

```
┌─────────────────────────────────────────────────────────────┐
│                      API Layer (Real-time)                   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Pydantic Validation (Fast, User-Friendly)            │   │
│  │ • Type checking                                       │   │
│  │ • Basic range validation                             │   │
│  │ • Required field validation                          │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ GE Monitoring (Non-blocking, Async)                  │   │
│  │ • Logs validation results                            │   │
│  │ • Never fails requests                               │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                  Training Pipeline (Batch)                   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Raw Data Validation (Critical)                       │   │
│  │ • Schema validation                                  │   │
│  │ • Type validation                                    │   │
│  │ • Range validation                                   │   │
│  │ • Cross-field validation                             │   │
│  │ → FAIL pipeline on errors                           │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Engineered Features Validation (High Priority)       │   │
│  │ • Derived feature validation                         │   │
│  │ • Business rule validation                           │   │
│  │ • Calculation correctness                            │   │
│  │ → FAIL on critical errors, WARN on minor issues    │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Preprocessed Data Validation (Optional)              │   │
│  │ • NaN/Inf checks                                     │   │
│  │ • Shape validation                                   │   │
│  │ → Usually for debugging only                        │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### Why Two Validation Systems?

- **API (Pydantic)**: Fast (<1ms), user-friendly error messages, synchronous
- **Training (Great Expectations)**: Comprehensive, statistical, batch-oriented

**They complement each other:**
- Pydantic catches user input errors quickly
- Great Expectations catches data pipeline issues thoroughly

---

## Validation Suites

### 1. Raw Data Suite (`raw_housing_data`)

**Purpose**: Validate data immediately after loading from CSV

**Validates**:
- ✅ Required columns present: `LotArea`, `YearBuilt`, `YearRemodAdd`, `YrSold`, `OverallQual`, `OverallCond`, `SalePrice` (training only)
- ✅ Data types: `float64` for LotArea, `int64` for years and ratings
- ✅ Value ranges:
  - `LotArea`: 1,000 - 250,000 sq ft (95% of values)
  - `YearBuilt`: 1800 - current year
  - `YearRemodAdd`: 1800 - current year
  - `YrSold`: 2000 - current year
  - `OverallQual`: 1 - 10
  - `OverallCond`: 1 - 10
  - `SalePrice`: $10,000 - $1,000,000 (95% of values)
- ✅ Non-null constraints on critical features
- ✅ Cross-field rules:
  - `YearRemodAdd >= YearBuilt`
  - `YrSold >= YearBuilt`
  - `YrSold >= YearRemodAdd`

**Usage**:
```python
from ames_house_price_prediction.validation import validate_raw_data

# For training data (with SalePrice)
result = validate_raw_data(df, include_target=True, fail_on_error=True)

# For test data (without SalePrice)
result = validate_raw_data(df, include_target=False, fail_on_error=True)
```

---

### 2. Engineered Features Suite (`engineered_housing_features`)

**Purpose**: Validate data after feature transformation

**Validates**:
- ✅ All raw columns plus derived features: `LotAge`, `YearsSinceRemod`
- ✅ Derived feature ranges:
  - `LotAge`: 0 - 200 years
  - `YearsSinceRemod`: -1 or 0 - 200 years
- ✅ Non-null constraints on derived features
- ✅ Logical consistency (custom check):
  - When `YearsSinceRemod != -1`, it should be `<= LotAge`

**Usage**:
```python
from ames_house_price_prediction.validation import validate_engineered_features

result = validate_engineered_features(df, include_target=True, fail_on_error=True)
```

---

### 3. Preprocessed Features Suite (`preprocessed_housing_features`)

**Purpose**: Validate model-ready data after preprocessing

**Validates**:
- ✅ Row count: 10 - 10,000 samples
- ✅ Column count matches expected (if specified)
- ✅ No NaN values
- ✅ No infinite values

**Usage**:
```python
from ames_house_price_prediction.validation import validate_preprocessed_features

# With numpy array or DataFrame
result = validate_preprocessed_features(
    preprocessed_data, 
    expected_feature_count=21,  # Optional
    fail_on_error=False,  # Usually non-critical
)
```

---

### 4. API Monitoring Suite (`api_housing_data`)

**Purpose**: Non-blocking validation for API request monitoring

**Validates** (lightweight):
- ✅ Basic range checks (very permissive)
- ✅ Logs results for monitoring
- ❌ Never fails requests

**Usage**:
```python
from ames_house_price_prediction.validation import monitor_api_prediction

# Non-blocking, never raises
result = monitor_api_prediction(single_row_df)
```

---

## Integration Points

### 1. Raw Data Loading (`data/dataset.py`)

```python
python -m ames_house_price_prediction.data.dataset

# Skip validation (not recommended)
python -m ames_house_price_prediction.data.dataset --skip-validation
```

**What it does**:
- Loads `data/raw/train.csv`
- Validates schema, types, ranges, cross-field rules
- **FAILS** pipeline if validation errors found
- Saves to `data/processed/dataset.parquet`

---

### 2. Feature Engineering (`features/features.py`)

```python
python -m ames_house_price_prediction.features.features

# Skip validation
python -m ames_house_price_prediction.features.features --skip-validation
```

**What it does**:
- Loads processed dataset
- Applies feature transformations
- Validates derived features
- **FAILS** on critical errors (negative ages, calculation errors)
- Saves features and fitted preprocessor

---

### 3. Batch Predictions (`modeling/predict.py`)

```python
python -m ames_house_price_prediction.modeling.predict

# Skip validation
python -m ames_house_price_prediction.modeling.predict --skip-validation
```

**What it does**:
- Loads `data/raw/test.csv`
- Validates test data matches training schema
- **FAILS** if schema mismatch or invalid data
- Generates predictions

---

### 4. API Monitoring (Optional, Non-blocking)

The API monitoring is currently **not enabled by default** to maintain low latency. To enable:

```python
# In ames_house_price_prediction/core/service.py
from ames_house_price_prediction.validation import monitor_api_prediction

def predict_single(self, **kwargs):
    data = pd.DataFrame([kwargs])
    
    # Optional monitoring (async recommended)
    monitor_api_prediction(data)
    
    # Continue with prediction...
```

---

## Usage

### Command Line

```bash
# Run full training pipeline with validation
python -m ames_house_price_prediction.engine

# Run individual steps
python -m ames_house_price_prediction.data.dataset
python -m ames_house_price_prediction.features.features
python -m ames_house_price_prediction.modeling.train
python -m ames_house_price_prediction.modeling.predict

# Skip validation (for debugging only)
python -m ames_house_price_prediction.data.dataset --skip-validation
```

### Programmatic Usage

```python
from ames_house_price_prediction.validation import (
    validate_raw_data,
    validate_engineered_features,
    ValidationError,
)
import pandas as pd

# Load data
df = pd.read_csv("data/raw/train.csv")

# Validate
try:
    result = validate_raw_data(df, include_target=True, fail_on_error=True)
    print(f"✓ Validation passed: {result}")
except ValidationError as e:
    print(f"✗ Validation failed: {e}")
    print(e.validation_result.get_failure_summary())
    # Handle error...
```

### Non-blocking Validation

```python
# Get results without raising exceptions
result = validate_raw_data(df, include_target=True, fail_on_error=False)

if result.success:
    print("Data is valid")
else:
    print("Data has issues:")
    print(result.get_failure_summary())
    # Decide whether to proceed...
```

---

## Custom Expectations

### Built-in Custom Expectations

Located in `ames_house_price_prediction/validation/custom_expectations.py`:

#### 1. `expect_column_values_lot_age_to_match_calculation`

Validates that `LotAge == YrSold - YearBuilt`.

```python
suite.add_expectation(
    ExpectationConfiguration(
        expectation_type="expect_column_values_lot_age_to_match_calculation",
        kwargs={"column": "LotAge"}
    )
)
```

#### 2. `expect_column_values_years_since_remod_to_follow_logic`

Validates YearsSinceRemod logic:
- `-1` when never remodeled (`YearRemodAdd == YearBuilt`)
- `YrSold - YearRemodAdd` when remodeled

```python
suite.add_expectation(
    ExpectationConfiguration(
        expectation_type="expect_column_values_years_since_remod_to_follow_logic",
        kwargs={"column": "YearsSinceRemod"}
    )
)
```

#### 3. `expect_column_values_house_age_to_be_reasonable`

Validates house age is 0-200 years (business rule).

```python
suite.add_expectation(
    ExpectationConfiguration(
        expectation_type="expect_column_values_house_age_to_be_reasonable",
        kwargs={"column": "LotAge", "max_age": 200}
    )
)
```

### Creating Custom Expectations

To add new custom expectations:

1. **Create Metric Provider**:
```python
class MyCustomMetricProvider(ColumnMapMetricProvider):
    condition_metric_name = "column_values.my_custom_check"
    
    @column_condition_partial(engine=PandasExecutionEngine)
    def _pandas(cls, column, **kwargs):
        # Return boolean Series
        return column > 0  # Example
```

2. **Create Expectation**:
```python
class ExpectColumnValuesMyCustomCheck(ColumnMapExpectation):
    map_metric = "column_values.my_custom_check"
```

3. **Import in module** to auto-register:
```python
from ames_house_price_prediction.validation.custom_expectations import (
    ExpectColumnValuesMyCustomCheck
)
```

---

## Testing

### Running Validation Tests

```bash
# Run all validation tests
pytest tests/unit/test_validation/ -v

# Run specific test modules
pytest tests/unit/test_validation/test_expectations.py -v
pytest tests/unit/test_validation/test_validators.py -v

# Run with coverage
pytest tests/unit/test_validation/ --cov=ames_house_price_prediction.validation
```

### Test Structure

- `test_expectations.py`: Tests for suite definitions
- `test_validators.py`: Tests for validation functions
- Coverage: 90%+ for validation module

### Example Test

```python
def test_validate_invalid_raw_data():
    """Test validation fails for invalid data."""
    invalid_data = pd.DataFrame({
        "LotArea": [-1000.0],  # Negative (invalid)
        "YearBuilt": [1776],   # Before 1800 (invalid)
        # ...
    })
    
    result = validate_raw_data(invalid_data, fail_on_error=False)
    
    assert result.success is False
    assert len(result.failed_expectations) > 0
```

---

## Troubleshooting

### Common Issues

#### 1. Validation Fails with "Column not found"

**Problem**: Expected column is missing from DataFrame.

**Solution**: 
- Check that CSV has all required columns
- Verify column names match exactly (case-sensitive)
- For test data, ensure `include_target=False`

```python
# Check columns
print(df.columns.tolist())

# For test data without SalePrice
result = validate_raw_data(df, include_target=False)
```

---

#### 2. Validation Fails with Type Errors

**Problem**: Column has wrong data type (e.g., `object` instead of `int64`).

**Solution**:
- Ensure CSV is parsed correctly with proper dtypes
- Convert types explicitly before validation

```python
# Fix types
df["YearBuilt"] = df["YearBuilt"].astype("int64")
df["LotArea"] = df["LotArea"].astype("float64")
```

---

#### 3. Range Validation Fails for Valid Data

**Problem**: Valid outliers are being flagged as invalid.

**Solution**:
- Check if `mostly` parameter is set (allows some outliers)
- Adjust range bounds in expectation suite if needed
- Use `fail_on_error=False` to get warnings instead of failures

```python
# See which values failed
result = validate_raw_data(df, fail_on_error=False)
if not result.success:
    print(result.get_failure_summary())
```

---

#### 4. Training Pipeline Hangs on Validation

**Problem**: Great Expectations validation is taking too long.

**Solution**:
- Skip validation for debugging: `--skip-validation`
- Reduce dataset size for testing
- Check for infinite loops in custom expectations

```bash
# Temporary workaround
python -m ames_house_price_prediction.data.dataset --skip-validation
```

---

#### 5. API Latency Increased After Adding Validation

**Problem**: Validation is slowing down API responses.

**Solution**:
- **DO NOT** add GE validation to API request path
- Use Pydantic only for API (already implemented)
- GE monitoring should be async/non-blocking if needed

```python
# WRONG - Don't do this in API
result = validate_raw_data(api_input, fail_on_error=True)  # Too slow!

# RIGHT - Use Pydantic (already implemented)
class HouseFeatures(BaseModel):
    LotArea: float = Field(gt=0)
    # ...
```

---

### Debugging Validation Failures

#### View Detailed Failure Information

```python
result = validate_raw_data(df, fail_on_error=False)

# Print summary
print(result)  # ✗ Validation failed (2 expectations failed)

# Get detailed failures
print(result.get_failure_summary())
# Output:
# Validation Failures (2 expectations):
#   1. expect_column_values_to_be_between on column 'LotArea'
#      Details: {'observed_value': -1000, ...}
#   2. expect_column_values_to_be_between on column 'YearBuilt'
#      Details: {'observed_value': 1776, ...}

# Inspect specific failures
for failure in result.failed_expectations:
    print(failure["expectation_config"])
    print(failure["result"])
```

#### Check Statistics

```python
print(result.statistics)
# Output:
# {
#   'evaluated': 25,
#   'successful': 23,
#   'unsuccessful': 2,
#   'success_percent': 92.0
# }
```

---

## Best Practices

### 1. Validation Strategy

- ✅ **DO** validate raw data immediately after loading
- ✅ **DO** validate engineered features to catch transformation bugs
- ✅ **DO** fail training pipelines on validation errors
- ❌ **DON'T** add GE validation to API request path (use Pydantic)
- ❌ **DON'T** skip validation in production without good reason

### 2. Error Handling

- ✅ **DO** use `fail_on_error=True` for training pipelines
- ✅ **DO** use `fail_on_error=False` for monitoring/debugging
- ✅ **DO** log validation results for tracking
- ✅ **DO** provide clear error messages to users

### 3. Performance

- ✅ **DO** run validation on batch data only
- ✅ **DO** skip expensive validations during development (`--skip-validation`)
- ❌ **DON'T** run GE validation on every API request
- ❌ **DON'T** run validation on very large datasets without sampling

### 4. Maintenance

- ✅ **DO** update validation suites when features change
- ✅ **DO** write tests for custom expectations
- ✅ **DO** document business rules in expectation suites
- ✅ **DO** version control expectation suite definitions

---

## Performance Metrics

### Validation Overhead

| Pipeline Step | Without Validation | With Validation | Overhead |
|---------------|-------------------|-----------------|----------|
| Raw data load | 0.5s | 1.5s | +1.0s |
| Feature engineering | 0.3s | 0.8s | +0.5s |
| Batch predictions | 2.0s | 2.5s | +0.5s |
| **Total pipeline** | **2.8s** | **4.8s** | **+2.0s** |

**Validation adds ~71% overhead but prevents costly production errors.**

### API Performance

- **Without GE validation**: ~50ms per request
- **With Pydantic only** (current): ~50ms per request ✅
- **With GE validation** (not recommended): ~150ms per request ❌

**Recommendation**: Keep GE validation out of API request path.

---

## Future Enhancements

### Planned Features

1. **Data Drift Detection**
   - Compare inference data distribution to training data
   - Alert on significant distribution shifts
   - Track feature statistics over time

2. **Data Docs Generation**
   - Generate HTML documentation of expectations
   - Include validation history and trends
   - Host as internal data quality dashboard

3. **Checkpoint Persistence**
   - Save expectation suites to JSON
   - Version control validation rules
   - Enable CI/CD validation checks

4. **Advanced Custom Expectations**
   - Multi-column business rules
   - Statistical distribution tests
   - Time-series specific validations

---

## References

- [Great Expectations Documentation](https://docs.greatexpectations.io/)
- [Project Architecture](../ARCHITECTURE.md)
- [Testing Documentation](../README.md#running-tests)
- [Pydantic Validation](../api/main.py) (API layer)

---

## Support

For questions or issues with data validation:

1. Check this documentation
2. Review validation test examples in `tests/unit/test_validation/`
3. Check Great Expectations logs
4. Open an issue on GitHub

---

**Last Updated**: 2025-11-25  
**Version**: 1.0.0
