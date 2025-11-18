# Security Overview

ProxBox is designed with security as a top priority. This document outlines the security measures implemented in the project.

## Security Features

### 1. Input Validation

All user inputs are validated before use:

- **VM IDs** - Range validation (100-999999999)
- **VM Names** - Alphanumeric, hyphens, underscores only (max 64 chars)
- **Release Names** - Enum-based validation (only supported releases)
- **File Paths** - Existence and type checking
- **Configuration Values** - Pydantic validation with constraints

### 2. Command Injection Prevention

All shell commands use parameterized execution:

```python
# ✅ SECURE: Parameterized
run_command(["qm", "create", str(vm_id), "--name", vm_name])

# ❌ INSECURE: String concatenation (NOT USED)
os.system(f"qm create {vm_id} --name {vm_name}")
```

### 3. Input Sanitization

VM names are sanitized to prevent injection:

```python
def sanitize_vm_name(name: str) -> str:
    """Only allow alphanumeric, hyphens, and underscores."""
    return re.sub(r"[^a-zA-Z0-9\-_]", "", name)
```

### 4. Type Safety

Full type hints with mypy enforcement:

```python
def validate_vm_id(vm_id: int, min_id: int = 100) -> None:
    if not isinstance(vm_id, int):
        raise ValueError(f"VM ID must be an integer")
```

### 5. No Hardcoded Secrets

All sensitive data via environment variables or config files:

```bash
# SSH keys
export PROXMOX_SSH_KEY_PATH="$HOME/.ssh/id_ed25519.pub"

# Never hardcoded in source code
```

### 6. Secure Defaults

- Network timeouts (300s default)
- Retry limits (3 attempts)
- Memory limits (2048MB default)
- Disk size limits (max 1000GB increase)

### 7. Error Handling

Comprehensive error handling prevents information leakage:

```python
try:
    run_command(cmd)
except ProxmoxCommandError as e:
    # Log detailed error for admin
    logger.error(f"Command failed: {e}")
    # Show safe error to user
    console.print("[red]Operation failed. Check logs.[/red]")
```

## Security Scanning

### Automated Scanning

The project includes automated security scanning:

- **Bandit** - Python code security issues
- **pip-audit** - Dependency vulnerabilities
- **Safety** - Known security vulnerabilities
- **Ruff** - Security-focused linting rules

### Running Security Scans

```bash
# Install security tools
pip install proxbox[security]

# Run Bandit
bandit -r src/

# Check dependencies
pip-audit

# Run safety
safety check
```

## Vulnerability Reporting

### Disclosure Policy

If you discover a security vulnerability:

1. **DO NOT** open a public issue
2. Email: security@zer0day.net
3. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

### Response Timeline

- **24 hours** - Initial acknowledgment
- **7 days** - Initial assessment and triage
- **30 days** - Fix developed and tested
- **90 days** - Public disclosure (coordinated)

## Security Best Practices

See [Best Practices](best-practices.md) for detailed security recommendations.

## Threat Model

See [Threat Model](threat-model.md) for detailed threat analysis.

## Security Updates

Security updates are released as soon as possible:

- **Critical** - Within 24-48 hours
- **High** - Within 1 week
- **Medium** - Next regular release
- **Low** - Next major version

Subscribe to [GitHub Security Advisories](https://github.com/zerodaysec/proxbox/security/advisories) for notifications.

## Compliance

### OWASP Top 10

This project addresses OWASP Top 10 vulnerabilities:

| Vulnerability | Mitigation |
|---------------|------------|
| A01: Broken Access Control | VM ID validation, permission checks |
| A02: Cryptographic Failures | No crypto operations (relies on SSH) |
| A03: Injection | Parameterized commands, input sanitization |
| A04: Insecure Design | Security-first architecture |
| A05: Security Misconfiguration | Secure defaults, configuration validation |
| A06: Vulnerable Components | Automated dependency scanning |
| A07: Authentication Failures | SSH key-based authentication |
| A08: Data Integrity Failures | Checksum verification for downloads |
| A09: Logging Failures | Comprehensive audit logging |
| A10: SSRF | URL validation for image downloads |

## Security Certifications

No formal security certifications at this time. Contributions welcome for security audits.
