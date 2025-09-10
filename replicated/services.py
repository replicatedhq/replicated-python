from typing import TYPE_CHECKING, Optional

from .resources import AsyncCustomer, Customer

if TYPE_CHECKING:
    from .async_client import AsyncReplicatedClient
    from .client import ReplicatedClient


class CustomerService:
    """Service for managing customers."""

    def __init__(self, client: "ReplicatedClient") -> None:
        self._client = client

    def get_or_create(
        self,
        email_address: str,
        channel: Optional[str] = None,
    ) -> Customer:
        """Get or create a customer."""
        # Check if customer ID is cached
        cached_customer_id = self._client.state_manager.get_customer_id()
        if cached_customer_id:
            return Customer(
                self._client,
                cached_customer_id,
                email_address,
                channel,
            )

        # Create or fetch customer
        response = self._client.http_client._make_request(
            "POST",
            "/api/v1/customers",
            json_data={
                "email_address": email_address,
                "channel": channel,
                "app_slug": self._client.app_slug,
            },
            headers=self._client._get_auth_headers(),
        )

        customer_id = response["id"]
        self._client.state_manager.set_customer_id(customer_id)

        # Store dynamic token if provided
        if "dynamic_token" in response:
            dynamic_token = response["dynamic_token"]
            self._client.state_manager.set_dynamic_token(dynamic_token)

        response_data = response.copy()
        response_data.pop("email_address", None)

        return Customer(
            self._client,
            customer_id,
            email_address,
            channel,
            **response_data,
        )


class AsyncCustomerService:
    """Async service for managing customers."""

    def __init__(self, client: "AsyncReplicatedClient") -> None:
        self._client = client

    async def get_or_create(
        self,
        email_address: str,
        channel: Optional[str] = None,
    ) -> AsyncCustomer:
        """Get or create a customer."""
        # Check if customer ID is cached
        cached_customer_id = self._client.state_manager.get_customer_id()
        if cached_customer_id:
            return AsyncCustomer(
                self._client,
                cached_customer_id,
                email_address,
                channel,
            )

        # Create or fetch customer
        response = await self._client.http_client._make_request_async(
            "POST",
            "/api/v1/customers",
            json_data={
                "email_address": email_address,
                "channel": channel,
                "app_slug": self._client.app_slug,
            },
            headers=self._client._get_auth_headers(),
        )

        customer_id = response["id"]
        self._client.state_manager.set_customer_id(customer_id)

        # Store dynamic token if provided
        if "dynamic_token" in response:
            dynamic_token = response["dynamic_token"]
            self._client.state_manager.set_dynamic_token(dynamic_token)

        response_data = response.copy()
        response_data.pop("email_address", None)

        return AsyncCustomer(
            self._client,
            customer_id,
            email_address,
            channel,
            **response_data,
        )
