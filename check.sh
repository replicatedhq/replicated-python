#!/bin/bash

set -e

echo "🔍 Running all CI checks locally..."
echo "=================================="

echo "📦 Installing dependencies..."
uv sync --extra dev > /dev/null 2>&1
echo "✅ Dependencies installed"

echo ""
echo "🧪 Running tests..."
uv run pytest
echo "✅ Tests passed"

echo ""
echo "🔍 Running linting..."
uv run flake8 replicated tests examples
uv run mypy replicated
echo "✅ Linting passed"

echo ""
echo "🎨 Checking formatting..."
uv run black --check replicated tests examples
uv run isort --check-only replicated tests examples
echo "✅ Formatting passed"

echo ""
echo "🎉 ALL CI CHECKS PASSED! Ready to push! 🎉"