# Bugs Found in check-my-code (cmc)

> **Last Verified:** December 8, 2025 against v1.5.7

---

## Bug: MCP Server `check_project` Returns "No Lintable Files" for Subdirectories

**Severity:** High
**Component:** MCP Server (`cmc mcp-server`)
**Affected Versions:** 1.5.7
**Status:** ❌ NOT FIXED

### Description
The MCP server's `check_project` tool fails to find lintable files when given a subdirectory path, while the CLI and `check_files` tool work correctly for the same files.

### Steps to Reproduce

1. Start the MCP server (e.g., via Claude Code integration)
2. Have a valid Python file at `test-bugs/newtest/test.py` with lint violations
3. Call `check_project` with the subdirectory path:
```json
{"path": "test-bugs/newtest"}
```

**Result:**
```json
{
  "success": true,
  "violations": [],
  "files_checked": 0,
  "has_violations": false,
  "message": "No lintable files found"
}
```

4. Call `check_files` with the same file (works correctly):
```json
{"files": ["test-bugs/newtest/test.py"]}
```

**Result:**
```json
{
  "success": true,
  "violations": [
    {"file": "test.py", "line": 1, "rule": "F401", "message": "`os` imported but unused"},
    {"file": "test.py", "line": 2, "rule": "F401", "message": "`sys` imported but unused"}
  ],
  "files_checked": 1,
  "has_violations": true
}
```

5. CLI also works correctly:
```bash
$ cmc check test-bugs/newtest/
test-bugs/newtest/test.py:1 [ruff/F401] `os` imported but unused
test-bugs/newtest/test.py:2 [ruff/F401] `sys` imported but unused

✗ 2 violations found
```

### Expected Behavior
The MCP `check_project` tool should discover and lint files in subdirectories the same way the CLI does.

### Actual Behavior
- `check_project` with subdirectory path: Returns "No lintable files found" with 0 files checked
- `check_files` with explicit file path: Works correctly
- CLI `cmc check <subdir>`: Works correctly

### Root Cause
The MCP server's `check_project` tool appears to have a bug in its file discovery logic when given a subdirectory path. It may be looking for files relative to the wrong directory or failing to traverse the given path.

### Impact
- MCP integration cannot scan subdirectories for violations
- Users must explicitly list files using `check_files` instead of scanning directories
- Inconsistent behavior between MCP tools (`check_project` vs `check_files`) and CLI

### Workaround
Use `check_files` with explicit file paths instead of `check_project` with a directory path.

---

## Fixed Bugs

### ✅ FIXED in v1.5.7: MCP Server `check_files` Tool Path Resolution

**Previous Issue:** The `check_files` tool failed to find files - relative paths returned "No valid files found" and absolute paths had the leading `/` stripped.

**Status:** Fixed. Both relative and absolute paths now work correctly.

---

## Test Environment
- **OS:** macOS Darwin 24.6.0
- **cmc version:** 1.5.7
- **Node version:** >= 20 (as required)
- **Install method:** npm global install
