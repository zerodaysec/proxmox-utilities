"""
Tests for utility functions.
"""

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from proxmox_utilities.exceptions import NetworkError, ProxmoxCommandError
from proxmox_utilities.utils import (
    download_file,
    run_command,
    sanitize_vm_name,
    validate_vm_id,
    verify_checksum,
)


class TestRunCommand:
    """Tests for run_command function."""

    def test_successful_command(self, mock_subprocess: MagicMock) -> None:
        """Test successful command execution."""
        mock_subprocess.return_value.returncode = 0
        mock_subprocess.return_value.stdout = "success"

        result = run_command(["echo", "test"])

        assert result.returncode == 0
        assert result.stdout == "success"
        mock_subprocess.assert_called_once()

    def test_failed_command_with_check(self, mock_subprocess: MagicMock) -> None:
        """Test failed command with check=True."""
        mock_subprocess.return_value.returncode = 1
        mock_subprocess.return_value.stderr = "error"

        with pytest.raises(ProxmoxCommandError, match="failed with exit code 1"):
            run_command(["false"], check=True)

    def test_failed_command_without_check(self, mock_subprocess: MagicMock) -> None:
        """Test failed command with check=False."""
        mock_subprocess.return_value.returncode = 1

        result = run_command(["false"], check=False)
        assert result.returncode == 1


class TestValidateVMID:
    """Tests for validate_vm_id function."""

    def test_valid_vm_id(self) -> None:
        """Test valid VM IDs."""
        validate_vm_id(100)
        validate_vm_id(9001)
        validate_vm_id(999999)

    def test_vm_id_below_minimum(self) -> None:
        """Test VM ID below minimum."""
        with pytest.raises(ValueError, match="must be between"):
            validate_vm_id(50, min_id=100)

    def test_vm_id_above_maximum(self) -> None:
        """Test VM ID above maximum."""
        with pytest.raises(ValueError, match="must be between"):
            validate_vm_id(10000, min_id=100, max_id=9999)

    def test_non_integer_vm_id(self) -> None:
        """Test non-integer VM ID."""
        with pytest.raises(ValueError, match="must be an integer"):
            validate_vm_id("100")  # type: ignore


class TestSanitizeVMName:
    """Tests for sanitize_vm_name function."""

    def test_valid_vm_names(self) -> None:
        """Test valid VM names."""
        assert sanitize_vm_name("my-vm") == "my-vm"
        assert sanitize_vm_name("test_vm_01") == "test_vm_01"
        assert sanitize_vm_name("VM-123") == "VM-123"

    def test_empty_vm_name(self) -> None:
        """Test empty VM name."""
        with pytest.raises(ValueError, match="cannot be empty"):
            sanitize_vm_name("")

    def test_invalid_characters(self) -> None:
        """Test VM name with invalid characters."""
        with pytest.raises(ValueError, match="contains no valid characters"):
            sanitize_vm_name("!!!@@@###")

    def test_sanitization(self) -> None:
        """Test that invalid characters are removed."""
        # This should raise an error for having special chars only after sanitization
        with pytest.raises(ValueError):
            sanitize_vm_name("my;vm")  # semicolon would be security risk

    def test_name_too_long(self) -> None:
        """Test VM name that's too long."""
        long_name = "a" * 100
        with pytest.raises(ValueError, match="too long"):
            sanitize_vm_name(long_name)


class TestDownloadFile:
    """Tests for download_file function."""

    def test_successful_download(
        self, mock_requests: MagicMock, tmp_path: Path
    ) -> None:
        """Test successful file download."""
        dest = tmp_path / "test.img"

        download_file("https://example.com/file.img", dest)

        assert dest.exists()
        mock_requests.assert_called_once()

    def test_failed_download(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        """Test failed file download."""
        import requests

        def mock_get(*args, **kwargs):  # type: ignore
            raise requests.RequestException("Connection failed")

        monkeypatch.setattr("requests.get", mock_get)

        dest = tmp_path / "test.img"

        with pytest.raises(NetworkError, match="Failed to download"):
            download_file("https://example.com/file.img", dest, timeout=1)


class TestVerifyChecksum:
    """Tests for verify_checksum function."""

    def test_matching_checksum(self, tmp_path: Path) -> None:
        """Test checksum verification with matching checksum."""
        import hashlib

        test_file = tmp_path / "test.txt"
        content = b"test content"
        test_file.write_bytes(content)

        expected = hashlib.sha256(content).hexdigest()

        assert verify_checksum(test_file, expected, "sha256") is True

    def test_mismatched_checksum(self, tmp_path: Path) -> None:
        """Test checksum verification with mismatched checksum."""
        test_file = tmp_path / "test.txt"
        test_file.write_bytes(b"test content")

        assert verify_checksum(test_file, "wrong_checksum", "sha256") is False
