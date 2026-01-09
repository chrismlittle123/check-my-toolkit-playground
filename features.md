# check-my-toolkit Features Documentation

**Version:** 0.17.1
**Package:** [check-my-toolkit](https://www.npmjs.com/package/check-my-toolkit)
**CLI Command:** `cm`

## Overview

check-my-toolkit is a unified CLI tool for project health checks that consolidates multiple code quality utilities through a single `check.toml` configuration file. It provides consistent output across different linting, formatting, and type checking tools.

**Key Benefits:**
- Single configuration file for all tools
- Standardized output format regardless of underlying tool
- Organization-wide standards via registry extension
- CI automation ready with exit codes and JSON output
- Multi-language support (TypeScript, JavaScript, Python)

---

## Installation

```bash
npm install -g check-my-toolkit
```

---

## Commands

### Main Commands

| Command | Description |
|---------|-------------|
| `cm code check` | Execute all enabled code quality checks |
| `cm code audit` | Verify tool configurations exist without running checks |
| `cm validate config` | Validate `check.toml` syntax and structure |
| `cm validate registry` | Validate registry structure (rulesets/*.toml) |
| `cm schema config` | Output JSON schema for configuration files |

### Global Options

| Option | Description |
|--------|-------------|
| `-V, --version` | Output version number |
| `-h, --help` | Display help for command |

### Command-Specific Options

#### `cm code check`
| Option | Description |
|--------|-------------|
| `-c, --config <path>` | Path to check.toml config file |
| `-f, --format <format>` | Output format: `text` (default) or `json` |

#### `cm code audit`
| Option | Description |
|--------|-------------|
| `-c, --config <path>` | Path to check.toml config file |
| `-f, --format <format>` | Output format: `text` (default) or `json` |

#### `cm validate config`
| Option | Description |
|--------|-------------|
| `-c, --config <path>` | Path to check.toml config file |
| `-f, --format <format>` | Output format: `text` (default) or `json` |

#### `cm validate registry`
| Option | Description |
|--------|-------------|
| `-f, --format <format>` | Output format: `text` (default) or `json` |

---

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | All checks pass |
| 1 | Violations detected |
| 2 | Configuration error |
| 3 | Runtime error |

---

## Supported Tools

### Linting

#### ESLint (JavaScript/TypeScript)
```toml
[code.linting.eslint]
enabled = true
files = ["src/**/*.ts"]
ignore = ["**/*.test.ts"]
max-warnings = 0

[code.linting.eslint.rules]
"no-unused-vars" = "error"
"no-console" = { severity = "warn" }
```

**Features:**
- Custom file patterns with glob support
- Ignore patterns for excluding files
- Maximum warnings threshold
- Rule severity configuration (off, warn, error)
- Rule options via object format
- Built-in eslint-plugin-import rules for circular dependency detection

#### Ruff (Python)
```toml
[code.linting.ruff]
enabled = true
format = false
line-length = 88

[code.linting.ruff.lint]
select = ["E", "F", "W"]
ignore = ["E501"]
```

**Features:**
- Optional format checking mode
- Configurable line length
- Rule selection and ignoring

### Formatting

#### Prettier (JavaScript/TypeScript/JSON/CSS)
```toml
[code.formatting.prettier]
enabled = true
```

Verifies that files are properly formatted according to Prettier rules.

### Type Checking

#### TypeScript Compiler (tsc)
```toml
[code.types.tsc]
enabled = true

[code.types.tsc.require]
strict = true
noImplicitAny = true
strictNullChecks = true
noUnusedLocals = true
noUnusedParameters = true
noImplicitReturns = true
noFallthroughCasesInSwitch = true
esModuleInterop = true
skipLibCheck = true
forceConsistentCasingInFileNames = true
```

**Features:**
- Type checking enforcement
- Configurable strict mode settings
- Auditing of tsconfig.json compiler options

#### ty (Python Type Checker)
```toml
[code.types.ty]
enabled = true
```

Astral's fast Python type checker for rapid validation.

### Unused Code Detection

#### Knip (JavaScript/TypeScript)
```toml
[code.unused.knip]
enabled = true
```

Detects:
- Orphaned files
- Unused dependencies
- Unused exports

#### Vulture (Python)
```toml
[code.unused.vulture]
enabled = true
```

Detects:
- Dead functions
- Unused classes
- Unused variables

### Test Validation

```toml
[code.tests]
enabled = true
pattern = "**/*.test.ts"
min_test_files = 1
```

**Features:**
- Custom glob patterns for test file detection
- Minimum test file count requirements

### Security Scanning

#### Secrets Detection (Gitleaks)
```toml
[code.security.secrets]
enabled = true
```

Scans for hardcoded secrets, API keys, and credentials in the codebase.

#### npm Audit
```toml
[code.security.npmaudit]
enabled = true
```

Scans JavaScript/TypeScript dependencies for known vulnerabilities.

**Features:**
- Supports both npm and pnpm package managers
- Auto-detects package manager via lock files

#### pip-audit
```toml
[code.security.pipaudit]
enabled = true
```

Scans Python dependencies for known vulnerabilities.

### File/Folder Naming Conventions

```toml
[code.naming]
enabled = true

[[code.naming.rules]]
extensions = ["ts", "tsx"]
file_case = "kebab-case"
folder_case = "kebab-case"
exclude = ["tests/fixtures/**"]

[[code.naming.rules]]
extensions = ["py"]
file_case = "snake_case"
folder_case = "snake_case"
```

**Supported Cases:**
- `kebab-case`
- `snake_case`
- `camelCase`
- `PascalCase`

**Features:**
- Per-extension rules
- Separate file and folder case requirements
- Exclude patterns for bypassing certain paths

---

## Configuration

### Configuration File

Create a `check.toml` file in your project root:

```toml
# Extend from a registry (optional)
[extends]
registry = "github:org/repo-name"
rulesets = ["typescript-strict", "security-baseline"]

# Local configuration
[code.linting.eslint]
enabled = true
files = ["src/**/*.ts"]

[code.formatting.prettier]
enabled = true

[code.types.tsc]
enabled = true

[code.types.tsc.require]
strict = true
noImplicitAny = true

[code.unused.knip]
enabled = true

[code.security.secrets]
enabled = true

[code.tests]
enabled = true
pattern = "**/*.test.ts"
min_test_files = 5
```

### Config Auto-Discovery

The CLI automatically searches for `check.toml` starting from the current directory and walking up the directory tree. Use `-c` flag to specify an explicit path.

### Registry Extension

Inherit configurations from remote registries:

```toml
[extends]
registry = "github:organization/registry-repo"
rulesets = ["typescript-internal", "security-strict"]
```

**Supported Registry Sources:**
- GitHub repositories (`github:owner/repo`)
- Local paths

**Features:**
- Multi-ruleset merging
- Local overrides take precedence over registry settings

---

## JSON Schema

Generate JSON schema for IDE integration and AI agents:

```bash
cm schema config
```

This outputs a JSON schema that can be used for:
- Editor autocompletion
- Configuration validation
- AI agent integration

---

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Code Quality
on: [push, pull_request]

jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
      - run: npm ci
      - run: npm install -g check-my-toolkit
      - run: cm code check
```

### JSON Output for Parsing

```bash
cm code check --format json
```

Returns structured JSON with check results for programmatic consumption.

---

## Domains

### CODE Domain (Implemented)
Current stable domain covering:
- Linting (ESLint, Ruff)
- Formatting (Prettier, Ruff Format)
- Type Checking (tsc, ty)
- Unused Code Detection (Knip, Vulture)
- Test Validation
- Security Scanning (Gitleaks, npm audit, pip-audit)
- Naming Conventions

### PROCESS Domain (Planned)
Future domain for workflow compliance:
- PR size limits
- Branch naming conventions
- Ticket reference requirements
- Repository settings validation

### STACK Domain (Planned)
Future domain for environment validation:
- Version requirements
- Environment configuration

---

## Version History Highlights

| Version | Feature |
|---------|---------|
| 0.17.0 | pnpm support for dependency auditing |
| 0.16.0 | eslint-plugin-import integration |
| 0.15.0 | TOML-friendly ESLint rule options |
| 0.14.0 | Mandatory `files` for ESLint rules |
| 0.13.0 | ESLint rules auditing |
| 0.12.0 | ESLint files, ignore, max-warnings |
| 0.11.0 | `cm schema config` command |
| 0.10.0 | File/folder naming conventions |
| 0.9.0 | TypeScript config auditing |
| 0.8.0 | Registry extension system |
| 0.7.0 | Gitleaks secrets detection |
| 0.6.0 | ty Python type checker |
| 0.5.0 | Test file validation |
| 0.4.0 | Prettier formatting |
| 0.3.0 | Ruff format checking |
| 0.2.0 | Knip unused code detection |

---

## Resources

- **npm:** https://www.npmjs.com/package/check-my-toolkit
- **GitHub:** https://github.com/chrismlittle123/check-my-toolkit
- **Issues:** https://github.com/chrismlittle123/check-my-toolkit/issues
