from typing import Dict, Optional

from .http_client import AsyncHTTPClient
from .services import AsyncCustomerService
from .state import StateManager


class AsyncReplicatedClient:
    """Asynchronous client for the Replicated SDK."""

    def __init__(
        self,
        publishable_key: str,
        app_slug: str,
        base_url: str = "https://replicated.app",
        timeout: float = 30.0,
    ) -> None:
        self.publishable_key = publishable_key
        self.app_slug = app_slug
        self.base_url = base_url
        self.timeout = timeout
        
        self.http_client = AsyncHTTPClient(
            base_url=base_url,
            timeout=timeout,
        )
        self.state_manager = StateManager(app_slug)
        self.customer = AsyncCustomerService(self)

    async def __aenter__(self) -> "AsyncReplicatedClient":
        await self.http_client.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.http_client.__aexit__(exc_type, exc_val, exc_tb)

    def _get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers for API requests."""
        # Try to use dynamic token first, fall back to publishable key
        dynamic_token = self.state_manager.get_dynamic_token()
        if dynamic_token:
            return {"Authorization": f"Bearer {dynamic_token}"}
        else:
            return {"Authorization": f"Bearer {self.publishable_key}"}