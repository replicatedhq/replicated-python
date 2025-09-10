from typing import Dict, Optional

from .http_client import SyncHTTPClient
from .services import CustomerService
from .state import StateManager


class ReplicatedClient:
    """Synchronous client for the Replicated SDK."""

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
        
        self.http_client = SyncHTTPClient(
            base_url=base_url,
            timeout=timeout,
        )
        self.state_manager = StateManager(app_slug)
        self.customer = CustomerService(self)

    def __enter__(self) -> "ReplicatedClient":
        self.http_client.__enter__()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.http_client.__exit__(exc_type, exc_val, exc_tb)

    def _get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers for API requests."""
        # Try to use dynamic token first, fall back to publishable key
        dynamic_token = self.state_manager.get_dynamic_token()
        if dynamic_token:
            return {"Authorization": f"Bearer {dynamic_token}"}
        else:
            return {"Authorization": f"Bearer {self.publishable_key}"}