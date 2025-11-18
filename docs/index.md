# ProxBox

**Secure, production-ready utilities for Proxmox VM automation**

[![CI/CD Action](https://github.com/zerodaysec/proxbox/actions/workflows/cicd.yml/badge.svg)](https://github.com/zerodaysec/proxbox/actions)
[![PyPI version](https://badge.fury.io/py/proxbox.svg)](https://pypi.org/project/proxbox/)
[![Python versions](https://img.shields.io/pypi/pyversions/proxbox.svg)](https://pypi.org/project/proxbox/)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

## Overview

ProxBox is a Python package and CLI tool for automating common Proxmox VE tasks with a focus on security, reliability, and operational excellence.

### Features

- 🚀 **Template Creation** - Automated Ubuntu cloud-init template creation
- 🖥️ **VM Management** - Clone, start, stop, and manage VMs
- 🔒 **Security First** - Input validation, sanitization, and command injection prevention
- 📊 **Progress Tracking** - Rich terminal UI with progress bars and colored output
- 🔄 **Retry Logic** - Automatic retry with exponential backoff for network operations
- ✅ **Type Safe** - Full type hints and mypy compliance
- 🧪 **Well Tested** - Comprehensive test suite with pytest
- 📚 **Documented** - Extensive documentation and examples

## Quick Start

### Installation

```bash
pip install proxbox
```

### Create a Template

```bash
# Create an Ubuntu 22.04 LTS template
proxbox create-template jammy 9001 \\
    --ssh-key ~/.ssh/id_rsa.pub \\
    --memory 4096 \\
    --disk-increase 50
```

### Clone a VM

```bash
# Clone a VM from the template and start it
proxbox create-vm 9001 190 my-ubuntu-vm --start
```

### Manage VMs

```bash
# Check VM status
proxbox status 190

# Stop a VM
proxbox stop 190

# Delete a VM
proxbox delete 190 --yes
```

## Why ProxBox?

### Security

- **Command Injection Prevention** - All inputs are validated and sanitized
- **Type Safety** - Full type hints prevent common programming errors
- **Input Validation** - Comprehensive validation with Pydantic
- **No Hardcoded Secrets** - Configuration via environment variables
- **Security Scanning** - Automated scanning with Bandit and pip-audit

### Reliability

- **Retry Logic** - Network operations retry with exponential backoff
- **Error Handling** - Comprehensive error handling and recovery
- **Progress Tracking** - Visual feedback for long-running operations
- **Timeouts** - Configurable timeouts prevent hanging operations

### Operational Excellence

- **Comprehensive Docs** - Full documentation with examples
- **CLI & Library** - Use as CLI tool or import as Python library
- **Logging** - Detailed logging for troubleshooting
- **Testing** - High test coverage ensures reliability

## Comparison with Shell Scripts

| Feature | Shell Scripts | ProxBox |
|---------|---------------|-------------------|
| Security | ⚠️ Basic | ✅ Comprehensive |
| Error Handling | ❌ Minimal | ✅ Robust |
| Testing | ❌ None | ✅ Comprehensive |
| Type Safety | ❌ No | ✅ Full |
| Progress Tracking | ❌ No | ✅ Rich UI |
| Retry Logic | ❌ No | ✅ Automatic |
| Documentation | ⚠️ Comments | ✅ Full docs |
| Cross-platform | ⚠️ Linux only | ✅ Python 3.9+ |

## Architecture

```
proxbox/
├── src/proxbox/
│   ├── __init__.py      # Package initialization
│   ├── cli.py           # CLI commands
│   ├── config.py        # Configuration management
│   ├── exceptions.py    # Custom exceptions
│   ├── template.py      # Template creation
│   ├── vm.py            # VM management
│   └── utils.py         # Utility functions
├── tests/               # Comprehensive test suite
├── docs/                # Documentation
└── pyproject.toml       # Package configuration
```

## Next Steps

- [Installation Guide](getting-started/installation.md) - Detailed installation instructions
- [Quick Start](getting-started/quick-start.md) - Step-by-step tutorial
- [Configuration](getting-started/configuration.md) - Configuration options
- [CLI Reference](user-guide/cli.md) - Complete CLI documentation
- [Security Best Practices](security/best-practices.md) - Security guidelines

## License

This project is licensed under the GNU General Public License v3.0 or later (GPLv3+).

## Support

- 📖 [Documentation](https://zerodaysec.github.io/proxbox)
- 🐛 [Issue Tracker](https://github.com/zerodaysec/proxbox/issues)
- 💬 [Discussions](https://github.com/zerodaysec/proxbox/discussions)
