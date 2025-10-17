import os
import tempfile
from pathlib import Path
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
            "customer": {
                "id": "customer_123",
                "email": "test@example.com",
                "name": "test user",
                "serviceToken": "service_token_123",
                "instanceId": "instance_123",
            }
        }

        mock_client = Mock()
        mock_client.request.return_value = mock_response
        mock_httpx.return_value = mock_client

        client = ReplicatedClient(publishable_key="pk_test_123", app_slug="my-app")

        customer = client.customer.get_or_create("test@example.com")
        assert customer.customer_id == "customer_123"
        assert customer.email_address == "test@example.com"

    def test_custom_state_directory(self):
        """Test client with custom absolute state directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            custom_dir = Path(tmpdir) / "custom_state"
            client = ReplicatedClient(
                publishable_key="pk_test_123",
                app_slug="my-app",
                state_directory=str(custom_dir),
            )
            # Resolve both paths to handle symlinks
            # (e.g., /var vs /private/var on macOS)
            assert client.state_manager._state_dir == custom_dir.resolve()
            expected_file = custom_dir.resolve() / "state.json"
            assert client.state_manager._state_file == expected_file
            assert custom_dir.exists()

    def test_custom_state_directory_with_tilde(self):
        """Test that ~ expansion works in custom state directory."""
        client = ReplicatedClient(
            publishable_key="pk_test_123",
            app_slug="my-app",
            state_directory="~/test-replicated-state",
        )
        # Should be expanded to actual home directory
        assert "~" not in str(client.state_manager._state_dir)
        assert str(client.state_manager._state_dir).startswith(str(Path.home()))

    def test_custom_state_directory_relative_path(self):
        """Test that relative paths are resolved in custom state directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Change to temp directory and use relative path
            original_cwd = os.getcwd()
            try:
                os.chdir(tmpdir)
                client = ReplicatedClient(
                    publishable_key="pk_test_123",
                    app_slug="my-app",
                    state_directory="./relative_state",
                )
                # Should be resolved to absolute path
                assert client.state_manager._state_dir.is_absolute()
                assert str(tmpdir) in str(client.state_manager._state_dir)
            finally:
                os.chdir(original_cwd)

    def test_default_state_directory_unchanged(self):
        """Test that default behavior is unchanged when state_directory not provided."""
        client = ReplicatedClient(publishable_key="pk_test_123", app_slug="my-app")
        # Should use platform-specific directory
        state_dir_str = str(client.state_manager._state_dir)
        assert "my-app" in state_dir_str
        assert "Replicated" in state_dir_str

    def test_client_has_machine_id(self):
        """Test that client initializes with a machine_id."""
        client = ReplicatedClient(publishable_key="pk_test_123", app_slug="my-app")
        assert hasattr(client, "_machine_id")
        assert client._machine_id is not None
        assert isinstance(client._machine_id, str)
        assert len(client._machine_id) == 64  # SHA256 hash

    @patch("replicated.http_client.httpx.Client")
    def test_instance_has_machine_id_from_client(self, mock_httpx):
        """Test that instances created from client have the client's machine_id."""
        from replicated.resources import Instance

        mock_response = Mock()
        mock_response.is_success = True
        mock_response.json.return_value = {
            "customer": {
                "id": "customer_123",
                "email": "test@example.com",
                "name": "test user",
                "serviceToken": "service_token_123",
                "instanceId": "instance_123",
            }
        }

        mock_client = Mock()
        mock_client.request.return_value = mock_response
        mock_httpx.return_value = mock_client

        client = ReplicatedClient(publishable_key="pk_test_123", app_slug="my-app")
        customer = client.customer.get_or_create("test@example.com")
        instance = customer.get_or_create_instance()

        assert isinstance(instance, Instance)
        assert hasattr(instance, "_machine_id")
        assert instance._machine_id == client._machine_id

    @patch("replicated.http_client.httpx.Client")
    def test_instance_uses_machine_id_in_headers(self, mock_httpx):
        """Test that instance methods use machine_id as cluster ID in headers."""
        from replicated.resources import Instance

        mock_response = Mock()
        mock_response.is_success = True
        mock_response.json.return_value = {}

        mock_client = Mock()
        mock_client.request.return_value = mock_response
        mock_httpx.return_value = mock_client

        client = ReplicatedClient(publishable_key="pk_test_123", app_slug="my-app")
        instance = Instance(client, "customer_123", "instance_123")

        # Send a metric
        instance.send_metric("test_metric", 42)

        # Verify the request was made with correct headers
        call_args = mock_client.request.call_args
        headers = call_args[1]["headers"]
        assert "X-Replicated-ClusterID" in headers
        assert headers["X-Replicated-ClusterID"] == client._machine_id

    def test_instance_with_service_account_token(self):
        """Test that instances can be created with a service account token."""
        from replicated.resources import Instance

        client = ReplicatedClient(publishable_key="pk_test_123", app_slug="my-app")
        instance = Instance(
            client,
            "customer_123",
            "instance_123",
            service_account_token="test_token_123",
        )

        assert instance._service_account_token == "test_token_123"

    @patch("replicated.http_client.httpx.Client")
    def test_get_or_create_instance_with_service_token(self, mock_httpx):
        """Test that get_or_create_instance passes service token to instance."""
        mock_response = Mock()
        mock_response.is_success = True
        mock_response.json.return_value = {
            "customer": {
                "id": "customer_123",
                "email": "test@example.com",
                "name": "test user",
                "serviceToken": "service_token_123",
                "instanceId": "instance_123",
            }
        }

        mock_client = Mock()
        mock_client.request.return_value = mock_response
        mock_httpx.return_value = mock_client

        client = ReplicatedClient(publishable_key="pk_test_123", app_slug="my-app")
        customer = client.customer.get_or_create("test@example.com")
        instance = customer.get_or_create_instance(
            service_account_token="instance_token_abc"
        )

        assert instance._service_account_token == "instance_token_abc"

    @patch("replicated.http_client.httpx.Client")
    def test_ensure_instance_replaces_dynamic_token_from_api(self, mock_httpx):
        """Test that _ensure_instance replaces dynamic_token with service_token from API."""
        from replicated.resources import Instance

        with tempfile.TemporaryDirectory() as tmpdir:
            mock_response = Mock()
            mock_response.is_success = True
            mock_response.json.return_value = {
                "instance_id": "instance_789",
                "service_token": "api_returned_token_xyz",
            }

            mock_client = Mock()
            mock_client.request.return_value = mock_response
            mock_httpx.return_value = mock_client

            client = ReplicatedClient(
                publishable_key="pk_test_123",
                app_slug="my-app",
                state_directory=tmpdir,
            )

            # Set initial customer token
            client.state_manager.set_dynamic_token("customer_token_abc")

            instance = Instance(client, "customer_123")

            # Trigger instance creation
            instance._ensure_instance()

            # Verify dynamic token was replaced with instance token
            stored_token = client.state_manager.get_dynamic_token()
            assert stored_token == "api_returned_token_xyz"

    @patch("replicated.http_client.httpx.Client")
    def test_service_account_token_replaces_dynamic_token(self, mock_httpx):
        """Test that providing service_account_token replaces the dynamic_token."""
        from replicated.resources import Instance

        with tempfile.TemporaryDirectory() as tmpdir:
            mock_response = Mock()
            mock_response.is_success = True
            mock_response.json.return_value = {
                "instance_id": "instance_789",
            }

            mock_client = Mock()
            mock_client.request.return_value = mock_response
            mock_httpx.return_value = mock_client

            client = ReplicatedClient(
                publishable_key="pk_test_123",
                app_slug="my-app",
                state_directory=tmpdir,
            )

            # Set initial customer token
            client.state_manager.set_dynamic_token("customer_token_abc")

            instance = Instance(
                client, "customer_123", service_account_token="user_provided_token"
            )

            # Trigger instance creation
            instance._ensure_instance()

            # Verify dynamic token was replaced with user-provided token
            stored_token = client.state_manager.get_dynamic_token()
            assert stored_token == "user_provided_token"

    @patch("replicated.http_client.httpx.Client")
    def test_auth_headers_use_dynamic_token(self, mock_httpx):
        """Test that _get_auth_headers uses the dynamic token."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mock_client = Mock()
            mock_httpx.return_value = mock_client

            client = ReplicatedClient(
                publishable_key="pk_test_123",
                app_slug="my-app",
                state_directory=tmpdir,
            )

            # No token set, should use publishable key
            headers = client._get_auth_headers()
            assert headers["Authorization"] == "Bearer pk_test_123"

            # Set dynamic token (could be from customer or instance)
            client.state_manager.set_dynamic_token("dynamic_token_xyz")
            headers = client._get_auth_headers()
            assert headers["Authorization"] == "dynamic_token_xyz"


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

    @pytest.mark.asyncio
    async def test_custom_state_directory(self):
        """Test async client with custom state directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            custom_dir = Path(tmpdir) / "custom_state"
            client = AsyncReplicatedClient(
                publishable_key="pk_test_123",
                app_slug="my-app",
                state_directory=str(custom_dir),
            )
            # Resolve both paths to handle symlinks
            # (e.g., /var vs /private/var on macOS)
            assert client.state_manager._state_dir == custom_dir.resolve()
            expected_file = custom_dir.resolve() / "state.json"
            assert client.state_manager._state_file == expected_file
            assert custom_dir.exists()

    @pytest.mark.asyncio
    async def test_custom_state_directory_with_tilde(self):
        """Test that ~ expansion works in async client custom state directory."""
        client = AsyncReplicatedClient(
            publishable_key="pk_test_123",
            app_slug="my-app",
            state_directory="~/test-replicated-state",
        )
        # Should be expanded to actual home directory
        assert "~" not in str(client.state_manager._state_dir)
        assert str(client.state_manager._state_dir).startswith(str(Path.home()))

    @pytest.mark.asyncio
    async def test_custom_state_directory_relative_path(self):
        """Test that relative paths are resolved in async client."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Change to temp directory and use relative path
            original_cwd = os.getcwd()
            try:
                os.chdir(tmpdir)
                client = AsyncReplicatedClient(
                    publishable_key="pk_test_123",
                    app_slug="my-app",
                    state_directory="./relative_state",
                )
                # Should be resolved to absolute path
                assert client.state_manager._state_dir.is_absolute()
                assert str(tmpdir) in str(client.state_manager._state_dir)
            finally:
                os.chdir(original_cwd)

    @pytest.mark.asyncio
    async def test_default_state_directory_unchanged(self):
        """Test that async client default behavior is unchanged."""
        client = AsyncReplicatedClient(publishable_key="pk_test_123", app_slug="my-app")
        state_dir_str = str(client.state_manager._state_dir)
        assert "my-app" in state_dir_str
        assert "Replicated" in state_dir_str

    @pytest.mark.asyncio
    async def test_client_has_machine_id(self):
        """Test that async client initializes with a machine_id."""
        client = AsyncReplicatedClient(publishable_key="pk_test_123", app_slug="my-app")
        assert hasattr(client, "_machine_id")
        assert client._machine_id is not None
        assert isinstance(client._machine_id, str)
        assert len(client._machine_id) == 64  # SHA256 hash

    @pytest.mark.asyncio
    async def test_instance_has_machine_id_from_client(self):
        """Test that async instances have the client's machine_id."""
        from replicated.resources import AsyncInstance

        with patch("replicated.http_client.httpx.AsyncClient") as mock_httpx:
            mock_response = Mock()
            mock_response.is_success = True
            mock_response.json.return_value = {
                "customer": {
                    "id": "customer_123",
                    "email": "test@example.com",
                    "name": "test user",
                    "serviceToken": "service_token_123",
                    "instanceId": "instance_123",
                }
            }

            mock_client = Mock()
            mock_client.request.return_value = mock_response
            mock_httpx.return_value = mock_client

            client = AsyncReplicatedClient(
                publishable_key="pk_test_123", app_slug="my-app"
            )
            customer = await client.customer.get_or_create("test@example.com")
            instance = await customer.get_or_create_instance()

            assert isinstance(instance, AsyncInstance)
            assert hasattr(instance, "_machine_id")
            assert instance._machine_id == client._machine_id

    @pytest.mark.asyncio
    async def test_instance_uses_machine_id_in_headers(self):
        """Test that async instance methods use machine_id as cluster ID in headers."""
        from unittest.mock import AsyncMock

        from replicated.resources import AsyncInstance

        with patch("replicated.http_client.httpx.AsyncClient") as mock_httpx:
            mock_response = Mock()
            mock_response.is_success = True
            mock_response.json.return_value = {}

            mock_client = Mock()
            mock_client.request = AsyncMock(return_value=mock_response)
            mock_httpx.return_value = mock_client

            client = AsyncReplicatedClient(
                publishable_key="pk_test_123", app_slug="my-app"
            )
            instance = AsyncInstance(client, "customer_123", "instance_123")

            # Send a metric
            await instance.send_metric("test_metric", 42)

            # Verify the request was made with correct headers
            call_args = mock_client.request.call_args
            headers = call_args[1]["headers"]
            assert "X-Replicated-ClusterID" in headers
            assert headers["X-Replicated-ClusterID"] == client._machine_id

    @pytest.mark.asyncio
    async def test_instance_token_storage_and_retrieval(self):
        """Test that instance tokens can be stored and retrieved in async client."""
        with tempfile.TemporaryDirectory() as tmpdir:
            client = AsyncReplicatedClient(
                publishable_key="pk_test_123",
                app_slug="my-app",
                state_directory=tmpdir,
            )

            # Store an instance token
            client.state_manager.set_instance_token(
                "instance_123", "instance_token_abc"
            )

            # Retrieve it
            token = client.state_manager.get_instance_token("instance_123")
            assert token == "instance_token_abc"

    @pytest.mark.asyncio
    async def test_instance_with_service_account_token(self):
        """Test that async instances can be created with a service account token."""
        from replicated.resources import AsyncInstance

        client = AsyncReplicatedClient(
            publishable_key="pk_test_123", app_slug="my-app"
        )
        instance = AsyncInstance(
            client,
            "customer_123",
            "instance_123",
            service_account_token="test_token_123",
        )

        assert instance._service_account_token == "test_token_123"

    @pytest.mark.asyncio
    async def test_get_or_create_instance_with_service_token(self):
        """Test that async get_or_create_instance passes service token to instance."""
        with patch("replicated.http_client.httpx.AsyncClient") as mock_httpx:
            from unittest.mock import AsyncMock

            mock_response = Mock()
            mock_response.is_success = True
            mock_response.json.return_value = {
                "customer": {
                    "id": "customer_123",
                    "email": "test@example.com",
                    "name": "test user",
                    "serviceToken": "service_token_123",
                    "instanceId": "instance_123",
                }
            }

            mock_client = Mock()
            mock_client.request = AsyncMock(return_value=mock_response)
            mock_httpx.return_value = mock_client

            client = AsyncReplicatedClient(
                publishable_key="pk_test_123", app_slug="my-app"
            )
            customer = await client.customer.get_or_create("test@example.com")
            instance = await customer.get_or_create_instance(
                service_account_token="instance_token_abc"
            )

            assert instance._service_account_token == "instance_token_abc"

    @pytest.mark.asyncio
    async def test_ensure_instance_stores_service_token_from_api(self):
        """Test that async _ensure_instance stores service_token from API response."""
        from unittest.mock import AsyncMock

        from replicated.resources import AsyncInstance

        with tempfile.TemporaryDirectory() as tmpdir:
            with patch("replicated.http_client.httpx.AsyncClient") as mock_httpx:
                mock_response = Mock()
                mock_response.is_success = True
                mock_response.json.return_value = {
                    "instance_id": "instance_789",
                    "service_token": "api_returned_token_xyz",
                }

                mock_client = Mock()
                mock_client.request = AsyncMock(return_value=mock_response)
                mock_httpx.return_value = mock_client

                client = AsyncReplicatedClient(
                    publishable_key="pk_test_123",
                    app_slug="my-app",
                    state_directory=tmpdir,
                )
                instance = AsyncInstance(client, "customer_123")

                # Trigger instance creation
                await instance._ensure_instance()

                # Verify token was stored
                stored_token = client.state_manager.get_instance_token("instance_789")
                assert stored_token == "api_returned_token_xyz"

    @pytest.mark.asyncio
    async def test_auth_headers_prefer_instance_token(self):
        """Test that async _get_auth_headers prefers instance token over customer token."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch("replicated.http_client.httpx.AsyncClient") as mock_httpx:
                mock_client = Mock()
                mock_httpx.return_value = mock_client

                client = AsyncReplicatedClient(
                    publishable_key="pk_test_123",
                    app_slug="my-app",
                    state_directory=tmpdir,
                )

                # Set customer-level token
                client.state_manager.set_dynamic_token("customer_token_abc")

                # Set instance-level token
                client.state_manager.set_instance_token(
                    "instance_123", "instance_token_xyz"
                )

                # Without instance_id, should use customer token
                headers = client._get_auth_headers()
                assert headers["Authorization"] == "customer_token_abc"

                # With instance_id, should prefer instance token
                headers = client._get_auth_headers(instance_id="instance_123")
                assert headers["Authorization"] == "instance_token_xyz"

                # With non-existent instance_id, should fall back to customer token
                headers = client._get_auth_headers(instance_id="instance_999")
                assert headers["Authorization"] == "customer_token_abc"
