# Installation

## Requirements

- Python 3.9 or later
- Proxmox VE 7.0 or later
- SSH access to Proxmox host
- Root or sudo privileges on Proxmox host

## Installation Methods

### From PyPI (Recommended)

Install the latest stable release from PyPI:

```bash
pip install proxmox-utilities
```

### From Source

Install from the GitHub repository:

```bash
git clone https://github.com/zerodaysec/proxmox-utilities.git
cd proxmox-utilities
pip install -e .
```

### With Development Dependencies

For development and testing:

```bash
pip install proxmox-utilities[dev]
```

### With Documentation Tools

To build documentation locally:

```bash
pip install proxmox-utilities[docs]
```

### With Security Tools

To include security scanning tools:

```bash
pip install proxmox-utilities[security]
```

### All Optional Dependencies

```bash
pip install proxmox-utilities[dev,docs,security]
```

## Verification

Verify the installation:

```bash
proxmox --version
```

You should see output like:

```
proxmox-utilities, version 0.1.0
```

## Shell Completion

### Bash

```bash
_PROXMOX_COMPLETE=bash_source proxmox > ~/.proxmox-complete.bash
echo ". ~/.proxmox-complete.bash" >> ~/.bashrc
```

### Zsh

```bash
_PROXMOX_COMPLETE=zsh_source proxmox > ~/.proxmox-complete.zsh
echo ". ~/.proxmox-complete.zsh" >> ~/.zshrc
```

### Fish

```bash
_PROXMOX_COMPLETE=fish_source proxmox > ~/.config/fish/completions/proxmox.fish
```

## Configuration

### SSH Key Setup

Generate an SSH key if you don't have one:

```bash
ssh-keygen -t ed25519 -C "proxmox-vms"
```

### Environment Variables

Create a `.env` file or set environment variables:

```bash
export PROXMOX_SSH_KEY_PATH="$HOME/.ssh/id_ed25519.pub"
export PROXMOX_DATA_STORE="local-lvm"
export PROXMOX_VM_BRIDGE="vmbr0"
```

See [Configuration](configuration.md) for all available options.

## Troubleshooting

### Permission Denied

If you get permission errors, ensure you're running on the Proxmox host with root privileges:

```bash
sudo -i
proxmox create-template jammy 9001
```

### Command Not Found

If the `proxmox` command is not found after installation, ensure your Python scripts directory is in your PATH:

```bash
# For user installations
export PATH="$HOME/.local/bin:$PATH"

# For system installations (with sudo)
export PATH="/usr/local/bin:$PATH"
```

### Network Errors

If you encounter network errors during image downloads:

1. Check internet connectivity
2. Verify firewall rules
3. Check proxy settings if behind a corporate firewall
4. Increase timeout: `export PROXMOX_DOWNLOAD_TIMEOUT_SECONDS=600`

## Next Steps

- [Quick Start Guide](quick-start.md) - Create your first template
- [Configuration](configuration.md) - Customize settings
- [CLI Reference](../user-guide/cli.md) - Explore all commands
