# 🧪 Run Tests

How to execute the test suite and understand test results.

## Quick Start

```bash
# Run all tests
uv run pytest

# That's it! ✅
```

## Test Categories

### Run All Tests

```bash
uv run pytest
```

**Output:**
```
===== 136 passed in 7.81s =====
Coverage: 83%
```

### Run by Category

```bash
# Unit tests only (fast)
uv run pytest -m unit

# Integration tests
uv run pytest -m integration

# End-to-end tests
uv run pytest -m e2e

# API tests
uv run pytest -m api
```

### Run Specific Tests

```bash
# Specific file
uv run pytest tests/unit/test_core/test_model.py

# Specific test
uv run pytest tests/unit/test_core/test_model.py::test_model_training

# Pattern matching
uv run pytest -k "test_preprocessing"
```

## Test Options

### With Verbose Output

```bash
uv run pytest -v
```

Shows each test name as it runs.

### Without Coverage

```bash
uv run pytest --no-cov
```

Faster for quick checks.

### With Detailed Output

```bash
uv run pytest -vv
```

Shows full output including print statements.

### Parallel Execution

```bash
uv run pytest -n auto
```

Runs tests in parallel (faster for large suites).

### Stop on First Failure

```bash
uv run pytest -x
```

Useful for debugging.

### Failed Tests Only

```bash
# Run tests that failed last time
uv run pytest --lf

# Run failed tests first, then rest
uv run pytest --ff
```

## Coverage Reports

### Terminal Report

```bash
uv run pytest
```

Shows coverage summary in terminal.

### HTML Report

```bash
uv run pytest --cov-report=html
open htmlcov/index.html
```

Interactive coverage browser.

### Missing Lines

```bash
uv run pytest --cov-report=term-missing
```

Shows which lines aren't covered.

## Test Structure

```
tests/
├── unit/                      # Fast, isolated tests
│   ├── test_config/          # Config tests
│   ├── test_core/            # Core component tests
│   ├── test_data/            # Data preparation tests
│   ├── test_features/        # Feature tests
│   └── test_validation/      # Validation tests
├── integration/               # Multi-component tests
│   ├── test_api.py           # API endpoint tests
│   └── test_prediction_pipeline.py
└── e2e/                       # End-to-end tests
    └── test_complete_pipeline.py
```

## Understanding Test Output

### Success

```
tests/unit/test_core/test_model.py::test_model_fit PASSED     [1%]
tests/unit/test_core/test_model.py::test_model_predict PASSED [2%]
...
===== 136 passed in 7.81s =====
```

### Failure

```
FAILED tests/unit/test_core/test_model.py::test_model_fit - AssertionError

def test_model_fit():
>   assert result == expected
E   AssertionError: assert 0.85 == 0.90
```

Shows:
- Which test failed
- The failing assertion
- Expected vs. actual values

### Coverage

```
Name                                    Stmts   Miss  Cover
---------------------------------------------------------
ames_house_price_prediction/core/
  feature_transformer.py                  45      0   100%
  preprocessing.py                        78      0   100%
  model.py                                41      2    95%
---------------------------------------------------------
TOTAL                                   512     86    83%
```

Shows:
- Lines of code (Stmts)
- Lines not covered (Miss)
- Percentage covered

## Debugging Failed Tests

### Show Print Statements

```bash
uv run pytest -s
```

### Show Full Traceback

```bash
uv run pytest --tb=long
```

### Drop into Debugger

```bash
uv run pytest --pdb
```

Drops into Python debugger on failure.

### Specific Test with Output

```bash
uv run pytest tests/unit/test_core/test_model.py::test_model_fit -s -vv
```

## Writing Tests

### Test Template

```python
def test_feature_description():
    """Test docstring explaining what we're testing."""
    # Arrange - Set up test data
    input_data = create_test_data()
    
    # Act - Execute the code
    result = function_under_test(input_data)
    
    # Assert - Verify results
    assert result == expected_value
    assert result > 0
    assert len(result) == expected_length
```

### Using Fixtures

```python
@pytest.fixture
def sample_data():
    """Fixture providing sample data."""
    return pd.DataFrame({
        'LotArea': [8450, 9600],
        'YearBuilt': [2003, 1976]
    })

def test_with_fixture(sample_data):
    """Test using fixture."""
    result = process_data(sample_data)
    assert len(result) == 2
```

### Parametrized Tests

```python
@pytest.mark.parametrize("input,expected", [
    (1, 2),
    (2, 4),
    (3, 6),
])
def test_double(input, expected):
    """Test doubling numbers."""
    assert double(input) == expected
```

## Continuous Integration

Tests run automatically on GitHub Actions:

```yaml
# .github/workflows/test.yml
- name: Run tests
  run: uv run pytest
```

## Coverage Goals

| Module | Target | Current |
|--------|--------|---------|
| Core | 95%+ | 95%+ ✅ |
| Data | 90%+ | 100% ✅ |
| Features | 90%+ | 100% ✅ |
| Validation | 85%+ | 90% ✅ |
| API | 85%+ | 88% ✅ |
| **Overall** | **80%+** | **83%** ✅ |

## Common Issues

### Import Errors

```
ModuleNotFoundError: No module named 'ames_house_price_prediction'
```

**Solution:**
```bash
# Make sure you're in project root
cd /path/to/house-price-quoting-app

# Activate environment
source .venv/bin/activate
```

### Fixture Not Found

```
fixture 'sample_data' not found
```

**Solution:** Check `tests/conftest.py` for fixture definitions.

### Slow Tests

```bash
# See which tests are slow
uv run pytest --durations=10
```

## Best Practices

✅ **Do:**
- Run tests before committing
- Write tests for new features
- Keep tests fast
- Use descriptive test names
- Test edge cases

❌ **Don't:**
- Skip failing tests
- Write tests that depend on external services
- Use sleep() in tests
- Test implementation details

## Related Documentation

- [Testing strategy →](../explanation/testing-strategy.md)
- [Contributing →](../contributing.md)
- [Architecture →](../explanation/architecture.md)
