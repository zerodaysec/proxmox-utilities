"""
Configuration management for Proxmox Utilities.

This module handles configuration loading from environment variables,
config files, and provides sensible defaults.
"""

from pathlib import Path
from typing import Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class ProxmoxConfig(BaseSettings):
    """
    Proxmox configuration settings.

    Settings can be provided via:
    1. Environment variables (prefixed with PROXMOX_)
    2. .env file
    3. Direct initialization

    Attributes:
        data_store: Proxmox data store name (default: local-lvm)
        vm_bridge: Network bridge name (default: vmbr0)
        ssh_key_path: Path to SSH public key for cloud-init
        template_memory_mb: Default template memory in MB (default: 2048)
        template_disk_increase_gb: Disk size increase in GB (default: 30)
        ubuntu_image_base_url: Base URL for Ubuntu cloud images
        download_timeout_seconds: Timeout for image downloads (default: 300)
        max_retries: Maximum retry attempts for network operations (default: 3)
    """

    model_config = SettingsConfigDict(
        env_prefix="PROXMOX_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Storage configuration
    data_store: str = Field(
        default="local-lvm",
        description="Proxmox data store for VM disks",
    )
    vm_bridge: str = Field(
        default="vmbr0",
        description="Network bridge for VM network interfaces",
    )

    # SSH configuration
    ssh_key_path: Optional[Path] = Field(
        default=None,
        description="Path to SSH public key for cloud-init (e.g., ~/.ssh/id_rsa.pub)",
    )

    # Template defaults
    template_memory_mb: int = Field(
        default=2048,
        ge=512,
        le=65536,
        description="Default memory allocation for templates in MB",
    )
    template_disk_increase_gb: int = Field(
        default=30,
        ge=0,
        le=1000,
        description="Disk size increase in GB from base image",
    )

    # Network configuration
    ubuntu_image_base_url: str = Field(
        default="https://cloud-images.ubuntu.com",
        description="Base URL for Ubuntu cloud images",
    )
    download_timeout_seconds: int = Field(
        default=300,
        ge=30,
        le=3600,
        description="Timeout for image downloads in seconds",
    )
    max_retries: int = Field(
        default=3,
        ge=1,
        le=10,
        description="Maximum retry attempts for network operations",
    )

    @field_validator("ssh_key_path", mode="before")
    @classmethod
    def expand_ssh_key_path(cls, v: Optional[str | Path]) -> Optional[Path]:
        """Expand SSH key path to absolute path."""
        if v is None:
            return None
        path = Path(v).expanduser().resolve()
        if not path.exists():
            raise ValueError(f"SSH key file not found: {path}")
        if not path.is_file():
            raise ValueError(f"SSH key path is not a file: {path}")
        return path

    @field_validator("data_store", "vm_bridge")
    @classmethod
    def validate_not_empty(cls, v: str) -> str:
        """Ensure string fields are not empty."""
        if not v or not v.strip():
            raise ValueError("Value cannot be empty")
        return v.strip()


def load_config(config_file: Optional[Path] = None) -> ProxmoxConfig:
    """
    Load Proxmox configuration.

    Args:
        config_file: Optional path to .env file

    Returns:
        ProxmoxConfig instance

    Example:
        >>> config = load_config()
        >>> print(config.data_store)
        local-lvm
    """
    if config_file:
        return ProxmoxConfig(_env_file=config_file)
    return ProxmoxConfig()
