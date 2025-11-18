"""
Tests for template creation functionality.
"""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from proxmox_utilities.config import ProxmoxConfig
from proxmox_utilities.exceptions import TemplateCreationError
from proxmox_utilities.template import TemplateCreator, UbuntuRelease


class TestUbuntuRelease:
    """Tests for UbuntuRelease enum."""

    def test_release_values(self) -> None:
        """Test Ubuntu release values."""
        assert UbuntuRelease.JAMMY.value == "jammy"
        assert UbuntuRelease.FOCAL.value == "focal"
        assert UbuntuRelease.NOBLE.value == "noble"

    def test_get_latest_lts(self) -> None:
        """Test getting latest LTS release."""
        assert UbuntuRelease.get_latest_lts() == UbuntuRelease.NOBLE


class TestTemplateCreator:
    """Tests for TemplateCreator class."""

    def test_initialization_with_config(self, mock_config: ProxmoxConfig) -> None:
        """Test initialization with custom config."""
        creator = TemplateCreator(mock_config)
        assert creator.config == mock_config

    def test_initialization_without_config(self) -> None:
        """Test initialization with default config."""
        creator = TemplateCreator()
        assert isinstance(creator.config, ProxmoxConfig)

    def test_get_image_url(self, mock_config: ProxmoxConfig) -> None:
        """Test image URL generation."""
        creator = TemplateCreator(mock_config)
        url = creator._get_image_url(UbuntuRelease.JAMMY)

        assert "jammy" in url
        assert "cloudimg-amd64.img" in url
        assert url.startswith(mock_config.ubuntu_image_base_url)

    def test_get_image_path(self, mock_config: ProxmoxConfig) -> None:
        """Test image path generation."""
        creator = TemplateCreator(mock_config)
        path = creator._get_image_path(UbuntuRelease.FOCAL)

        assert isinstance(path, Path)
        assert "focal" in str(path)

    @patch("proxmox_utilities.template.download_file")
    @patch("proxmox_utilities.template.run_command")
    def test_create_template_success(
        self,
        mock_run: MagicMock,
        mock_download: MagicMock,
        mock_config: ProxmoxConfig,
        tmp_path: Path,
    ) -> None:
        """Test successful template creation."""
        # Mock image already exists
        mock_image = tmp_path / "jammy-server-cloudimg-amd64.img"
        mock_image.write_bytes(b"fake image")

        with patch.object(
            TemplateCreator, "_get_image_path", return_value=mock_image
        ):
            creator = TemplateCreator(mock_config)
            creator.create_template(
                release=UbuntuRelease.JAMMY,
                template_id=9001,
            )

        # Verify qm commands were called
        assert mock_run.call_count >= 5

    @patch("proxmox_utilities.template.run_command")
    def test_create_template_with_invalid_id(
        self, mock_run: MagicMock, mock_config: ProxmoxConfig
    ) -> None:
        """Test template creation with invalid ID."""
        creator = TemplateCreator(mock_config)

        with pytest.raises(TemplateCreationError):
            creator.create_template(
                release=UbuntuRelease.JAMMY,
                template_id=50,  # Too low
            )

    @patch("proxmox_utilities.template.download_file")
    @patch("proxmox_utilities.template.run_command")
    def test_create_template_with_custom_settings(
        self,
        mock_run: MagicMock,
        mock_download: MagicMock,
        mock_config: ProxmoxConfig,
        tmp_path: Path,
    ) -> None:
        """Test template creation with custom settings."""
        mock_image = tmp_path / "noble-server-cloudimg-amd64.img"
        mock_image.write_bytes(b"fake image")

        with patch.object(
            TemplateCreator, "_get_image_path", return_value=mock_image
        ):
            creator = TemplateCreator(mock_config)
            creator.create_template(
                release=UbuntuRelease.NOBLE,
                template_id=9002,
                template_name="custom-template",
                memory_mb=4096,
                disk_increase_gb=50,
            )

        # Verify custom values were used
        calls = [str(call) for call in mock_run.call_args_list]
        assert any("4096" in str(call) for call in calls)
        assert any("50" in str(call) for call in calls)
