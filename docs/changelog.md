# 📝 Changelog

All notable changes to the AMES House Price Prediction project are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Comprehensive Diátaxis-based documentation with MkDocs Material
- GitHub Actions workflow for automatic documentation deployment
- Custom CSS and JavaScript for enhanced documentation experience
- Tutorials section with Quick Start and First Model guides
- How-To guides for common tasks
- Reference documentation for API, configuration, and code
- Explanation section for architectural decisions

## [0.2.0] - 2024-11-25

### Added
- Complete data validation with Great Expectations
- Four validation suites: raw data, engineered features, preprocessed features, API monitoring
- ValidationResult and ValidationError classes for structured validation
- Comprehensive test suite (136 tests, 83% coverage)
- UV package manager integration for faster dependency management
- Separate production and development dependencies
- Migration guide for uv

### Changed
- Migrated from pip to uv for dependency management
- Updated all documentation to use `uv run` commands
- Improved test structure with unit, integration, and E2E categories
- Enhanced README with updated coverage numbers and badges
- Relaxed dependency version constraints for better compatibility

### Fixed
- Numpy version conflict with Great Expectations (now <2.0.0)
- Altair version conflict with Great Expectations (now <5.0.0)
- Type validation to accept both int64 and float64
- Cross-field validation with 99% tolerance for data quality issues
- Test coverage configuration in pyproject.toml

## [0.1.0] - 2024-09-15

### Added
- Initial project structure using Cookiecutter Data Science template
- Core ML pipeline with Ridge regression model
- Feature engineering with LotAge and YearsSinceRemod
- Preprocessing pipeline with polynomial features
- FastAPI REST API service
- Streamlit web interface
- Docker and Docker Compose configuration
- Basic test suite
- Project documentation and README

### Features
- House price prediction with 5 core features
- RESTful API with GET and POST endpoints
- Interactive web UI for predictions
- Model persistence (pkl files)
- Preprocessor pipeline persistence

## [0.0.1] - 2024-08-01

### Added
- Initial repository setup
- Project structure
- Basic README

---

## Release Types

We use semantic versioning:

- **MAJOR** version for incompatible API changes
- **MINOR** version for new functionality in a backward compatible manner  
- **PATCH** version for backward compatible bug fixes

## Categories

- **Added** for new features
- **Changed** for changes in existing functionality
- **Deprecated** for soon-to-be removed features
- **Removed** for now removed features
- **Fixed** for any bug fixes
- **Security** for vulnerability fixes

## Links

- [Unreleased]: https://github.com/nikolaos-mavromatis/ames_house_price_prediction/compare/v0.2.0...HEAD
- [0.2.0]: https://github.com/nikolaos-mavromatis/ames_house_price_prediction/compare/v0.1.0...v0.2.0
- [0.1.0]: https://github.com/nikolaos-mavromatis/ames_house_price_prediction/compare/v0.0.1...v0.1.0
- [0.0.1]: https://github.com/nikolaos-mavromatis/ames_house_price_prediction/releases/tag/v0.0.1
