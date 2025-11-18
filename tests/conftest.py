"""
Pytest configuration and fixtures for ProxBox tests.
"""

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from proxbox.config import ProxmoxConfig


@pytest.fixture
def mock_config() -> ProxmoxConfig:
    """Provide a mock Proxmox configuration for testing."""
    return ProxmoxConfig(
        data_store="test-storage",
        vm_bridge="vmbr0",
        ssh_key_path=None,
        template_memory_mb=2048,
        template_disk_increase_gb=30,
    )


@pytest.fixture
def temp_ssh_key(tmp_path: Path) -> Path:
    """Create a temporary SSH key file for testing."""
    ssh_key = tmp_path / "id_rsa.pub"
    ssh_key.write_text("ssh-rsa AAAAB3NzaC1yc2EAAAA... test@example.com\n")
    return ssh_key


@pytest.fixture
def mock_subprocess(monkeypatch: pytest.MonkeyPatch) -> MagicMock:
    """Mock subprocess.run for command execution."""
    mock_result = MagicMock()
    mock_result.returncode = 0
    mock_result.stdout = ""
    mock_result.stderr = ""

    mock_run = MagicMock(return_value=mock_result)
    monkeypatch.setattr("subprocess.run", mock_run)

    return mock_run


@pytest.fixture
def mock_requests(monkeypatch: pytest.MonkeyPatch) -> MagicMock:
    """Mock requests.get for file downloads."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.headers = {"content-length": "1024"}
    mock_response.iter_content = lambda chunk_size: [b"x" * 1024]
    mock_response.raise_for_status = MagicMock()

    mock_get = MagicMock(return_value=mock_response)
    mock_get.return_value.__enter__ = MagicMock(return_value=mock_response)
    mock_get.return_value.__exit__ = MagicMock(return_value=False)

    monkeypatch.setattr("requests.get", mock_get)

    return mock_get
