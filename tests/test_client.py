from unittest.mock import Mock, patch

import pytest

from replicated import AsyncReplicatedClient, ReplicatedClient


class TestReplicatedClient:
    def test_client_initialization(self):
        client = ReplicatedClient(publishable_key="pk_test_123", app_slug="my-app")
        assert client.publishable_key == "pk_test_123"
        assert client.app_slug == "my-app"
        assert client.base_url == "https://replicated.app"

    def test_context_manager(self):
        with ReplicatedClient(
            publishable_key="pk_test_123", app_slug="my-app"
        ) as client:
            assert client is not None

    @patch("replicated.http_client.httpx.Client")
    def test_customer_creation(self, mock_httpx):
        mock_response = Mock()
        mock_response.is_success = True
        mock_response.json.return_value = {
            "id": "customer_123",
            "email_address": "test@example.com",
        }

        mock_client = Mock()
        mock_client.request.return_value = mock_response
        mock_httpx.return_value = mock_client

        client = ReplicatedClient(publishable_key="pk_test_123", app_slug="my-app")

        customer = client.customer.get_or_create("test@example.com")
        assert customer.customer_id == "customer_123"
        assert customer.email_address == "test@example.com"


class TestAsyncReplicatedClient:
    @pytest.mark.asyncio
    async def test_client_initialization(self):
        client = AsyncReplicatedClient(publishable_key="pk_test_123", app_slug="my-app")
        assert client.publishable_key == "pk_test_123"
        assert client.app_slug == "my-app"

    @pytest.mark.asyncio
    async def test_context_manager(self):
        async with AsyncReplicatedClient(
            publishable_key="pk_test_123", app_slug="my-app"
        ) as client:
            assert client is not None
