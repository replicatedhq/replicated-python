# Replicated Python SDK Examples

This directory contains examples demonstrating how to use the Replicated Python SDK.

## Setup

Before running the examples, install the SDK and its dependencies.

### Using uv (recommended)

```bash
# Install dependencies
uv sync --extra dev

# Run an example
uv run examples/basic_example.py --publishable-key "your_key" --app-slug "your-app"
```

### Using pip

```bash
# Install dependencies
pip install -e .[dev]

# Run an example
python examples/basic_example.py --publishable-key "your_key" --app-slug "your-app"
```

## Basic Example

The `basic_example.py` script demonstrates the most fundamental usage of the SDK:
- Initializing the Replicated client
- Creating or retrieving a customer
- Creating or retrieving an instance

### Usage

```bash
python3 basic_example.py \
    --publishable-key "your_publishable_key_here" \
    --app-slug "your-app-slug" \
    --customer-email "customer@example.com" \
    --customer-name "John Doe" \
    --channel "stable"
```

### Options

- `--publishable-key`: Your Replicated publishable key (required)
- `--app-slug`: Your application slug (required) 
- `--customer-email`: Customer email address (default: user@example.com)
- `--channel`: Channel for the customer (optional)
- `--customer-name`: Customer name (optional)
- `--base-url`: Base URL for the Replicated API (default: https://replicated.app)

### Using Different Environments

To use the SDK against a different environment (not production), use the `--base-url` flag:

```bash
python3 basic_example.py \
    --publishable-key "your_publishable_key_here" \
    --app-slug "your-app-slug" \
    --base-url "https://staging.replicated.app" \
    --customer-email "customer@example.com" \
    --customer-name "Jane Smith" \
    --channel "beta"
```

## Other Examples

- `sync_example.py`: More comprehensive synchronous example with metrics and status updates
- `async_example.py`: Asynchronous version of the SDK usage