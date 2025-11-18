"""
Tests for configuration management.
"""

from pathlib import Path

import pytest

from proxmox_utilities.config import ProxmoxConfig, load_config


class TestProxmoxConfig:
    """Tests for ProxmoxConfig class."""

    def test_default_config(self) -> None:
        """Test default configuration values."""
        config = ProxmoxConfig()

        assert config.data_store == "local-lvm"
        assert config.vm_bridge == "vmbr0"
        assert config.ssh_key_path is None
        assert config.template_memory_mb == 2048
        assert config.template_disk_increase_gb == 30
        assert config.ubuntu_image_base_url == "https://cloud-images.ubuntu.com"
        assert config.download_timeout_seconds == 300
        assert config.max_retries == 3

    def test_custom_config(self, temp_ssh_key: Path) -> None:
        """Test custom configuration values."""
        config = ProxmoxConfig(
            data_store="custom-storage",
            vm_bridge="vmbr1",
            ssh_key_path=temp_ssh_key,
            template_memory_mb=4096,
        )

        assert config.data_store == "custom-storage"
        assert config.vm_bridge == "vmbr1"
        assert config.ssh_key_path == temp_ssh_key
        assert config.template_memory_mb == 4096

    def test_ssh_key_expansion(self, tmp_path: Path) -> None:
        """Test SSH key path expansion."""
        ssh_key = tmp_path / "key.pub"
        ssh_key.write_text("test key")

        config = ProxmoxConfig(ssh_key_path=ssh_key)
        assert config.ssh_key_path.is_absolute()

    def test_invalid_ssh_key_path(self) -> None:
        """Test validation of non-existent SSH key path."""
        with pytest.raises(ValueError, match="SSH key file not found"):
            ProxmoxConfig(ssh_key_path=Path("/nonexistent/key.pub"))

    def test_empty_data_store(self) -> None:
        """Test validation of empty data store."""
        with pytest.raises(ValueError, match="Value cannot be empty"):
            ProxmoxConfig(data_store="")

    def test_empty_vm_bridge(self) -> None:
        """Test validation of empty VM bridge."""
        with pytest.raises(ValueError, match="Value cannot be empty"):
            ProxmoxConfig(vm_bridge="")

    def test_memory_validation(self) -> None:
        """Test memory validation."""
        # Test minimum
        config = ProxmoxConfig(template_memory_mb=512)
        assert config.template_memory_mb == 512

        # Test maximum
        config = ProxmoxConfig(template_memory_mb=65536)
        assert config.template_memory_mb == 65536

        # Test below minimum
        with pytest.raises(ValueError):
            ProxmoxConfig(template_memory_mb=256)

    def test_load_config_function(self) -> None:
        """Test load_config helper function."""
        config = load_config()
        assert isinstance(config, ProxmoxConfig)
