# Bugs Found in check-my-code (cmc)

> **Last Verified:** December 6, 2025 against v1.5.5
> **Status:** Bugs #1 and #2 FIXED in v1.5.5. **New bug #3 found in v1.5.5.**

---

## Bug #3: MCP Server `check_files` Tool Fails to Find Files (NEW - v1.5.5)

**Severity:** High
**Component:** MCP Server (`cmc mcp-server`)
**Affected Versions:** 1.5.5
**Status:** ❌ NOT FIXED

### Description
The MCP server's `check_files` tool fails to find files that exist and can be checked via the CLI. The tool appears to have path resolution issues:

1. Relative paths return "No valid files found to check"
2. Absolute paths have the leading `/` stripped, causing "No such file or directory" errors

### Steps to Reproduce

1. Start the MCP server (e.g., via Claude Code integration)
2. Have a valid Python file at `test-bugs/newtest/test.py`
3. Call `check_files` with relative path:
```json
{"files": ["test-bugs/newtest/test.py"]}
```

**Result:**
```json
{
  "success": false,
  "error": {
    "code": "FILE_NOT_FOUND",
    "message": "No valid files found to check"
  }
}
```

4. Call `check_files` with absolute path:
```json
{"files": ["/Users/.../test-bugs/newtest/test.py"]}
```

**Result:**
```json
{
  "success": true,
  "violations": [{
    "file": "Users/.../test.py",  // Note: leading / stripped!
    "rule": "E902",
    "message": "No such file or directory (os error 2)"
  }]
}
```

### Expected Behavior
The MCP `check_files` tool should find and lint files the same way the CLI does:
```bash
$ cmc check test-bugs/newtest/test.py
test-bugs/newtest/test.py:1 [ruff/F401] `os` imported but unused
```

### Actual Behavior
- Relative paths: Returns FILE_NOT_FOUND error
- Absolute paths: Strips leading `/`, causing linter to fail with "No such file or directory"

### Root Cause
The MCP server appears to incorrectly resolve file paths relative to the project root or strips path prefixes incorrectly.

### Impact
- MCP integration with AI tools (Claude Code, Cursor) cannot check specific files
- Users must rely on `check_project` instead of targeted file checks
- `fix_files` tool is also affected (same path resolution issue)

---

## Bug #1: Missing Schema File - `cmc validate` Crashes (CRITICAL)

**Severity:** Critical
**Command:** `cmc validate`
**Affected Versions:** 1.4.5, 1.5.1
**Fixed In:** v1.5.5
**Status:** ✅ FIXED

### Description
The `cmc validate` command crashes with a file not found error because the `schemas` directory is missing from the npm package distribution.

### Steps to Reproduce
1. Run `cmc validate` in any directory (with or without a cmc.toml)

### Expected Behavior
The command should validate the cmc.toml file against the JSON schema.

### Actual Behavior
```
Error: ENOENT: no such file or directory, open '/opt/homebrew/lib/node_modules/check-my-code/schemas/cmc.schema.json'
```

### Root Cause
The `schemas/` directory was not included in the npm package. The installed package structure shows:
```
/opt/homebrew/lib/node_modules/check-my-code/
├── compatibility.yaml
├── dist/
├── node_modules/
├── package.json
└── README.md
```

No `schemas/` directory is present.

### Impact
- The `cmc validate` command is completely non-functional
- Users cannot validate their cmc.toml files
- CI/CD pipelines using validation will fail

---

## Bug #2: Incorrect Template Name Format in Documentation/Help

**Severity:** Medium
**Commands:** `cmc context --help`, error messages
**Affected Versions:** 1.4.5, 1.5.1
**Fixed In:** v1.5.5
**Status:** ✅ FIXED

### Description
The help text and error messages show incorrect template name format that doesn't match the actual available templates.

### Steps to Reproduce
1. Run `cmc context --help`
2. Follow the documented example: `templates = ["typescript/5.5"]`
3. Run `cmc context --target claude --stdout`

### Expected Behavior
The documented template name format should work.

### Actual Behavior
```
Error: Template "typescript/5.5" not found.
Available templates: prototype/python/3.12, prototype/typescript/5.5, internal/python/3.12, internal/typescript/5.5, production/python/3.12, production/typescript/5.5
```

### Documentation Shows (Incorrect)
```
templates = ["typescript/5.5"]
```

### Correct Format
```
templates = ["production/typescript/5.5"]
```

### Affected Locations
1. `cmc context --help` example shows wrong format
2. Error messages from `cmc context` suggest the old format
3. The `cmc info` command shows languages but not available prompt templates

### Impact
- New users will follow documentation and get errors
- Confusion about the correct template naming convention
- Additional time spent debugging configuration

---

## Additional Observations (Minor Issues)

### Observation 1: `cmc generate` accepts invalid template references silently
When using `[rulesets.eslint] template = "nonexistent/template"`, the generate command succeeds without warning that the template doesn't exist. It generates a default config instead of warning the user.

### Observation 2: `cmc info` doesn't show available prompt templates
The `cmc info` command shows supported languages and linters but doesn't list the available prompt templates (production/typescript/5.5, etc.). This would help users discover the correct template names.

### Observation 3: Exit codes could be more consistent
- Exit code 1 = violations found (expected)
- Exit code 2 = user error (invalid args, missing config)
- Exit code 3 = internal error

The missing schema file issue exits with code 3, which is correct, but some error messages could be more helpful.

---

## Test Environment
- **OS:** macOS Darwin 24.6.0
- **cmc version:** Initially tested on 1.4.5, re-verified on 1.5.1, confirmed fixed in 1.5.5
- **Node version:** >= 20 (as required)
- **Install method:** npm global install

## Verification History
| Date | Version | Bug #1 | Bug #2 | Bug #3 |
|------|---------|--------|--------|--------|
| 2025-12-06 | 1.4.5 | ❌ Present | ❌ Present | N/A |
| 2025-12-06 | 1.5.1 | ❌ Present | ❌ Present | N/A |
| 2025-12-06 | 1.5.5 | ✅ Fixed | ✅ Fixed | ❌ Present |
