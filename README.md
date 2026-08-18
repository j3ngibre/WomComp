# WomComp

**WomComp** is a Linux compliance and security configuration scanner designed for **GRC, SysAdmin, DevSecOps and Blue Team** environments.

It allows you to define security and compliance controls in **YAML** and automatically evaluate a Linux system against those controls.

The goal is to make compliance checks:

* **Simple** — define controls in YAML.
* **Auditable** — every test produces evidence.
* **Repeatable** — run the same controls across multiple systems.
* **Framework-oriented** — map controls to CIS, ISO 27001 and NIST.
* **Extensible** — add new checks without modifying the scanner core.

---

## Features

* YAML-based compliance test definitions.
* File existence checks.
* File content checks.
* Regular expression checks.
* Unix permission checks.
* Command-based checks.
* Evidence collection for every test.
* PASS / FAIL results.
* Compliance score calculation.
* Verbose and silent execution modes.
* CIS / ISO 27001 / NIST framework mapping.
* Basic and complex predefined configurations.
* Suitable for Linux hardening and security auditing.

---

## Project Structure

```text
WomComp/
│
├── launcher.py          # Main CLI entry point
├── conf_tester.py       # Compliance test engine
│
├── bconf.yaml           # Basic compliance configuration
├── cconf.yaml           # Complex compliance configuration
│
├── README.md
└── LICENSE
```

## Installation

Clone the repository:

```bash
git clone https://github.com/J3ngibre/WomComp.git
cd WomComp
```

Install dependencies:


```bash
python3 -m pip install pyyaml
```

---

# Usage

The main entry point is:

```bash
python3 launcher.py
```

By default, WomComp uses:

```text
bconf.yaml
```

### Basic scan

```bash
python3 launcher.py
```

### Basic configuration

```bash
python3 launcher.py -b
```

### Complex configuration

```bash
python3 launcher.py -c
```

### Custom YAML configuration

```bash
python3 launcher.py -f myconfig.yaml
```

### Verbose mode

Verbose mode displays detailed evidence for each test:

```bash
python3 launcher.py -b -v
```

### Silent mode

Silent mode displays only the final compliance score:

```bash
python3 launcher.py -b -s
```

Example:

```text
Compliance Score: 42/50 passed (84.0%)
```

---

# Command-line Options

| Option | Long option | Description                         |
| ------ | ----------- | ----------------------------------- |
| `-f`   | `--file`    | Use a custom YAML configuration     |
| `-b`   | `--basic`   | Use `bconf.yaml`                    |
| `-c`   | `--complex` | Use `cconf.yaml`                    |
| `-v`   | `--verbose` | Display detailed test evidence      |
| `-s`   | `--silent`  | Display only the compliance summary |
| `-h`   | `--help`    | Show help                           |

---

# How It Works

WomComp follows a simple workflow:

```text
                ┌─────────────────┐
                │   YAML Config   │
                └────────┬────────┘
                         │
                         ▼
                ┌─────────────────┐
                │    fileLoad()   │
                └────────┬────────┘
                         │
                         ▼
                ┌─────────────────┐
                │   Test Engine   │
                └────────┬────────┘
                         │
            ┌────────────┼────────────┐
            ▼            ▼            ▼
       File Check    Regex Check  Command Check
            │            │            │
            └────────────┼────────────┘
                         ▼
                ┌─────────────────┐
                │ PASS / FAIL +    │
                │ Evidence         │
                └────────┬────────┘
                         │
                         ▼
                ┌─────────────────┐
                │ Compliance Score │
                └─────────────────┘
```

Each YAML test defines:

1. What is being checked.
2. Which type of check should be performed.
3. What result is expected.
4. Which compliance frameworks are relevant.
5. The severity of a failure.
6. The evidence used to determine the result.

---

# YAML Configuration

A test is defined inside the `tests` section.

Example:

```yaml
tests:

  - id: "WOM-001"
    title: "Check SSH configuration"
    category: "SSH"
    severity: "HIGH"

    frameworks:
      CIS: "5.2.1"
      ISO27001: "A.8.20"
      NIST: "SC-8"

    check:
      type: "file_contains"
      file: "/etc/ssh/sshd_config"
      expected: "PermitRootLogin no"
```

---

# Supported Check Types

## File Exists

Checks whether a file exists.

```yaml
check:
  type: "file_exists"
  file: "/etc/ssh/sshd_config"
```

The test passes when the file exists.

---

## File Contains

Checks whether a specific string exists in a file.

```yaml
check:
  type: "file_contains"
  file: "/etc/ssh/sshd_config"
  expected: "PermitRootLogin no"
```

Commented lines beginning with `#` are ignored.

---

## Regex

Regular expressions can be used for more flexible checks.

```yaml
check:
  type: "regex"
  file: "/etc/login.defs"
  expected: '^PASS_MAX_DAYS\s+[0-9]+$'
```

### YAML regex warning

When using backslashes in regular expressions, prefer **single quotes**:

```yaml
expected: '^\d+$'
```

instead of:

```yaml
expected: "^\d+$"
```

The second form can cause YAML parsing errors because `\d` is not a valid YAML escape sequence inside double quotes.

---

## File Permissions

Checks Unix file permissions.

```yaml
check:
  type: "permission"
  file: "/etc/shadow"
  expected: "640"
```

The expected value represents the standard Unix permission bits.

---

## Command

WomComp can execute a system command and check its output.

Example:

```yaml
check:
  type: "command"
  command: "sudo awk -F: '($2 == \"\") {print}' /etc/shadow"
  expected: ""
```

For complex commands, YAML block syntax can make the configuration easier to read:

```yaml
check:
  type: "command"
  command: >
    sudo awk -F: '($2 == "") {print}' /etc/shadow
  expected: ""
```

---

# Framework Mapping

Each control can be associated with one or more security frameworks.

Example:

```yaml
frameworks:
  CIS: "5.2.1"
  ISO27001: "A.8.20"
  NIST: "SC-8"
```

Currently supported mappings include:

* **CIS**
* **ISO/IEC 27001**
* **NIST**

The framework fields are metadata used to associate technical checks with broader compliance requirements.

> Framework mappings should be validated against the specific edition/version of each framework used by your organization.

---

# Example Output

Normal mode:

```text
Starting WomComp Compliance Scan...
Total tests: 50
================================================================================

[1/50] ✓ WOM-001 - SSH root login disabled
[2/50] ✓ WOM-002 - Password expiration configured
[3/50] ✗ WOM-003 - Unnecessary service disabled
[4/50] ✓ WOM-004 - Shadow file permissions
...

================================================================================
Scan Summary:
  Total tests: 50
  Passed: 42
  Failed: 8
  Compliance Score: 84.0%
================================================================================
```

Verbose mode provides additional evidence:

```text
================================================================================
✓ PASS - WOM-001
No vulnerabilities detected

Title: SSH root login disabled
Category: SSH
Severity: HIGH
Frameworks: CIS: 5.2.1 | ISO27001: A.8.20 | NIST: AC-6

Type: file_contains
File: /etc/ssh/sshd_config
Expected: PermitRootLogin no

Evidence:
  → PermitRootLogin no
================================================================================
```

---

# Compliance Score

WomComp calculates the compliance score using:

```text
Passed Tests / Total Tests × 100
```

For example:

```text
42 / 50 × 100 = 84%
```

The score is intended to provide a quick overview of the system's compliance posture.

It should **not** be interpreted as a formal certification or compliance attestation.

---

# Security Considerations

WomComp is designed to perform security configuration checks on Linux systems.

Some checks may require elevated privileges.

For example:

```bash
sudo python3 launcher.py -b
```

Be aware that command-based checks execute commands on the local system.

Only use YAML configurations from trusted sources.

Do not execute untrusted YAML files without reviewing the commands they contain.

---

# Adding New Tests

Adding a new compliance control does not require modifying the Python code when using an existing check type.

For example:

```yaml
- id: "WOM-010"
  title: "Ensure SSH protocol version is secure"
  category: "SSH"
  severity: "HIGH"

  frameworks:
    CIS: "5.2"
    ISO27001: "A.8.20"
    NIST: "SC-8"

  check:
    type: "file_contains"
    file: "/etc/ssh/sshd_config"
    expected: "Protocol 2"
```

The scanner automatically loads the test from the YAML configuration.

---

# Development

The project is intentionally modular.

### `launcher.py`

Responsible for:

* CLI arguments.
* Configuration selection.
* Starting the scan.
* Displaying the final result.

### `conf_tester.py`

Responsible for:

* Loading YAML configurations.
* Executing compliance checks.
* Collecting evidence.
* Calculating results.
* Displaying scan information.

---

# Roadmap

Planned improvements include:

* [ ] JSON output.
* [ ] CSV reporting.
* [ ] HTML reports.
* [ ] PDF compliance reports.
* [ ] Better logging.
* [ ] Additional CIS controls.
* [ ] More NIST mappings.
* [ ] More ISO 27001 mappings.
* [ ] Service status checks.
* [ ] Package/version checks.
* [ ] Network configuration checks.
* [ ] Kernel parameter checks.
* [ ] Systemd security checks.
* [ ] Docker/container security checks.
* [ ] Unit tests.
* [ ] CI/CD integration.
* [ ] Exit codes for automated pipelines.
* [ ] Configuration validation before scanning.
* [ ] Multiple Linux distribution support.

---

# Use Cases

WomComp can be used for:

### Blue Team

Quickly identify security configuration weaknesses on Linux systems.

### System Administration

Verify that security hardening configurations are correctly applied.

### GRC

Map technical controls to compliance frameworks and collect evidence.

### DevSecOps

Run compliance checks as part of infrastructure or deployment pipelines.

### Security Auditing

Generate repeatable evidence from system configuration.

### Learning

Understand how Linux security controls can be translated into automated checks.

---

# Limitations

WomComp is a technical configuration scanner.

It does not currently provide:

* Formal compliance certification.
* Complete vulnerability scanning.
* CVE vulnerability management.
* Network penetration testing.
* Exploitation capabilities.
* Full SIEM functionality.
* Continuous monitoring.

A passing test only means that the configured technical condition was satisfied at the time of the scan.

---

# Contributing

Contributions are welcome.

If you want to add a new check:

1. Create or update a YAML test.
2. Test it on the target Linux distribution.
3. Verify the expected evidence.
4. Document the control.
5. Submit a pull request.

For larger changes, open an issue first to discuss the proposed implementation.

---

# Disclaimer

WomComp is provided for **security auditing, compliance validation and defensive purposes**.

Always test security configurations in a controlled environment before deploying them to production.

The compliance results generated by WomComp should be reviewed by qualified security, system administration or GRC personnel.

WomComp does not replace a formal security assessment, audit or certification process.

---

# License

This project is licensed under the **MIT License**.

See the `LICENSE` file for details.

---

# Author

**WomComp**

Linux Compliance Scanner for:

**GRC · SysAdmin · DevSecOps · Blue Team**

---

⭐ If you find WomComp useful, consider giving the project a star.
