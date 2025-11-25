# UV Package Manager Migration

This document summarizes the migration from pip to uv for dependency management.

## Migration Date
2025-11-25

## What Changed

### 1. Dependency Management Files

**Removed:**
- `requirements.txt` (138 lines)
- `requirements-dev.txt` (20 lines)

**Added:**
- `requirements.lock` - Production dependencies (167 packages)
- `requirements-dev.lock` - Development dependencies (202 packages)

**Modified:**
- `pyproject.toml` - Added comprehensive dependency specifications

### 2. Docker Configuration

**Updated Files:**
- `dockerfile-fastapi` - Now uses uv for faster dependency installation
- `dockerfile-streamlit` - Now uses uv for faster dependency installation

**Key Changes:**
```dockerfile
# Old approach
RUN pip install -r requirements.txt

# New approach
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
RUN uv pip install --system -r requirements.lock
```

### 3. Documentation Updates

**Updated Files:**
- `README.md` - Installation instructions now use uv
- `VALIDATION_IMPLEMENTATION.md` - Updated dependency file references

### 4. Dependency Resolution Fixes

Fixed version conflicts during migration:
- **numpy**: Changed from `2.2.6` to `>=1.22.4,<2.0.0` (Great Expectations requirement)
- **altair**: Changed from `5.5.0` to `>=4.2.1,<5.0.0` (Great Expectations requirement)

## Benefits

### Performance
- **10-100x faster** dependency resolution compared to pip
- **Production install**: ~450ms (vs several minutes with pip)
- **Development install**: ~520ms (vs several minutes with pip)

### Reliability
- **Deterministic builds**: Lock files ensure identical environments
- **Better conflict resolution**: Clear error messages for dependency conflicts
- **Reproducible**: Same lock file = same packages every time

### Developer Experience
- **Cleaner separation**: Production vs development dependencies clearly split
- **Easier maintenance**: Single source of truth in `pyproject.toml`
- **Modern tooling**: Follows current Python packaging best practices

## Installation Instructions

### Production Environment
```bash
# Install uv (first time only)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install production dependencies
uv pip sync requirements.lock
```

### Development Environment
```bash
# Install uv (first time only)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install development dependencies (includes all prod deps)
uv pip sync requirements-dev.lock
```

## Adding New Dependencies

### Production Dependency
1. Edit `pyproject.toml`
2. Add package to `[project.dependencies]` section
3. Regenerate lock file:
   ```bash
   uv pip compile pyproject.toml -o requirements.lock
   ```

### Development Dependency
1. Edit `pyproject.toml`
2. Add package to `[project.optional-dependencies.dev]` section
3. Regenerate lock file:
   ```bash
   uv pip compile pyproject.toml --extra dev -o requirements-dev.lock
   ```

## Dependency Structure

### Production Dependencies (109 packages)
Located in `[project.dependencies]`:
- Web frameworks: FastAPI, Streamlit, Uvicorn
- ML/Data science: pandas, numpy, scikit-learn, scipy, lightgbm
- Data validation: Great Expectations, Pydantic
- Visualization: altair, matplotlib, seaborn
- Utilities: loguru, requests, httpx, etc.

### Development Dependencies (70 packages)
Located in `[project.optional-dependencies.dev]`:
- Testing: pytest, pytest-cov, pytest-asyncio, pytest-mock, pytest-xdist
- Code quality: black, flake8, isort, mypy
- Development tools: ipython, ipykernel, jupyter
- Documentation: mkdocs, mkdocs-material, mkdocstrings

## Verification

All installations were tested successfully:
- ✅ Production dependencies install correctly
- ✅ Development dependencies install correctly
- ✅ All imports work as expected
- ✅ No dependency conflicts
- ✅ Docker builds work with uv

## Rollback (Not Recommended)

If you need to roll back to pip for any reason:
1. Restore `requirements.txt` and `requirements-dev.txt` from git history
2. Update Dockerfiles to use `pip install -r requirements.txt`
3. Use `pip install -r requirements.txt` for local development

However, we recommend staying with uv for the performance and reliability benefits.

## Resources

- [uv Documentation](https://github.com/astral-sh/uv)
- [Python Packaging Guide](https://packaging.python.org/)
- [pyproject.toml Specification](https://peps.python.org/pep-0621/)
