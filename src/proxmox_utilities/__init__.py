"""
Proxmox Utilities - Secure, production-ready utilities for Proxmox VM automation.

This package provides Python-based tools for automating common Proxmox VE tasks:
- Creating Ubuntu cloud-init templates
- Cloning VMs from templates
- Managing VM lifecycle operations

Copyright (C) 2024 ZeroDay Security
Licensed under GPLv3+
"""

__version__ = "0.1.0"
__author__ = "ZeroDay Security"
__email__ = "jon@zer0day.net"
__license__ = "GPL-3.0-or-later"

from proxmox_utilities.exceptions import (
    ProxmoxUtilityError,
    TemplateCreationError,
    VMCreationError,
    ValidationError,
    NetworkError,
    ProxmoxCommandError,
)
from proxmox_utilities.template import TemplateCreator, UbuntuRelease
from proxmox_utilities.vm import VMCreator

__all__ = [
    # Version info
    "__version__",
    "__author__",
    "__email__",
    "__license__",
    # Exceptions
    "ProxmoxUtilityError",
    "TemplateCreationError",
    "VMCreationError",
    "ValidationError",
    "NetworkError",
    "ProxmoxCommandError",
    # Main classes
    "TemplateCreator",
    "VMCreator",
    "UbuntuRelease",
]
