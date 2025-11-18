"""
Tests for VM creation and management functionality.
"""

from unittest.mock import MagicMock, patch

import pytest

from proxmox_utilities.config import ProxmoxConfig
from proxmox_utilities.exceptions import ValidationError, VMCreationError
from proxmox_utilities.vm import VMCreator


class TestVMCreator:
    """Tests for VMCreator class."""

    def test_initialization_with_config(self, mock_config: ProxmoxConfig) -> None:
        """Test initialization with custom config."""
        creator = VMCreator(mock_config)
        assert creator.config == mock_config

    def test_initialization_without_config(self) -> None:
        """Test initialization with default config."""
        creator = VMCreator()
        assert isinstance(creator.config, ProxmoxConfig)

    @patch("proxmox_utilities.vm.run_command")
    def test_create_vm_success(
        self, mock_run: MagicMock, mock_config: ProxmoxConfig
    ) -> None:
        """Test successful VM creation."""
        creator = VMCreator(mock_config)
        creator.create_vm(
            template_id=9001,
            vm_id=190,
            vm_name="test-vm",
        )

        # Verify qm clone and qm set commands were called
        assert mock_run.call_count >= 2

    @patch("proxmox_utilities.vm.run_command")
    def test_create_vm_with_invalid_template_id(
        self, mock_run: MagicMock, mock_config: ProxmoxConfig
    ) -> None:
        """Test VM creation with invalid template ID."""
        creator = VMCreator(mock_config)

        with pytest.raises(VMCreationError):
            creator.create_vm(
                template_id=50,  # Too low
                vm_id=190,
                vm_name="test-vm",
            )

    @patch("proxmox_utilities.vm.run_command")
    def test_create_vm_with_invalid_vm_id(
        self, mock_run: MagicMock, mock_config: ProxmoxConfig
    ) -> None:
        """Test VM creation with invalid VM ID."""
        creator = VMCreator(mock_config)

        with pytest.raises(VMCreationError):
            creator.create_vm(
                template_id=9001,
                vm_id=50,  # Too low
                vm_name="test-vm",
            )

    @patch("proxmox_utilities.vm.run_command")
    def test_create_vm_with_same_ids(
        self, mock_run: MagicMock, mock_config: ProxmoxConfig
    ) -> None:
        """Test VM creation with same template and VM ID."""
        creator = VMCreator(mock_config)

        with pytest.raises(VMCreationError, match="cannot be the same"):
            creator.create_vm(
                template_id=9001,
                vm_id=9001,  # Same as template
                vm_name="test-vm",
            )

    @patch("proxmox_utilities.vm.run_command")
    def test_create_vm_with_invalid_name(
        self, mock_run: MagicMock, mock_config: ProxmoxConfig
    ) -> None:
        """Test VM creation with invalid name."""
        creator = VMCreator(mock_config)

        with pytest.raises(VMCreationError, match="Invalid VM name"):
            creator.create_vm(
                template_id=9001,
                vm_id=190,
                vm_name="bad;name",  # Invalid character
            )

    @patch("proxmox_utilities.vm.run_command")
    def test_create_and_start_vm(
        self, mock_run: MagicMock, mock_config: ProxmoxConfig
    ) -> None:
        """Test creating and starting a VM."""
        creator = VMCreator(mock_config)
        creator.create_vm(
            template_id=9001,
            vm_id=190,
            vm_name="test-vm",
            start_vm=True,
        )

        # Verify qm start command was called
        calls = [str(call) for call in mock_run.call_args_list]
        assert any("start" in str(call) for call in calls)

    @patch("proxmox_utilities.vm.run_command")
    def test_start_vm(self, mock_run: MagicMock, mock_config: ProxmoxConfig) -> None:
        """Test starting a VM."""
        creator = VMCreator(mock_config)
        creator.start_vm(190)

        mock_run.assert_called_once()
        call_args = mock_run.call_args[0][0]
        assert "qm" in call_args
        assert "start" in call_args

    @patch("proxmox_utilities.vm.run_command")
    def test_stop_vm(self, mock_run: MagicMock, mock_config: ProxmoxConfig) -> None:
        """Test stopping a VM."""
        creator = VMCreator(mock_config)
        creator.stop_vm(190)

        mock_run.assert_called_once()
        call_args = mock_run.call_args[0][0]
        assert "qm" in call_args
        assert "stop" in call_args

    @patch("proxmox_utilities.vm.run_command")
    def test_stop_vm_force(
        self, mock_run: MagicMock, mock_config: ProxmoxConfig
    ) -> None:
        """Test force stopping a VM."""
        creator = VMCreator(mock_config)
        creator.stop_vm(190, force=True)

        call_args = mock_run.call_args[0][0]
        assert "--skiplock" in call_args

    @patch("proxmox_utilities.vm.run_command")
    def test_get_vm_status(
        self, mock_run: MagicMock, mock_config: ProxmoxConfig
    ) -> None:
        """Test getting VM status."""
        mock_run.return_value.stdout = "status: running\nname: test-vm\n"

        creator = VMCreator(mock_config)
        status = creator.get_vm_status(190)

        assert isinstance(status, dict)
        assert "status" in status

    @patch("proxmox_utilities.vm.run_command")
    def test_delete_vm(self, mock_run: MagicMock, mock_config: ProxmoxConfig) -> None:
        """Test deleting a VM."""
        creator = VMCreator(mock_config)
        creator.delete_vm(190)

        call_args = mock_run.call_args[0][0]
        assert "qm" in call_args
        assert "destroy" in call_args
        assert "--purge" in call_args

    @patch("proxmox_utilities.vm.run_command")
    def test_delete_vm_no_purge(
        self, mock_run: MagicMock, mock_config: ProxmoxConfig
    ) -> None:
        """Test deleting a VM without purging."""
        creator = VMCreator(mock_config)
        creator.delete_vm(190, purge=False)

        call_args = mock_run.call_args[0][0]
        assert "--purge" not in call_args
