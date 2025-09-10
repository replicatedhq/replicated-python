.PHONY: install dev test lint format clean build upload

# Install package
install:
	pip install -e .

# Install development dependencies
dev:
	pip install -e .[dev]

# Run tests
test:
	pytest

# Run linting
lint:
	flake8 replicated tests examples
	mypy replicated

# Format code
format:
	black replicated tests examples
	isort replicated tests examples

# Clean build artifacts
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Build package
build: clean
	python -m build

# Upload to PyPI (requires twine)
upload: build
	twine check dist/*
	twine upload dist/*

# Run all checks
check: format lint test
	@echo "All checks passed!"