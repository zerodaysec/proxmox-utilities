"""
Ubuntu template creation for Proxmox.

This module handles downloading Ubuntu cloud images and creating
Proxmox VM templates with cloud-init support.
"""

from enum import Enum
from pathlib import Path
from typing import Optional

from rich.console import Console

from proxmox_utilities.config import ProxmoxConfig
from proxmox_utilities.exceptions import TemplateCreationError, ValidationError
from proxmox_utilities.utils import (
    download_file,
    format_error,
    format_info,
    format_success,
    format_warning,
    run_command,
    validate_vm_id,
)

console = Console()


class UbuntuRelease(str, Enum):
    """Supported Ubuntu releases."""

    JAMMY = "jammy"  # 22.04 LTS
    FOCAL = "focal"  # 20.04 LTS
    NOBLE = "noble"  # 24.04 LTS

    @classmethod
    def get_latest_lts(cls) -> "UbuntuRelease":
        """Get the latest LTS release."""
        return cls.NOBLE


class TemplateCreator:
    """
    Create Ubuntu cloud-init templates for Proxmox.

    This class handles the complete workflow of:
    1. Downloading Ubuntu cloud images
    2. Creating a Proxmox VM
    3. Importing the disk image
    4. Configuring cloud-init
    5. Converting to a template

    Example:
        >>> config = ProxmoxConfig(ssh_key_path=Path("~/.ssh/id_rsa.pub"))
        >>> creator = TemplateCreator(config)
        >>> creator.create_template(
        ...     release=UbuntuRelease.JAMMY,
        ...     template_id=9001
        ... )
    """

    def __init__(self, config: Optional[ProxmoxConfig] = None) -> None:
        """
        Initialize TemplateCreator.

        Args:
            config: Proxmox configuration (uses defaults if not provided)
        """
        self.config = config or ProxmoxConfig()

    def _get_image_url(self, release: UbuntuRelease) -> str:
        """Get the download URL for an Ubuntu cloud image."""
        return (
            f"{self.config.ubuntu_image_base_url}/"
            f"{release.value}/current/"
            f"{release.value}-server-cloudimg-amd64.img"
        )

    def _get_image_path(self, release: UbuntuRelease) -> Path:
        """Get the local path for downloaded image."""
        return Path(f"/tmp/{release.value}-server-cloudimg-amd64.img")

    def _download_image(self, release: UbuntuRelease) -> Path:
        """
        Download Ubuntu cloud image.

        Args:
            release: Ubuntu release to download

        Returns:
            Path to downloaded image

        Raises:
            NetworkError: If download fails
        """
        url = self._get_image_url(release)
        image_path = self._get_image_path(release)

        # Check if already downloaded
        if image_path.exists():
            format_info(f"Image already exists: {image_path}")
            return image_path

        format_info(f"Downloading Ubuntu {release.value} cloud image...")
        download_file(url, image_path, timeout=self.config.download_timeout_seconds)

        return image_path

    def _create_vm(
        self, template_id: int, template_name: str, memory_mb: int
    ) -> None:
        """
        Create initial VM.

        Args:
            template_id: VM ID for the template
            template_name: Name for the template
            memory_mb: Memory allocation in MB
        """
        format_info(f"Creating VM {template_id} ({template_name})...")

        run_command(
            [
                "qm",
                "create",
                str(template_id),
                "--name",
                template_name,
                "--memory",
                str(memory_mb),
                "--net0",
                f"virtio,bridge={self.config.vm_bridge}",
            ]
        )

        format_success(f"VM {template_id} created")

    def _import_disk(
        self, template_id: int, image_path: Path
    ) -> None:
        """
        Import disk image to Proxmox.

        Args:
            template_id: VM ID
            image_path: Path to disk image
        """
        format_info(f"Importing disk image for VM {template_id}...")

        run_command(
            [
                "qm",
                "importdisk",
                str(template_id),
                str(image_path),
                self.config.data_store,
                "-format",
                "qcow2",
            ],
            timeout=600,  # Image import can take longer
        )

        format_success("Disk imported successfully")

    def _configure_vm(self, template_id: int) -> None:
        """
        Configure VM hardware and cloud-init.

        Args:
            template_id: VM ID to configure
        """
        format_info(f"Configuring VM {template_id}...")

        # Set SCSI controller and attach disk
        run_command(
            [
                "qm",
                "set",
                str(template_id),
                "--scsihw",
                "virtio-scsi-pci",
                "--scsi0",
                f"{self.config.data_store}:vm-{template_id}-disk-0",
            ]
        )

        # Configure boot and serial console
        run_command(
            [
                "qm",
                "set",
                str(template_id),
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

        format_success("VM configured")

    def _resize_disk(self, template_id: int, increase_gb: int) -> None:
        """
        Resize VM disk.

        Args:
            template_id: VM ID
            increase_gb: Size increase in GB
        """
        if increase_gb <= 0:
            format_warning("Skipping disk resize (increase_gb <= 0)")
            return

        format_info(f"Resizing disk by +{increase_gb}GB...")

        run_command(
            [
                "qm",
                "resize",
                str(template_id),
                "scsi0",
                f"+{increase_gb}G",
            ]
        )

        format_success(f"Disk resized by +{increase_gb}GB")

    def _configure_cloud_init(self, template_id: int) -> None:
        """
        Configure cloud-init settings.

        Args:
            template_id: VM ID to configure
        """
        format_info("Configuring cloud-init...")

        # Set network to DHCP
        run_command(
            [
                "qm",
                "set",
                str(template_id),
                "--ipconfig0",
                "ip=dhcp",
            ]
        )

        # Set SSH key if provided
        if self.config.ssh_key_path:
            format_info(f"Adding SSH key: {self.config.ssh_key_path}")
            run_command(
                [
                    "qm",
                    "set",
                    str(template_id),
                    "--sshkey",
                    str(self.config.ssh_key_path),
                ]
            )
        else:
            format_warning(
                "No SSH key configured. Set PROXMOX_SSH_KEY_PATH or "
                "manually configure after template creation."
            )

        # Display cloud-init config
        result = run_command(
            ["qm", "cloudinit", "dump", str(template_id), "user"],
            check=False,
        )

        if result.returncode == 0:
            console.print("[dim]Cloud-init configuration:[/dim]")
            console.print(result.stdout)

        format_success("Cloud-init configured")

    def _convert_to_template(self, template_id: int) -> None:
        """
        Convert VM to template.

        Args:
            template_id: VM ID to convert
        """
        format_info(f"Converting VM {template_id} to template...")

        run_command(["qm", "template", str(template_id)])

        format_success(f"Template {template_id} created successfully!")

    def _cleanup_image(self, image_path: Path, keep_image: bool) -> None:
        """
        Clean up downloaded image file.

        Args:
            image_path: Path to image file
            keep_image: Whether to keep the image file
        """
        if keep_image:
            format_info(f"Keeping image file: {image_path}")
            return

        try:
            image_path.unlink()
            format_success(f"Cleaned up image file: {image_path}")
        except OSError as e:
            format_warning(f"Failed to delete image file: {e}")

    def create_template(
        self,
        release: UbuntuRelease,
        template_id: int,
        template_name: Optional[str] = None,
        memory_mb: Optional[int] = None,
        disk_increase_gb: Optional[int] = None,
        keep_image: bool = False,
    ) -> None:
        """
        Create an Ubuntu cloud-init template.

        Args:
            release: Ubuntu release to use
            template_id: VM ID for the template (must be > 100)
            template_name: Template name (default: ubuntu-{release}-template)
            memory_mb: Memory in MB (default from config)
            disk_increase_gb: Disk size increase in GB (default from config)
            keep_image: Keep downloaded image file after creation

        Raises:
            ValidationError: If inputs are invalid
            TemplateCreationError: If template creation fails

        Example:
            >>> creator = TemplateCreator()
            >>> creator.create_template(
            ...     release=UbuntuRelease.JAMMY,
            ...     template_id=9001
            ... )
        """
        try:
            # Validate inputs
            validate_vm_id(template_id, min_id=100)

            if template_name is None:
                template_name = f"ubuntu-{release.value}-template"

            if memory_mb is None:
                memory_mb = self.config.template_memory_mb

            if disk_increase_gb is None:
                disk_increase_gb = self.config.template_disk_increase_gb

            console.print(
                f"\n[bold cyan]Creating Ubuntu {release.value} Template[/bold cyan]"
            )
            console.print(f"  ID: {template_id}")
            console.print(f"  Name: {template_name}")
            console.print(f"  Memory: {memory_mb} MB")
            console.print(f"  Disk increase: +{disk_increase_gb} GB\n")

            # Execute creation workflow
            image_path = self._download_image(release)
            self._create_vm(template_id, template_name, memory_mb)
            self._import_disk(template_id, image_path)
            self._configure_vm(template_id)
            self._resize_disk(template_id, disk_increase_gb)
            self._configure_cloud_init(template_id)
            self._convert_to_template(template_id)
            self._cleanup_image(image_path, keep_image)

            console.print(
                f"\n[bold green]✓ Template {template_id} "
                f"({template_name}) created successfully![/bold green]"
            )

        except Exception as e:
            format_error(f"Template creation failed: {e}")
            raise TemplateCreationError(
                f"Failed to create template {template_id}: {e}"
            ) from e
