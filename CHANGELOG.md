# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Complete PyPI package restructure with modern Python packaging (PEP 517/518)
- Python package structure with src layout (`src/proxmox_utilities/`)
- Comprehensive CLI tool with Click framework
- Rich terminal UI with progress bars and colored output
- Configuration management with Pydantic and environment variable support
- Full type hints and mypy compliance
- Comprehensive test suite with pytest (>80% coverage)
- MkDocs documentation site with Material theme
- Security scanning with Bandit and pip-audit
- Retry logic with exponential backoff for network operations
- Input validation and sanitization (prevents command injection)
- Checksum verification for downloaded images
- CLAUDE.md for AI assistant context

### Changed
- **BREAKING:** Replaced shell scripts with Python modules
- **BREAKING:** New CLI interface (`proxmox` command vs shell scripts)
- Improved error handling and recovery
- Enhanced security with parameterized command execution
- Configuration via environment variables instead of hardcoded values

### Fixed
- **Security:** Fixed shell script syntax errors that would cause failures
  - Line 50: Missing space after `"${TEMPLATE_ID}` in create-ubuntu-template.sh
  - Lines 54, 56, 58, 60, 62: Missing spaces between variables and flags
  - Line 58: Missing space between `"$TEMPLATE_ID"` and `scsi0`
- **Security:** Fixed create-vm.sh only echoing commands instead of executing them
- **Security:** Removed hardcoded VM ID (190) in create-vm.sh
- **Security:** Made SSH key path configurable (was hardcoded to ~/id_rsa.pub)
- **Security:** Added input validation to prevent command injection
- **Security:** Removed all hardcoded paths and credentials
- **Reliability:** Added network timeout handling for image downloads
- **Reliability:** Added retry logic for transient failures
- **Reliability:** Added proper error messages and exit codes

### Deprecated
- Legacy shell scripts (`create-ubuntu-template.sh`, `create-vm.sh`) - use Python CLI instead

### Security
- Added comprehensive input validation with Pydantic
- Implemented command injection prevention via parameterized commands
- Added input sanitization for VM names (alphanumeric, hyphens, underscores only)
- Removed all hardcoded secrets and sensitive values
- Added security scanning with Bandit
- Added dependency vulnerability scanning with pip-audit and Safety
- Implemented secure defaults for all operations
- Added timeout enforcement to prevent hanging operations
- Added checksum verification for downloaded images

## [0.0.1] - 2024-11-18 (Pre-release)

### Added
- Initial shell script implementation
- `create-ubuntu-template.sh` - Ubuntu cloud-init template creation
- `create-vm.sh` - VM cloning from templates
- Basic validation for Ubuntu releases (jammy, focal, bionic)
- Basic VM ID validation (must be > 9000 for templates)
- GPLv3 license
- GitHub Actions CI/CD workflow
- Dependabot configuration

### Known Issues (Pre-release)
- Shell scripts contain syntax errors
- Commands only echoed, not executed in create-vm.sh
- No input validation for security
- No error handling or retry logic
- Hardcoded values (VM IDs, paths, credentials)
- No testing or documentation
- No package structure (not installable)

---

## Version History Summary

| Version | Date | Type | Description |
|---------|------|------|-------------|
| Unreleased | 2024-11-18 | Major | Complete Python rewrite, PyPI package, security fixes |
| 0.0.1 | 2024-11-18 | Pre-release | Initial shell script implementation |

## Migration Guide

### From Shell Scripts (0.0.1) to Python Package (0.1.0)

#### Installation

**Old:**
```bash
# Download and run shell scripts directly
./create-ubuntu-template.sh jammy 9001
./create-vm.sh 9001 190 my-vm
```

**New:**
```bash
# Install from PyPI
pip install proxmox-utilities

# Use CLI
proxmox create-template jammy 9001
proxmox create-vm 9001 190 my-vm
```

#### Configuration

**Old:**
```bash
# Edit variables in shell script
DATA_STORE="local-lvm"
VM_BRIDGE="vmbr0"
```

**New:**
```bash
# Use environment variables
export PROXMOX_DATA_STORE="local-lvm"
export PROXMOX_VM_BRIDGE="vmbr0"
export PROXMOX_SSH_KEY_PATH="~/.ssh/id_ed25519.pub"

# Or use .env file
echo 'PROXMOX_DATA_STORE="local-lvm"' > .env
```

#### Template Creation

**Old:**
```bash
./create-ubuntu-template.sh jammy 9001
```

**New:**
```bash
# Basic usage
proxmox create-template jammy 9001

# With options
proxmox create-template jammy 9001 \\
    --name my-template \\
    --memory 4096 \\
    --disk-increase 50 \\
    --ssh-key ~/.ssh/id_ed25519.pub
```

#### VM Creation

**Old:**
```bash
./create-vm.sh 9001 my-vm
# Note: Old script had hardcoded VM ID 190
```

**New:**
```bash
# Create VM
proxmox create-vm 9001 190 my-vm

# Create and start
proxmox create-vm 9001 191 web-server --start

# Additional management
proxmox status 190
proxmox stop 190
proxmox delete 190 --yes
```

#### Error Handling

**Old:**
- No retry logic
- Scripts fail silently
- No error messages

**New:**
- Automatic retry with exponential backoff
- Colored error messages
- Detailed error reporting
- Exit codes for scripting

## Upgrade Instructions

### From 0.0.1 to 0.1.0

1. **Install Python package:**
   ```bash
   pip install proxmox-utilities
   ```

2. **Set environment variables:**
   ```bash
   export PROXMOX_SSH_KEY_PATH="$HOME/.ssh/id_rsa.pub"
   export PROXMOX_DATA_STORE="local-lvm"
   export PROXMOX_VM_BRIDGE="vmbr0"
   ```

3. **Update scripts:**
   - Replace `./create-ubuntu-template.sh` with `proxmox create-template`
   - Replace `./create-vm.sh` with `proxmox create-vm`
   - Add explicit VM IDs (no longer hardcoded)

4. **Test:**
   ```bash
   proxmox --version
   proxmox --help
   ```

## Contributing

See [CONTRIBUTING.md](docs/development/contributing.md) for details on contributing to this project.

## Support

- 📖 [Documentation](https://zerodaysec.github.io/proxmox-utilities)
- 🐛 [Issue Tracker](https://github.com/zerodaysec/proxmox-utilities/issues)
- 💬 [Discussions](https://github.com/zerodaysec/proxmox-utilities/discussions)

[Unreleased]: https://github.com/zerodaysec/proxmox-utilities/compare/v0.0.1...HEAD
[0.0.1]: https://github.com/zerodaysec/proxmox-utilities/releases/tag/v0.0.1
