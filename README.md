# ProxBox

![CI/CD](https://github.com/zerodaysec/proxmox-utilities/actions/workflows/python-ci.yml/badge.svg)
[![PyPI version](https://badge.fury.io/py/proxbox.svg)](https://pypi.org/project/proxbox/)
[![Python versions](https://img.shields.io/pypi/pyversions/proxbox.svg)](https://pypi.org/project/proxbox/)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

**ProxBox - Your Proxmox toolbox for secure VM automation**

ProxBox is a modern Python package and CLI tool for automating Proxmox VE operations with a focus on security, reliability, and operational excellence.

## ✨ Features

- 🚀 **Template Creation** - Automated Ubuntu cloud-init template creation from official images
- 🖥️ **VM Management** - Clone, start, stop, and manage VMs with ease
- 🔒 **Security First** - Input validation, sanitization, and command injection prevention
- 📊 **Rich UI** - Progress bars, colored output, and helpful error messages
- 🔄 **Retry Logic** - Automatic retry with exponential backoff for network operations
- ✅ **Type Safe** - Full type hints and mypy compliance
- 🧪 **Well Tested** - Comprehensive test suite with >80% coverage
- 📚 **Documented** - Extensive documentation with examples

## 📦 Installation

```bash
pip install proxbox
```

## 🚀 Quick Start

### Create an Ubuntu Template

```bash
# Create Ubuntu 22.04 LTS template
proxbox create-template jammy 9001 --ssh-key ~/.ssh/id_rsa.pub

# Create template with custom settings
proxbox create-template noble 9002 \
    --name my-ubuntu-template \
    --memory 4096 \
    --disk-increase 50
```

### Clone and Manage VMs

```bash
# Clone a VM from template and start it
proxbox create-vm 9001 190 my-ubuntu-vm --start

# Check VM status
proxbox status 190

# Stop a VM
proxbox stop 190

# Delete a VM (with confirmation)
proxbox delete 190
```

## 📖 Documentation

Full documentation is available at: **https://zerodaysec.github.io/proxmox-utilities**

- [Installation Guide](https://zerodaysec.github.io/proxmox-utilities/getting-started/installation/)
- [Quick Start Tutorial](https://zerodaysec.github.io/proxmox-utilities/getting-started/quick-start/)
- [CLI Reference](https://zerodaysec.github.io/proxmox-utilities/user-guide/cli/)
- [Security Best Practices](https://zerodaysec.github.io/proxmox-utilities/security/best-practices/)
- [API Documentation](https://zerodaysec.github.io/proxmox-utilities/api/template/)

## 🔧 Configuration

Configure via environment variables or `.env` file:

```bash
# SSH key for cloud-init
export PROXMOX_SSH_KEY_PATH="$HOME/.ssh/id_ed25519.pub"

# Storage configuration
export PROXMOX_DATA_STORE="local-lvm"
export PROXMOX_VM_BRIDGE="vmbr0"

# Template defaults
export PROXMOX_TEMPLATE_MEMORY_MB=2048
export PROXMOX_TEMPLATE_DISK_INCREASE_GB=30
```

See [Configuration Guide](https://zerodaysec.github.io/proxmox-utilities/getting-started/configuration/) for all options.

## 🔒 Security

Security is a top priority. This project includes:

- ✅ Input validation and sanitization
- ✅ Command injection prevention
- ✅ No hardcoded secrets
- ✅ Automated security scanning (Bandit, pip-audit)
- ✅ Type safety with mypy
- ✅ Comprehensive test coverage

See [Security Documentation](https://zerodaysec.github.io/proxmox-utilities/security/overview/) for details.

## 🆚 Comparison with Shell Scripts

| Feature | Shell Scripts (v0.0.1) | Python Package (v0.1.0+) |
|---------|----------------------|--------------------------|
| Security | ⚠️ Basic | ✅ Comprehensive |
| Error Handling | ❌ Minimal | ✅ Robust |
| Testing | ❌ None | ✅ >80% coverage |
| Type Safety | ❌ No | ✅ Full type hints |
| Progress Tracking | ❌ No | ✅ Rich UI |
| Retry Logic | ❌ No | ✅ Automatic |
| Documentation | ⚠️ Comments only | ✅ Full docs site |
| Package Management | ❌ Manual download | ✅ pip install |

## 🛠️ Development

### Setup Development Environment

```bash
git clone https://github.com/zerodaysec/proxmox-utilities.git
cd proxmox-utilities
pip install -e ".[dev,docs,security]"
pre-commit install
```

### Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/proxbox --cov-report=html

# Run specific tests
pytest tests/test_template.py -v
```

### Code Quality

```bash
# Format code
black src/ tests/

# Lint
ruff check src/ tests/

# Type check
mypy src/

# Security scan
bandit -r src/
```

### Build Documentation

```bash
# Serve locally
mkdocs serve

# Build
mkdocs build
```

## 📝 Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history and migration guides.

## 🤝 Contributing

Contributions are welcome! Please see [Contributing Guide](https://zerodaysec.github.io/proxmox-utilities/development/contributing/) for details.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`pytest`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## 📜 License

This project is licensed under the GNU General Public License v3.0 or later (GPLv3+).

See [LICENSE](LICENSE) for the full license text.

## 👨‍💻 Author

**ZeroDay Security**
- Email: jon@zer0day.net
- GitHub: [@zerodaysec](https://github.com/zerodaysec)

## 🙏 Acknowledgments

- Proxmox VE team for excellent virtualization platform
- Ubuntu for cloud images
- Python community for amazing tools and libraries

## 📞 Support

- 📖 [Documentation](https://zerodaysec.github.io/proxmox-utilities)
- 🐛 [Issue Tracker](https://github.com/zerodaysec/proxmox-utilities/issues)
- 💬 [Discussions](https://github.com/zerodaysec/proxmox-utilities/discussions)
- 🔒 [Security: security@zer0day.net](mailto:security@zer0day.net)

---

**Made with ❤️ by ZeroDay Security**
