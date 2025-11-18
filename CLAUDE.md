# CLAUDE.md - Project Context for AI Assistants

## Project Overview

**Project Name:** proxmox-utilities
**Version:** 0.1.0
**License:** GPLv3+
**Repository:** https://github.com/zerodaysec/proxmox-utilities
**Primary Language:** Python 3.9+

### Purpose

Proxmox Utilities is a secure, production-ready Python package and CLI tool for automating Proxmox VE operations, specifically:

1. **Template Creation** - Automated Ubuntu cloud-init template creation from official cloud images
2. **VM Management** - Clone, start, stop, delete, and manage Proxmox VMs
3. **Security** - Focus on preventing command injection, input validation, and operational security

### Key Design Principles

1. **Security First** - All inputs validated, no command injection risks, no hardcoded secrets
2. **Type Safety** - Full type hints, mypy compliance, Pydantic validation
3. **Error Handling** - Comprehensive exception handling with retry logic
4. **User Experience** - Rich CLI with progress bars, colored output, helpful messages
5. **Operational Excellence** - Extensive docs, tests, logging, monitoring
6. **PyPI Package** - Properly structured for distribution on PyPI

## Architecture

### Project Structure

```
proxmox-utilities/
├── src/proxmox_utilities/        # Main package
│   ├── __init__.py              # Package exports
│   ├── cli.py                   # Click-based CLI commands
│   ├── config.py                # Pydantic configuration management
│   ├── exceptions.py            # Custom exception hierarchy
│   ├── template.py              # Ubuntu template creation
│   ├── vm.py                    # VM lifecycle management
│   └── utils.py                 # Shared utilities (commands, downloads, validation)
├── tests/                       # Pytest test suite
│   ├── conftest.py              # Test fixtures
│   ├── test_config.py           # Config tests
│   ├── test_utils.py            # Utils tests
│   ├── test_template.py         # Template tests
│   └── test_vm.py               # VM tests
├── docs/                        # MkDocs documentation
│   ├── index.md                 # Documentation homepage
│   ├── getting-started/         # Installation, quick start, config
│   ├── user-guide/              # User documentation
│   ├── security/                # Security docs
│   ├── development/             # Contributing, testing
│   └── api/                     # API reference
├── pyproject.toml               # Package metadata and tool configuration
├── mkdocs.yml                   # MkDocs configuration
├── README.md                    # GitHub README
├── CHANGELOG.md                 # Version history
├── CLAUDE.md                    # This file
└── LICENSE                      # GPLv3 license

Legacy files (being deprecated):
├── create-ubuntu-template.sh    # Shell script (replaced by Python)
└── create-vm.sh                 # Shell script (replaced by Python)
```

### Module Responsibilities

#### `config.py`
- Pydantic-based configuration with environment variable support
- Validates SSH keys, storage names, memory limits, timeouts
- Supports `.env` files and direct initialization

#### `exceptions.py`
- Exception hierarchy: `ProxmoxUtilityError` (base)
- Specific exceptions: `ValidationError`, `TemplateCreationError`, `VMCreationError`, `NetworkError`, `ProxmoxCommandError`

#### `template.py`
- `UbuntuRelease` enum (JAMMY, FOCAL, NOBLE)
- `TemplateCreator` class handles complete workflow:
  1. Download Ubuntu cloud image (with retry)
  2. Create VM with qm
  3. Import disk
  4. Configure hardware (SCSI, boot, serial console)
  5. Resize disk
  6. Configure cloud-init (DHCP, SSH keys)
  7. Convert to template

#### `vm.py`
- `VMCreator` class for VM operations:
  - Clone from template
  - Configure cloud-init
  - Start/stop VMs
  - Get status
  - Delete VMs (with purge option)

#### `utils.py`
- `run_command()` - Secure subprocess execution with timeout
- `download_file()` - Downloads with retry, progress bars
- `validate_vm_id()` - VM ID range validation
- `sanitize_vm_name()` - Prevents command injection
- `verify_checksum()` - File integrity checking
- Progress formatting helpers

#### `cli.py`
- Click-based CLI with commands:
  - `proxmox create-template` - Create Ubuntu templates
  - `proxmox create-vm` - Clone VMs from templates
  - `proxmox start/stop/status/delete` - VM management

### Technology Stack

- **Python 3.9+** - Main language
- **Click** - CLI framework
- **Rich** - Terminal UI (progress bars, colors)
- **Pydantic** - Configuration and validation
- **Requests** - HTTP downloads
- **Tenacity** - Retry logic with exponential backoff
- **Pytest** - Testing framework
- **MkDocs Material** - Documentation
- **Black** - Code formatting
- **Ruff** - Linting (includes security rules)
- **MyPy** - Type checking
- **Bandit** - Security scanning

## Development Workflow

### Setting Up Development Environment

```bash
# Clone repository
git clone https://github.com/zerodaysec/proxmox-utilities.git
cd proxmox-utilities

# Install in development mode with all dependencies
pip install -e ".[dev,docs,security]"

# Install pre-commit hooks
pre-commit install
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/proxmox_utilities --cov-report=html

# Run specific test file
pytest tests/test_template.py

# Run with specific marker
pytest -m unit
```

### Code Quality

```bash
# Format code
black src/ tests/

# Lint code
ruff check src/ tests/

# Type check
mypy src/

# Security scan
bandit -r src/
pip-audit
```

### Building Documentation

```bash
# Serve docs locally
mkdocs serve

# Build docs
mkdocs build

# Deploy to GitHub Pages
mkdocs gh-deploy
```

### Building Package

```bash
# Build wheel and sdist
python -m build

# Check package
twine check dist/*

# Upload to PyPI (maintainers only)
twine upload dist/*
```

## Security Considerations

### Vulnerabilities Fixed from Shell Scripts

1. **Syntax Errors** - Fixed missing spaces in shell commands (lines 50, 54, 56, 58, 60, 62)
2. **Incomplete Execution** - Fixed create-vm.sh only echoing commands instead of running them
3. **Hardcoded Values** - Made SSH key path, VM IDs, storage configurable
4. **No Input Validation** - Added comprehensive validation with Pydantic
5. **Command Injection** - Prevented via parameterized commands and input sanitization
6. **No Error Handling** - Added try/catch, retries, timeouts
7. **No Logging** - Added structured logging throughout

### Security Features

- ✅ Input validation (VM IDs, names, paths)
- ✅ Command injection prevention (parameterized commands)
- ✅ Input sanitization (VM name regex)
- ✅ No hardcoded secrets (environment variables)
- ✅ Retry logic with exponential backoff
- ✅ Timeout enforcement
- ✅ Checksum verification for downloads
- ✅ Type safety with mypy
- ✅ Security scanning with Bandit
- ✅ Dependency scanning with pip-audit

## Common Tasks

### Adding a New CLI Command

1. Add command function in `cli.py` with `@main.command()` decorator
2. Add corresponding method in `VMCreator` or `TemplateCreator`
3. Add tests in `tests/test_vm.py` or `tests/test_template.py`
4. Document in `docs/user-guide/cli.md`
5. Update CHANGELOG.md

### Adding a New Ubuntu Release

1. Add enum value to `UbuntuRelease` in `template.py`
2. Test template creation
3. Update documentation in `docs/user-guide/templates.md`
4. Update CHANGELOG.md

### Fixing a Security Issue

1. Create private branch (don't push publicly)
2. Implement fix
3. Add tests to prevent regression
4. Run security scans: `bandit -r src/`
5. Update security documentation
6. Follow responsible disclosure process (see docs/security/overview.md)

### Releasing a New Version

1. Update version in `pyproject.toml` and `src/proxmox_utilities/__init__.py`
2. Update CHANGELOG.md with all changes
3. Run full test suite: `pytest`
4. Run security scans
5. Build package: `python -m build`
6. Test installation: `pip install dist/proxmox_utilities-*.whl`
7. Tag release: `git tag v0.1.0`
8. Push to GitHub: `git push && git push --tags`
9. Upload to PyPI: `twine upload dist/*`
10. Deploy docs: `mkdocs gh-deploy`

## Testing Strategy

### Test Categories

- **Unit Tests** (`@pytest.mark.unit`) - Test individual functions
- **Integration Tests** (`@pytest.mark.integration`) - Require Proxmox connection
- **Slow Tests** (`@pytest.mark.slow`) - Long-running tests

### Mocking Strategy

- Mock `subprocess.run` for command execution
- Mock `requests.get` for downloads
- Use `tmp_path` fixture for file operations
- Use `monkeypatch` for environment variables

### Coverage Goals

- Overall: >80%
- Critical modules (utils, template, vm): >90%
- Exception paths: 100%

## Configuration

### Environment Variables

```bash
# Storage configuration
PROXMOX_DATA_STORE="local-lvm"
PROXMOX_VM_BRIDGE="vmbr0"

# SSH configuration
PROXMOX_SSH_KEY_PATH="~/.ssh/id_ed25519.pub"

# Template defaults
PROXMOX_TEMPLATE_MEMORY_MB=2048
PROXMOX_TEMPLATE_DISK_INCREASE_GB=30

# Network configuration
PROXMOX_UBUNTU_IMAGE_BASE_URL="https://cloud-images.ubuntu.com"
PROXMOX_DOWNLOAD_TIMEOUT_SECONDS=300
PROXMOX_MAX_RETRIES=3
```

### .env File Support

Place `.env` file in project root or working directory:

```env
PROXMOX_SSH_KEY_PATH=/home/user/.ssh/id_rsa.pub
PROXMOX_DATA_STORE=local-lvm
PROXMOX_VM_BRIDGE=vmbr0
```

## Dependencies

### Core Dependencies

- `click>=8.1.0` - CLI framework
- `rich>=13.0.0` - Terminal UI
- `pydantic>=2.0.0` - Validation
- `pydantic-settings>=2.0.0` - Settings management
- `requests>=2.31.0` - HTTP client
- `tenacity>=8.2.0` - Retry logic

### Development Dependencies

- `pytest>=7.4.0` - Testing framework
- `pytest-cov>=4.1.0` - Coverage reporting
- `pytest-mock>=3.12.0` - Mocking utilities
- `black>=23.0.0` - Code formatter
- `ruff>=0.1.0` - Linter
- `mypy>=1.7.0` - Type checker

### Documentation Dependencies

- `mkdocs>=1.5.0` - Documentation generator
- `mkdocs-material>=9.4.0` - Material theme
- `mkdocstrings[python]>=0.24.0` - API docs from docstrings

### Security Dependencies

- `bandit[toml]>=1.7.0` - Security linter
- `safety>=2.3.0` - Dependency vulnerability checker
- `pip-audit>=2.6.0` - PyPI vulnerability checker

## Troubleshooting

### Common Issues

**Issue:** `qm` command not found
**Solution:** Must run on Proxmox host with root privileges

**Issue:** Permission denied
**Solution:** Use `sudo` or run as root on Proxmox host

**Issue:** SSH key not found
**Solution:** Verify `PROXMOX_SSH_KEY_PATH` points to existing `.pub` file

**Issue:** Network timeout during download
**Solution:** Increase `PROXMOX_DOWNLOAD_TIMEOUT_SECONDS`

**Issue:** Import errors
**Solution:** Install in editable mode: `pip install -e .`

## Contributing

See [CONTRIBUTING.md](development/contributing.md) for detailed contribution guidelines.

### Quick Contribution Checklist

- [ ] Code follows Black formatting
- [ ] Code passes Ruff linting
- [ ] Code passes MyPy type checking
- [ ] Tests added for new functionality
- [ ] Tests pass (`pytest`)
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] Security considerations addressed

## Contact

- **Maintainer:** ZeroDay Security
- **Email:** jon@zer0day.net
- **Repository:** https://github.com/zerodaysec/proxmox-utilities
- **Issues:** https://github.com/zerodaysec/proxmox-utilities/issues
- **Security:** security@zer0day.net (for vulnerabilities)

## License

GNU General Public License v3.0 or later (GPLv3+)

See [LICENSE](../LICENSE) for full text.

---

**Last Updated:** 2024-11-18
**Claude Version:** This file is maintained for AI assistants (like Claude) to understand project context.
