# Replicated Python SDK

A Python SDK for embedding Replicated customer, custom metrics, and instance insights data in your applications.

## Installation

Install the SDK via pip:

```bash
pip install --upgrade replicated
```

## Usage

### Sync Example

```python
from replicated import ReplicatedClient, InstanceStatus

client = ReplicatedClient(
    publishable_key="replicated_pk_...", 
    app_slug="my-app"
)

# Create a customer (or fetch an existing one)
customer = client.customer.get_or_create(email_address="xxx@yyy.com")

# Get or create the associated instance
instance = customer.get_or_create_instance()

# Use the instance for metrics and status reporting
instance.send_metric("cpu_usage", 0.83)
instance.set_status(InstanceStatus.RUNNING)
instance.set_version("1.2.0")
```

### Async Example

```python
from replicated import AsyncReplicatedClient, InstanceStatus

async def main():
    async with AsyncReplicatedClient(
        publishable_key="replicated_pk_...", 
        app_slug="my-app"
    ) as client:
        customer = await client.customer.get_or_create(email_address="xxx@yyy.com")
        instance = await customer.get_or_create_instance()

        await instance.send_metric("cpu_usage", 0.83)
        await instance.set_status(InstanceStatus.RUNNING)
        await instance.set_version("1.2.0")
```

## Documentation

For detailed documentation, visit [docs.replicated.com/sdk/python](https://docs.replicated.com/sdk/python).

## License

MIT License