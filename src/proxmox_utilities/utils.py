"""
Utility functions for Proxmox operations.

This module provides common utilities for executing commands,
handling file operations, and other shared functionality.
"""

import hashlib
import subprocess
from pathlib import Path
from typing import Any

from rich.console import Console
from rich.progress import (
    BarColumn,
    DownloadColumn,
    Progress,
    TaskID,
    TextColumn,
    TimeRemainingColumn,
    TransferSpeedColumn,
)
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from proxmox_utilities.exceptions import NetworkError, ProxmoxCommandError

console = Console()


def run_command(
    command: list[str],
    check: bool = True,
    capture_output: bool = True,
    timeout: int = 300,
) -> subprocess.CompletedProcess[str]:
    """
    Execute a shell command with security and error handling.

    Args:
        command: Command and arguments as list
        check: Raise exception on non-zero exit code
        capture_output: Capture stdout and stderr
        timeout: Command timeout in seconds

    Returns:
        CompletedProcess instance

    Raises:
        ProxmoxCommandError: If command fails and check=True
        subprocess.TimeoutExpired: If command times out

    Example:
        >>> result = run_command(["qm", "list"])
        >>> print(result.stdout)
    """
    try:
        console.print(f"[dim]Running: {' '.join(command)}[/dim]")
        result = subprocess.run(
            command,
            check=False,
            capture_output=capture_output,
            text=True,
            timeout=timeout,
        )

        if check and result.returncode != 0:
            raise ProxmoxCommandError(
                command=" ".join(command),
                returncode=result.returncode,
                stderr=result.stderr or "",
            )

        return result

    except subprocess.TimeoutExpired as e:
        raise ProxmoxCommandError(
            command=" ".join(command),
            returncode=-1,
            stderr=f"Command timed out after {timeout} seconds",
        ) from e


@retry(
    retry=retry_if_exception_type(NetworkError),
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
)
def download_file(url: str, destination: Path, timeout: int = 300) -> None:
    """
    Download a file with retry logic and progress indication.

    Args:
        url: URL to download from
        destination: Local file path to save to
        timeout: Download timeout in seconds

    Raises:
        NetworkError: If download fails after retries

    Example:
        >>> download_file(
        ...     "https://example.com/file.img",
        ...     Path("/tmp/file.img")
        ... )
    """
    import requests

    try:
        console.print(f"[cyan]Downloading:[/cyan] {url}")

        with requests.get(url, stream=True, timeout=timeout) as response:
            response.raise_for_status()
            total_size = int(response.headers.get("content-length", 0))

            with Progress(
                TextColumn("[bold blue]{task.description}"),
                BarColumn(),
                DownloadColumn(),
                TransferSpeedColumn(),
                TimeRemainingColumn(),
                console=console,
            ) as progress:
                task: TaskID = progress.add_task(
                    "Downloading...", total=total_size
                )

                with destination.open("wb") as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            progress.update(task, advance=len(chunk))

        console.print(
            f"[green]✓[/green] Downloaded: {destination.name} "
            f"({destination.stat().st_size:,} bytes)"
        )

    except requests.RequestException as e:
        raise NetworkError(f"Failed to download {url}: {e}") from e


def verify_checksum(
    file_path: Path, expected_checksum: str, algorithm: str = "sha256"
) -> bool:
    """
    Verify file checksum.

    Args:
        file_path: Path to file
        expected_checksum: Expected checksum value
        algorithm: Hash algorithm (sha256, sha512, md5)

    Returns:
        True if checksum matches, False otherwise

    Example:
        >>> verify_checksum(Path("file.img"), "abc123...", "sha256")
        True
    """
    hash_func = getattr(hashlib, algorithm)()

    with file_path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            hash_func.update(chunk)

    actual = hash_func.hexdigest()
    matches = actual == expected_checksum

    if matches:
        console.print(f"[green]✓[/green] Checksum verified: {algorithm}")
    else:
        console.print(
            f"[red]✗[/red] Checksum mismatch!\n"
            f"  Expected: {expected_checksum}\n"
            f"  Actual:   {actual}"
        )

    return matches


def validate_vm_id(vm_id: int, min_id: int = 100, max_id: int = 999999999) -> None:
    """
    Validate Proxmox VM ID.

    Args:
        vm_id: VM ID to validate
        min_id: Minimum valid ID
        max_id: Maximum valid ID

    Raises:
        ValueError: If VM ID is invalid

    Example:
        >>> validate_vm_id(9001, min_id=9000)
        >>> validate_vm_id(100)  # raises ValueError
    """
    if not isinstance(vm_id, int):
        raise ValueError(f"VM ID must be an integer, got {type(vm_id).__name__}")

    if vm_id < min_id or vm_id > max_id:
        raise ValueError(
            f"VM ID must be between {min_id} and {max_id}, got {vm_id}"
        )


def sanitize_vm_name(name: str) -> str:
    """
    Sanitize VM name to prevent command injection.

    Args:
        name: VM name to sanitize

    Returns:
        Sanitized name (alphanumeric, hyphens, underscores only)

    Raises:
        ValueError: If name is empty or invalid after sanitization

    Example:
        >>> sanitize_vm_name("my-vm_01")
        'my-vm_01'
        >>> sanitize_vm_name("bad;name")  # raises ValueError
    """
    import re

    if not name or not name.strip():
        raise ValueError("VM name cannot be empty")

    # Only allow alphanumeric, hyphens, and underscores
    sanitized = re.sub(r"[^a-zA-Z0-9\-_]", "", name)

    if not sanitized:
        raise ValueError(
            f"VM name '{name}' contains no valid characters "
            "(only alphanumeric, hyphens, and underscores allowed)"
        )

    if len(sanitized) > 64:
        raise ValueError(f"VM name too long (max 64 characters): {sanitized}")

    return sanitized


def format_success(message: str) -> None:
    """Print success message."""
    console.print(f"[green]✓[/green] {message}")


def format_error(message: str) -> None:
    """Print error message."""
    console.print(f"[red]✗[/red] {message}")


def format_warning(message: str) -> None:
    """Print warning message."""
    console.print(f"[yellow]⚠[/yellow] {message}")


def format_info(message: str) -> None:
    """Print info message."""
    console.print(f"[blue]ℹ[/blue] {message}")
