# 🤝 Contributing

Thank you for your interest in contributing to the AMES House Price Prediction project! This guide will help you get started.

## 🎯 Ways to Contribute

There are many ways to contribute to this project:

- 🐛 **Report bugs** - Found an issue? Let us know!
- ✨ **Suggest features** - Have ideas for improvements?
- 📝 **Improve documentation** - Help make the docs better
- 🔧 **Submit pull requests** - Fix bugs or add features
- 💬 **Answer questions** - Help other users in discussions
- 🧪 **Write tests** - Increase our test coverage
- 📊 **Share use cases** - Tell us how you're using the project

## 🚀 Quick Start

### 1. Fork and Clone

```bash
# Fork the repository on GitHub, then clone your fork
git clone https://github.com/YOUR-USERNAME/ames_house_price_prediction.git
cd ames_house_price_prediction

# Add upstream remote
git remote add upstream https://github.com/nikolaos-mavromatis/ames_house_price_prediction.git
```

### 2. Set Up Development Environment

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install development dependencies
uv pip sync requirements-dev.lock
```

### 3. Create a Branch

```bash
# Create a feature branch
git checkout -b feature/your-feature-name

# Or a bugfix branch
git checkout -b fix/issue-description
```

### 4. Make Your Changes

- Write your code
- Add tests
- Update documentation
- Follow our coding standards (see below)

### 5. Run Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov

# Run specific test categories
uv run pytest -m unit
```

### 6. Submit Pull Request

```bash
# Commit your changes
git add .
git commit -m "feat: add awesome feature"

# Push to your fork
git push origin feature/your-feature-name

# Go to GitHub and create a Pull Request
```

## 📋 Development Guidelines

### Code Style

We follow PEP 8 with these tools:

```bash
# Format code with black
uv run black ames_house_price_prediction/

# Sort imports
uv run isort ames_house_price_prediction/

# Check style
uv run flake8 ames_house_price_prediction/

# Type checking
uv run mypy ames_house_price_prediction/
```

**Configuration:**
- Line length: 99 characters
- Black for formatting
- isort for import sorting
- Type hints required for public APIs

### Commit Messages

We use [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**
```
feat(api): add batch prediction endpoint

fix(validation): handle missing values in cross-field checks

docs(tutorial): improve quick start instructions

test(core): increase coverage for preprocessing module
```

### Testing Requirements

- ✅ All tests must pass
- ✅ New features need tests
- ✅ Bug fixes should include regression tests
- ✅ Maintain or improve coverage (target: 80%+)

**Test Structure:**
```python
def test_feature_description():
    """Test docstring describing what we're testing."""
    # Arrange
    input_data = create_test_data()
    
    # Act
    result = function_under_test(input_data)
    
    # Assert
    assert result == expected_value
```

### Documentation

- Add docstrings to all public functions/classes
- Update relevant documentation in `docs/`
- Add examples for new features
- Update changelog

**Docstring Format (Google Style):**
```python
def predict_price(area: float, quality: int) -> float:
    """Predict house price based on features.
    
    Args:
        area: Lot area in square feet
        quality: Overall quality rating (1-10)
        
    Returns:
        Predicted price in dollars
        
    Raises:
        ValueError: If inputs are out of valid range
        
    Example:
        >>> predict_price(8450, 7)
        184408.00
    """
    ...
```

## 🔍 Code Review Process

### What We Look For

- ✅ **Correctness** - Does it work as intended?
- ✅ **Tests** - Are there adequate tests?
- ✅ **Documentation** - Is it well-documented?
- ✅ **Style** - Does it follow our guidelines?
- ✅ **Performance** - Is it efficient?
- ✅ **Security** - Are there any vulnerabilities?

### Review Timeline

- Initial review within 3-5 business days
- Follow-up responses within 2 business days
- Merge when approved by at least one maintainer

### Addressing Feedback

- Respond to all comments
- Push additional commits to your branch
- Mark conversations as resolved when addressed
- Be respectful and constructive

## 🐛 Reporting Bugs

### Before Reporting

1. Check existing issues
2. Verify it's reproducible
3. Test with latest version
4. Gather relevant information

### Bug Report Template

```markdown
## Description
[Clear description of the bug]

## Steps to Reproduce
1. Step one
2. Step two
3. Step three

## Expected Behavior
[What should happen]

## Actual Behavior
[What actually happens]

## Environment
- OS: [e.g., macOS 14.0]
- Python: [e.g., 3.12.4]
- Version: [e.g., 0.2.0]

## Additional Context
[Screenshots, logs, etc.]
```

## ✨ Feature Requests

### Before Requesting

1. Check existing feature requests
2. Consider if it fits the project scope
3. Think about implementation

### Feature Request Template

```markdown
## Problem
[What problem does this solve?]

## Proposed Solution
[How would you solve it?]

## Alternatives
[What alternatives have you considered?]

## Use Cases
[How would you use this feature?]

## Additional Context
[Mockups, examples, etc.]
```

## 📖 Documentation Contributions

Documentation is just as important as code!

### Types of Documentation

- **Tutorials** - Learning-oriented guides
- **How-To Guides** - Problem-solving recipes
- **Reference** - Technical descriptions
- **Explanation** - Conceptual discussions

### Documentation Style

- Use clear, simple language
- Include code examples
- Add diagrams where helpful
- Follow Diátaxis framework

### Building Docs Locally

```bash
# Install docs dependencies (included in dev)
uv pip sync requirements-dev.lock

# Serve docs locally
mkdocs serve

# Open http://localhost:8000
```

## 🏗️ Architecture Guidelines

### Design Principles

1. **Separation of Concerns** - Each module has one responsibility
2. **Dependency Injection** - Pass dependencies explicitly
3. **Interface-Based Design** - Program to interfaces, not implementations
4. **Testability** - Write testable code
5. **SOLID Principles** - Follow SOLID design principles

### Adding New Features

**For new ML models:**
1. Implement the `Model` interface
2. Add to `core/model.py`
3. Update configuration
4. Add tests
5. Document

**For new preprocessing:**
1. Implement the `Preprocessor` interface
2. Add to `core/preprocessing.py`
3. Ensure pipeline compatibility
4. Add tests
5. Document

**For new features:**
1. Implement the `FeatureTransformer` interface
2. Add to `core/feature_transformer.py`
3. Update validation
4. Add tests
5. Document

## 🎓 Learning Resources

### Understanding the Codebase

- Read the [Architecture explanation](explanation/architecture.md)
- Follow the [First Model tutorial](tutorials/first-model.md)
- Explore the [Code API reference](reference/code-api/core.md)

### ML Concepts

- [scikit-learn documentation](https://scikit-learn.org/)
- [Great Expectations docs](https://docs.greatexpectations.io/)
- [Ridge Regression guide](https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.Ridge.html)

### Python Best Practices

- [PEP 8 Style Guide](https://pep8.org/)
- [Type Hints Guide](https://docs.python.org/3/library/typing.html)
- [pytest documentation](https://docs.pytest.org/)

## 🙏 Recognition

Contributors are recognized in:

- GitHub contributors page
- Release notes
- Project README (for significant contributions)

## 📧 Questions?

- **General questions**: Open a [GitHub Discussion](https://github.com/nikolaos-mavromatis/ames_house_price_prediction/discussions)
- **Bug reports**: Open an [Issue](https://github.com/nikolaos-mavromatis/ames_house_price_prediction/issues)
- **Security issues**: Email [security contact]

---

## 📜 Code of Conduct

### Our Standards

- ✅ Be respectful and inclusive
- ✅ Welcome newcomers
- ✅ Focus on constructive feedback
- ✅ Accept responsibility for mistakes
- ✅ Prioritize community well-being

### Unacceptable Behavior

- ❌ Harassment or discrimination
- ❌ Trolling or insulting comments
- ❌ Personal or political attacks
- ❌ Publishing private information
- ❌ Other unprofessional conduct

### Enforcement

Violations may result in:

1. Warning
2. Temporary ban
3. Permanent ban

Report issues to [maintainer contact].

---

<div align="center">
  <p><strong>Thank you for contributing! 🎉</strong></p>
  <p>Every contribution, no matter how small, makes a difference.</p>
</div>
