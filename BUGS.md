# Bugs Found in check-my-code (cmc)

> **Last Verified:** December 6, 2025 against v1.5.5

---

## Bug: MCP Server `check_files` Tool Fails to Find Files

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

## Test Environment
- **OS:** macOS Darwin 24.6.0
- **cmc version:** 1.5.5
- **Node version:** >= 20 (as required)
- **Install method:** npm global install
