# Contributing to Replicated Python SDK

Thank you for your interest in contributing to the Replicated Python SDK! This guide will help you get started with development.

## Development Setup

The project supports two development workflows: **UV** (recommended) and **pip** (traditional). Both work identically, but UV is significantly faster.

### Using UV (Recommended)

[UV](https://github.com/astral-sh/uv) is a fast Python package installer (10-100x faster than pip).

#### Installation

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Or via pip
pip install uv
```

#### Setup

```bash
# Clone the repository
git clone https://github.com/replicatedhq/replicated-python.git
cd replicated-python

# Install dependencies (uses uv.lock for reproducible builds)
uv sync --extra dev

# Alternatively, use make
make dev
```

#### Daily Development

```bash
# Run tests
make test
# or: uv run pytest

# Run linting
make lint
# or: uv run flake8 replicated tests examples
# or: uv run mypy replicated

# Format code
make format
# or: uv run black replicated tests examples
# or: uv run isort replicated tests examples

# Run all CI checks locally
make ci
# or: ./check.sh

# Build package
make build
# or: uv build
```

### Using pip (Traditional)

If you prefer the traditional pip workflow, it works exactly the same:

#### Setup

```bash
# Clone the repository
git clone https://github.com/replicatedhq/replicated-python.git
cd replicated-python

# Create virtual environment (optional but recommended)
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -e .[dev]
```

#### Daily Development

```bash
# All the same make commands work
make test
make lint
make format
make ci
make build
```

## Project Structure

```
replicated-python/
├── replicated/          # Main SDK code
│   ├── __init__.py
│   ├── client.py        # Synchronous client
│   ├── async_client.py  # Asynchronous client
│   ├── resources.py     # API resource models
│   └── ...
├── tests/               # Test suite
│   └── test_client.py
├── examples/            # Example scripts
│   ├── basic_example.py
│   ├── sync_example.py
│   └── async_example.py
├── pyproject.toml       # Project configuration & dependencies
├── uv.lock             # Locked dependencies (for UV)
└── Makefile            # Development automation
```

## Making Changes

### Before You Start

1. **Check existing issues**: Look for related issues or discussions
2. **Create an issue**: For significant changes, create an issue first to discuss the approach
3. **Fork the repository**: Create your own fork to work in
4. **Create a branch**: Use a descriptive branch name (e.g., `fix/customer-creation-bug`)

### Development Workflow

1. **Make your changes**: Edit the code in the `replicated/` directory
2. **Add tests**: Add or update tests in `tests/` to cover your changes
3. **Run tests locally**: Ensure all tests pass with `make test`
4. **Format code**: Run `make format` to format with black and isort
5. **Check linting**: Run `make lint` to check with flake8 and mypy
6. **Run full CI**: Run `make ci` to simulate the full CI pipeline locally

### Code Style

We use the following tools to maintain code quality:

- **black**: Code formatting (line length: 88)
- **isort**: Import sorting (black-compatible profile)
- **flake8**: Linting (max line length: 88)
- **mypy**: Type checking (strict mode)

All of these run automatically in CI. Run `make format` and `make lint` before committing.

### Type Hints

We use type hints throughout the codebase. Please add type hints to all new functions and methods:

```python
def get_customer(self, customer_id: str) -> Customer:
    """Get a customer by ID."""
    ...
```

### Testing

We use pytest for testing. Tests should cover:

- **Happy path**: Normal, expected usage
- **Error cases**: How the code handles errors
- **Edge cases**: Boundary conditions and unusual inputs

```python
def test_customer_creation():
    """Test creating a new customer."""
    client = ReplicatedClient(publishable_key="test_key", app_slug="test-app")
    customer = client.customer.get_or_create(email_address="test@example.com")
    assert customer.email_address == "test@example.com"
```

Run tests with:
```bash
make test                    # Run all tests
uv run pytest tests/test_client.py  # Run specific test file
uv run pytest -k test_customer      # Run tests matching pattern
```

## Dependency Management

### Adding Dependencies

Dependencies are managed in `pyproject.toml`:

**Runtime dependencies** (end users need):
```toml
[project]
dependencies = [
    "httpx>=0.24.0",
    "typing-extensions>=4.0.0",
]
```

**Development dependencies** (contributors need):
```toml
[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "black>=23.0.0",
    # ...
]
```

After modifying dependencies:

**With UV:**
```bash
uv sync --extra dev  # Updates uv.lock automatically
```

**With pip:**
```bash
pip install -e .[dev]
```

### Lock File Maintenance (UV)

The `uv.lock` file ensures reproducible builds. It should be updated when:
- Dependencies are added/removed in `pyproject.toml`
- Dependency version ranges are changed
- You want to update to newer versions

```bash
# Update lock file
uv sync --extra dev

# Commit the updated lock file
git add uv.lock
git commit -m "Update dependencies"
```

## Submitting Changes

### Creating a Pull Request

1. **Push your branch**: Push your feature branch to your fork
2. **Create PR**: Open a pull request against the `main` branch
3. **Describe changes**: Provide a clear description of what and why
4. **Link issues**: Reference any related issues (e.g., "Fixes #123")
5. **Wait for CI**: Ensure all CI checks pass

### Pull Request Template

```markdown
## Description
Brief description of what this PR does.

## Changes
- Bullet list of changes made

## Testing
How you tested these changes:
- [ ] Added new tests
- [ ] All existing tests pass
- [ ] Tested locally with example scripts
- [ ] Ran `make ci` successfully

## Related Issues
Fixes #123
```

### Review Process

1. **Automated checks**: CI will run tests, linting, and formatting checks
2. **Code review**: Maintainers will review your code
3. **Revisions**: Address any feedback or requested changes
4. **Merge**: Once approved and CI passes, your PR will be merged

## CI/CD Pipeline

Our CI/CD pipeline runs on GitHub Actions:

### Test Workflow
- Runs on every pull request and push to main
- Tests Python 3.8, 3.9, 3.10, 3.11, and 3.12
- Runs pytest, flake8, mypy, black, and isort
- All checks must pass before merging

### Publish Workflow
- Runs on version tags (e.g., `1.0.0`)
- Builds the package with `uv build`
- Publishes to PyPI using trusted publishing
- Handled by maintainers

## Troubleshooting

### UV Issues

**Problem**: `uv: command not found`
**Solution**: Install UV or use pip workflow instead

**Problem**: "does not match project environment path" warning
**Solution**: This is harmless - UV is using `.venv` correctly

**Problem**: Lock file out of sync
**Solution**: Run `uv sync --extra dev` to update

### Test Failures

**Problem**: Tests fail locally but pass in CI
**Solution**: Ensure you're using the same Python version, run `make dev` to reinstall dependencies

**Problem**: Import errors
**Solution**: Install the package in editable mode: `uv sync --extra dev` or `pip install -e .[dev]`

### Environment Issues

**Problem**: Virtual environment conflicts
**Solution**: Delete `.venv` and `.direnv/` directories, then run `make dev`

```bash
rm -rf .venv .direnv
make dev
```

## Getting Help

- **Issues**: Check [existing issues](https://github.com/replicatedhq/replicated-python/issues)
- **Discussions**: Start a [discussion](https://github.com/replicatedhq/replicated-python/discussions)
- **Documentation**: Read the [API reference](API_REFERENCE.md)
- **Examples**: Check the [examples/](examples/) directory

## Code of Conduct

Be respectful, inclusive, and collaborative. We're all here to build great software together.

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
