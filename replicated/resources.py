import logging
from typing import TYPE_CHECKING, Any, Optional, Union

from .fingerprint import get_machine_fingerprint

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from .async_client import AsyncReplicatedClient
    from .client import ReplicatedClient


class Customer:
    """Represents a Replicated customer."""

    def __init__(
        self,
        client: Union["ReplicatedClient", "AsyncReplicatedClient"],
        customer_id: str,
        email_address: str,
        channel: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        self._client = client
        self.customer_id = customer_id
        self.email_address = email_address
        self.channel = channel
        self._data = kwargs

    def get_or_create_instance(self) -> Union["Instance", "AsyncInstance"]:
        """Get or create an instance for this customer."""
        if hasattr(self._client, "_get_or_create_instance_async"):
            # type: ignore[arg-type]
            return AsyncInstance(self._client, self.customer_id)
        else:
            # type: ignore[arg-type]
            return Instance(self._client, self.customer_id)

    def __getattr__(self, name: str) -> Any:
        """Access additional customer data."""
        return self._data.get(name)


class AsyncCustomer(Customer):
    """Async version of Customer."""

    # type: ignore[override]
    async def get_or_create_instance(self) -> "AsyncInstance":
        """Get or create an instance for this customer."""
        # type: ignore[arg-type]
        return AsyncInstance(self._client, self.customer_id)


class Instance:
    """Represents a customer instance."""

    def __init__(
        self,
        client: "ReplicatedClient",
        customer_id: str,
        instance_id: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        self._client = client
        self.customer_id = customer_id
        self.instance_id = instance_id
        self._data = kwargs
        self._status = "ready"

    def send_metric(self, name: str, value: Union[int, float, str]) -> None:
        """Send a metric for this instance."""
        if not self.instance_id:
            self._ensure_instance()
            self._report_instance()

        self._client.http_client._make_request(
            "POST",
            "/application/custom-metrics",
            json_data={"data": {name: value}},
            headers=self._client._get_auth_headers(),
        )

    def set_status(self, status: str) -> None:
        """Set the status of this instance for telemetry reporting."""
        if not self.instance_id:
            self._ensure_instance()
        self._status = status
        self._report_instance()

    def _ensure_instance(self) -> None:
        """Ensure the instance ID is generated and cached."""
        if self.instance_id:
            return

        # Check if instance ID is cached
        cached_instance_id = self._client.state_manager.get_instance_id()
        if cached_instance_id:
            self.instance_id = cached_instance_id
            return

        # Generate deterministic instance_id from fingerprint
        import uuid

        fingerprint = get_machine_fingerprint()
        # Use first 16 bytes of SHA256 hash as UUID
        instance_id = str(uuid.UUID(bytes=bytes.fromhex(fingerprint[:32])))

        self.instance_id = instance_id
        self._client.state_manager.set_instance_id(instance_id)

    def _report_instance(self) -> None:
        """Send instance telemetry to vandoor."""
        if not self.instance_id:
            self._ensure_instance()

        try:
            import base64
            import json
            import socket

            # Get hostname for instance tag
            try:
                hostname = socket.gethostname()
            except Exception as e:
                logger.debug(f"Failed to get hostname: {e}")
                hostname = "unknown"

            # Create instance tags with hostname as instance name
            instance_tags = {"force": True, "tags": {"name": hostname}}
            instance_tags_b64 = base64.b64encode(
                json.dumps(instance_tags).encode()
            ).decode()

            # cluster_id is same as instance_id for non-K8s environments
            headers = {
                **self._client._get_auth_headers(),
                "X-Replicated-InstanceID": self.instance_id,
                "X-Replicated-ClusterID": self.instance_id,
                "X-Replicated-AppStatus": self._status,
                "X-Replicated-InstanceTagData": instance_tags_b64,
            }

            self._client.http_client._make_request(
                "POST",
                "/kots_metrics/license_instance/info",
                headers=headers,
                json_data={},
            )
        except Exception as e:
            # Telemetry is optional - don't fail if it doesn't work
            logger.debug(f"Failed to report instance telemetry: {e}")

    def __getattr__(self, name: str) -> Any:
        """Access additional instance data."""
        return self._data.get(name)


class AsyncInstance:
    """Async version of Instance."""

    def __init__(
        self,
        client: "AsyncReplicatedClient",
        customer_id: str,
        instance_id: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        self._client = client
        self.customer_id = customer_id
        self.instance_id = instance_id
        self._data = kwargs
        self._status = "ready"

    async def send_metric(self, name: str, value: Union[int, float, str]) -> None:
        """Send a metric for this instance."""
        if not self.instance_id:
            await self._ensure_instance()
            await self._report_instance()

        await self._client.http_client._make_request_async(
            "POST",
            "/application/custom-metrics",
            json_data={"data": {name: value}},
            headers=self._client._get_auth_headers(),
        )

    async def set_status(self, status: str) -> None:
        """Set the status of this instance for telemetry reporting."""
        self._status = status
        await self._report_instance()

    async def _ensure_instance(self) -> None:
        """Ensure the instance ID is generated and cached."""
        if self.instance_id:
            return

        # Check if instance ID is cached
        cached_instance_id = self._client.state_manager.get_instance_id()
        if cached_instance_id:
            self.instance_id = cached_instance_id
            return

        # Generate deterministic instance_id from fingerprint
        import uuid

        fingerprint = get_machine_fingerprint()
        # Use first 16 bytes of SHA256 hash as UUID
        instance_id = str(uuid.UUID(bytes=bytes.fromhex(fingerprint[:32])))

        self.instance_id = instance_id
        self._client.state_manager.set_instance_id(instance_id)

    async def _report_instance(self) -> None:
        """Send instance telemetry to vandoor."""
        if not self.instance_id:
            await self._ensure_instance()

        try:
            import base64
            import json
            import socket

            # Get hostname for instance tag
            try:
                hostname = socket.gethostname()
            except Exception as e:
                logger.debug(f"Failed to get hostname: {e}")
                hostname = "unknown"

            # Create instance tags with hostname as instance name
            instance_tags = {"force": True, "tags": {"name": hostname}}
            instance_tags_b64 = base64.b64encode(
                json.dumps(instance_tags).encode()
            ).decode()

            # cluster_id is same as instance_id for non-K8s environments
            headers = {
                **self._client._get_auth_headers(),
                "X-Replicated-InstanceID": self.instance_id,
                "X-Replicated-ClusterID": self.instance_id,
                "X-Replicated-AppStatus": self._status,
                "X-Replicated-InstanceTagData": instance_tags_b64,
            }

            await self._client.http_client._make_request_async(
                "POST",
                "/kots_metrics/license_instance/info",
                headers=headers,
                json_data={},
            )
        except Exception as e:
            # Telemetry is optional - don't fail if it doesn't work
            logger.debug(f"Failed to report instance telemetry: {e}")

    def __getattr__(self, name: str) -> Any:
        """Access additional instance data."""
        return self._data.get(name)
