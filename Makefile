.PHONY: install dev test lint format clean build upload ci

# Install package
install:
	uv sync

# Install development dependencies
dev:
	uv sync --extra dev

# Run tests
test:
	uv run pytest

# Run linting
lint:
	uv run flake8 replicated tests examples
	uv run mypy replicated

# Format code
format:
	uv run black replicated tests examples
	uv run isort replicated tests examples

# Clean build artifacts
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Build package
build: clean
	uv build

# Upload to PyPI (requires twine)
upload: build
	uv run twine check dist/*
	uv run twine upload dist/*

# Run all checks (CI simulation - no formatting, just checking)
ci:
	@echo "🔍 Running all CI checks locally..."
	@echo "📦 Installing dependencies..."
	@uv sync --extra dev > /dev/null 2>&1
	@echo "✅ Dependencies installed"
	@echo "🧪 Running tests..."
	@uv run pytest
	@echo "✅ Tests passed"
	@echo "🔍 Running linting..."
	@uv run flake8 replicated tests examples
	@uv run mypy replicated
	@echo "✅ Linting passed"
	@echo "🎨 Checking formatting..."
	@uv run black --check replicated tests examples
	@uv run isort --check-only replicated tests examples
	@echo "✅ Formatting passed"
	@echo "🎉 ALL CI CHECKS PASSED! Ready to push! 🎉"

# Run all checks (formats code first)
check: format lint test
	@echo "All checks passed!"
