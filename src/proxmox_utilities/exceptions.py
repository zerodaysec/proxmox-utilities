"""
Custom exceptions for Proxmox Utilities.

This module defines the exception hierarchy for handling various error conditions
that can occur during Proxmox operations.
"""


class ProxmoxUtilityError(Exception):
    """Base exception for all Proxmox utility errors."""

    pass


class ValidationError(ProxmoxUtilityError):
    """Raised when input validation fails."""

    pass


class TemplateCreationError(ProxmoxUtilityError):
    """Raised when template creation fails."""

    pass


class VMCreationError(ProxmoxUtilityError):
    """Raised when VM creation/cloning fails."""

    pass


class NetworkError(ProxmoxUtilityError):
    """Raised when network operations fail (e.g., downloading images)."""

    pass


class ProxmoxCommandError(ProxmoxUtilityError):
    """Raised when a Proxmox qm command fails."""

    def __init__(self, command: str, returncode: int, stderr: str) -> None:
        """
        Initialize ProxmoxCommandError.

        Args:
            command: The command that failed
            returncode: The exit code of the command
            stderr: The stderr output from the command
        """
        self.command = command
        self.returncode = returncode
        self.stderr = stderr
        super().__init__(
            f"Command '{command}' failed with exit code {returncode}: {stderr}"
        )
