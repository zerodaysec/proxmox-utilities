"""
VM creation and cloning for Proxmox.

This module handles cloning VMs from templates and configuring them.
"""

from typing import Optional

from rich.console import Console

from proxbox.config import ProxmoxConfig
from proxbox.exceptions import ValidationError, VMCreationError
from proxbox.utils import (
    format_error,
    format_info,
    format_success,
    format_warning,
    run_command,
    sanitize_vm_name,
    validate_vm_id,
)

console = Console()


class VMCreator:
    """
    Create and clone Proxmox VMs from templates.

    This class handles:
    1. Cloning VMs from templates
    2. Configuring cloud-init settings
    3. Validating inputs

    Example:
        >>> config = ProxmoxConfig()
        >>> creator = VMCreator(config)
        >>> creator.create_vm(
        ...     template_id=9001,
        ...     vm_id=190,
        ...     vm_name="my-ubuntu-vm"
        ... )
    """

    def __init__(self, config: Optional[ProxmoxConfig] = None) -> None:
        """
        Initialize VMCreator.

        Args:
            config: Proxmox configuration (uses defaults if not provided)
        """
        self.config = config or ProxmoxConfig()

    def _clone_vm(self, template_id: int, vm_id: int, vm_name: str) -> None:
        """
        Clone a VM from a template.

        Args:
            template_id: Source template ID
            vm_id: New VM ID
            vm_name: Name for the new VM
        """
        format_info(
            f"Cloning VM {vm_id} ({vm_name}) from template {template_id}..."
        )

        run_command(
            [
                "qm",
                "clone",
                str(template_id),
                str(vm_id),
                "--name",
                vm_name,
            ]
        )

        format_success(f"VM {vm_id} cloned successfully")

    def _configure_vm(self, vm_id: int) -> None:
        """
        Configure cloud-init and boot settings for cloned VM.

        Args:
            vm_id: VM ID to configure
        """
        format_info(f"Configuring VM {vm_id}...")

        run_command(
            [
                "qm",
                "set",
                str(vm_id),
                "--ide2",
                f"{self.config.data_store}:cloudinit",
                "--boot",
                "c",
                "--bootdisk",
                "scsi0",
                "--serial0",
                "socket",
                "--vga",
                "serial0",
            ]
        )

        format_success(f"VM {vm_id} configured")

    def _set_cloud_init_network(self, vm_id: int, use_dhcp: bool = True) -> None:
        """
        Configure cloud-init network settings.

        Args:
            vm_id: VM ID
            use_dhcp: Use DHCP for IP configuration (default: True)
        """
        if use_dhcp:
            format_info(f"Setting VM {vm_id} network to DHCP...")
            run_command(
                [
                    "qm",
                    "set",
                    str(vm_id),
                    "--ipconfig0",
                    "ip=dhcp",
                ]
            )
            format_success("Network configured for DHCP")

    def create_vm(
        self,
        template_id: int,
        vm_id: int,
        vm_name: str,
        start_vm: bool = False,
        configure_network: bool = True,
    ) -> None:
        """
        Create a new VM by cloning a template.

        Args:
            template_id: Source template ID to clone from
            vm_id: New VM ID (must be unique)
            vm_name: Name for the new VM (alphanumeric, hyphens, underscores only)
            start_vm: Start the VM after creation (default: False)
            configure_network: Configure network for DHCP (default: True)

        Raises:
            ValidationError: If inputs are invalid
            VMCreationError: If VM creation fails

        Example:
            >>> creator = VMCreator()
            >>> creator.create_vm(
            ...     template_id=9001,
            ...     vm_id=190,
            ...     vm_name="my-ubuntu-vm",
            ...     start_vm=True
            ... )
        """
        try:
            # Validate inputs
            validate_vm_id(template_id, min_id=100)
            validate_vm_id(vm_id, min_id=100)

            if template_id == vm_id:
                raise ValidationError(
                    f"Template ID and VM ID cannot be the same: {template_id}"
                )

            # Sanitize VM name to prevent command injection
            try:
                safe_vm_name = sanitize_vm_name(vm_name)
            except ValueError as e:
                raise ValidationError(f"Invalid VM name: {e}") from e

            console.print(f"\n[bold cyan]Creating VM from Template[/bold cyan]")
            console.print(f"  Template ID: {template_id}")
            console.print(f"  New VM ID: {vm_id}")
            console.print(f"  VM Name: {safe_vm_name}\n")

            # Execute creation workflow
            self._clone_vm(template_id, vm_id, safe_vm_name)
            self._configure_vm(vm_id)

            if configure_network:
                self._set_cloud_init_network(vm_id, use_dhcp=True)

            if start_vm:
                self.start_vm(vm_id)

            console.print(
                f"\n[bold green]✓ VM {vm_id} ({safe_vm_name}) "
                f"created successfully![/bold green]"
            )

            if not start_vm:
                format_info(
                    f"VM is ready but not started. Start it with: qm start {vm_id}"
                )

        except Exception as e:
            format_error(f"VM creation failed: {e}")
            raise VMCreationError(
                f"Failed to create VM {vm_id} from template {template_id}: {e}"
            ) from e

    def start_vm(self, vm_id: int) -> None:
        """
        Start a VM.

        Args:
            vm_id: VM ID to start

        Raises:
            ProxmoxCommandError: If start fails
        """
        format_info(f"Starting VM {vm_id}...")

        run_command(["qm", "start", str(vm_id)])

        format_success(f"VM {vm_id} started successfully")

    def stop_vm(self, vm_id: int, force: bool = False) -> None:
        """
        Stop a VM.

        Args:
            vm_id: VM ID to stop
            force: Force stop (hard shutdown) if True, graceful shutdown if False

        Raises:
            ProxmoxCommandError: If stop fails
        """
        action = "force-stopping" if force else "stopping"
        format_info(f"Gracefully {action} VM {vm_id}...")

        command = ["qm", "stop", str(vm_id)]
        if force:
            command.append("--skiplock")

        run_command(command)

        format_success(f"VM {vm_id} stopped")

    def get_vm_status(self, vm_id: int) -> dict[str, str]:
        """
        Get VM status.

        Args:
            vm_id: VM ID

        Returns:
            Dictionary with VM status information

        Raises:
            ProxmoxCommandError: If command fails
        """
        result = run_command(["qm", "status", str(vm_id)])

        # Parse output (format: "status: running")
        status_lines = result.stdout.strip().split("\n")
        status_dict = {}

        for line in status_lines:
            if ":" in line:
                key, value = line.split(":", 1)
                status_dict[key.strip()] = value.strip()

        return status_dict

    def delete_vm(self, vm_id: int, purge: bool = True) -> None:
        """
        Delete a VM.

        Args:
            vm_id: VM ID to delete
            purge: Also remove from backup storage (default: True)

        Raises:
            ProxmoxCommandError: If deletion fails

        Warning:
            This operation is irreversible!
        """
        format_warning(f"Deleting VM {vm_id}...")

        command = ["qm", "destroy", str(vm_id)]
        if purge:
            command.append("--purge")

        run_command(command)

        format_success(f"VM {vm_id} deleted")
