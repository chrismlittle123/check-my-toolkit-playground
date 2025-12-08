# Bugs Found in check-my-code (cmc)

> **Last Verified:** December 8, 2025 against v1.5.9

---

## Bug: CLI Fails on TypeScript Files Outside Project Root

**Severity:** Medium
**Component:** CLI (`cmc check`)
**Affected Versions:** 1.5.7
**Status:** ❌ NOT FIXED

### Description
The CLI fails with "ESLint failed to execute: eslint exited with code 2" when checking TypeScript files in deeply nested directories or outside the eslint config scope, while the MCP `check_files` tool works correctly for the same files.

### Steps to Reproduce

1. Have a TypeScript file in a deeply nested directory:
   `test-bugs/deep/path/to/nested/files/test.ts`

2. Try to check it via CLI:
```bash
$ cmc check test-bugs/deep/path/to/nested/files/test.ts
Error: ESLint failed to execute: eslint exited with code 2
```

3. MCP `check_files` works correctly:
```json
{"files": ["test-bugs/deep/path/to/nested/files/test.ts"]}
// Returns violations successfully
```

### Expected Behavior
CLI should check TypeScript files regardless of directory depth, or provide a meaningful error message.

### Actual Behavior
- CLI fails with generic "ESLint failed to execute" error
- No indication of the actual problem
- MCP tool handles the same file correctly

### Root Cause
Likely an issue with ESLint config resolution - the CLI may not be finding or using the correct eslint.config.js for deeply nested files.

### Impact
- Cannot use CLI to check files in certain directory structures
- Inconsistent behavior between CLI and MCP tools
- Unhelpful error message doesn't guide users to a solution

### Workaround
Use MCP `check_files` tool instead of CLI for problematic paths.

---

## Bug: Race Condition in `commandExists()` Function

**Severity:** Low
**Component:** Linter Command Detection (`command.js`)
**Affected Versions:** 1.5.7
**Status:** ❌ NOT FIXED

### Description
The `commandExists()` function has a subtle race condition where both 'error' and 'close' event handlers can call `resolve()`, potentially causing unexpected behavior.

### Code Analysis

```javascript
// From command.js
export async function commandExists(cmd) {
    return new Promise((resolve) => {
        const proc = spawn(cmd, ["--version"], { stdio: "ignore" });
        proc.on("error", () => resolve(false));
        proc.on("close", (code) => resolve(code === 0));
        // If 'close' fires before 'error' is fully handled, behavior is undefined
    });
}
```

### Expected Behavior
The function should resolve exactly once with a deterministic result.

### Actual Behavior
- In edge cases (e.g., command not found but system is slow), both events might fire
- While JS promises only settle once, the logic flow is not clearly controlled
- Could cause flaky behavior in rare circumstances

### Impact
- May cause intermittent false positives/negatives for command detection
- Difficult to reproduce but could cause "linter not found" errors randomly

### Recommended Fix
Track resolution state explicitly:
```javascript
export async function commandExists(cmd) {
    return new Promise((resolve) => {
        let resolved = false;
        const proc = spawn(cmd, ["--version"], { stdio: "ignore" });
        proc.on("error", () => { if (!resolved) { resolved = true; resolve(false); } });
        proc.on("close", (code) => { if (!resolved) { resolved = true; resolve(code === 0); } });
    });
}
```

---

## Bug: Missing Null Check in AJV Error Formatting

**Severity:** Low
**Component:** Config Loader (`loader.js`)
**Affected Versions:** 1.5.7
**Status:** ❌ NOT FIXED

### Description
The `formatAjvError()` function accesses properties like `error.params.missingProperty` without null checks, which could cause crashes if AJV returns malformed error objects.

### Code Analysis

```javascript
// From loader.js
function formatAjvError(error) {
    switch (error.keyword) {
        case "required":
            return `missing required property '${error.params.missingProperty}'`;  // No null check
        case "type":
            return `must be ${error.params.type}`;  // No null check
        // ...
    }
}
```

### Expected Behavior
Function should handle missing or malformed error params gracefully.

### Actual Behavior
- If AJV returns an error with missing `params`, this will crash
- Error: "Cannot read property 'missingProperty' of undefined"

### Impact
- Config validation could crash instead of showing helpful error
- User sees generic error instead of specific validation failure

### Recommended Fix
Use optional chaining:
```javascript
return `missing required property '${error.params?.missingProperty ?? 'unknown'}'`;
```

---

## Fixed Bugs

### ✅ FIXED in v1.5.9: MCP Server `check_project` Returns "No Lintable Files" for Subdirectories

**Previous Issue:** The MCP server's `check_project` tool failed to find lintable files when given a subdirectory path.

**Status:** Fixed. `src/mcp/handlers.ts` now properly resolves paths relative to `process.cwd()`.

---

### ✅ FIXED in v1.5.9: CLI `check` Command Ignores Multiple File Arguments

**Previous Issue:** When passing multiple file paths to `cmc check`, only the first file was processed.

**Status:** Fixed. `src/cli/commands/check.ts` now accepts `[paths...]` (variadic), and `runCheck()` discovers files from all paths in parallel.

**Verified:**
```bash
$ cmc check test-bugs/test.py test-bugs/newtest/test.py
test-bugs/newtest/test.py:1 [ruff/F401] `os` imported but unused
test-bugs/newtest/test.py:2 [ruff/F401] `sys` imported but unused
test-bugs/test.py:2 [ruff/F401] `os` imported but unused
test-bugs/test.py:3 [ruff/F401] `sys` imported but unused

✗ 4 violations found
```

---

### ✅ FIXED in v1.5.9: CLI Returns Exit Code 0 for Nonexistent Files

**Previous Issue:** When checking a file that doesn't exist, CLI returned exit code 0 (success).

**Status:** Fixed. `src/cli/commands/check.ts` now throws a `ConfigError` when explicit paths are provided but none found, resulting in exit code 2.

**Verified:**
```bash
$ cmc check nonexistent-file.py
Error: Path not found: nonexistent-file.py
$ echo $?
2
```

---

### ✅ FIXED in v1.5.9: TSC Type Checking Ignores File List

**Previous Issue:** When checking specific files, `runTsc()` ignored the file list and checked the entire project.

**Status:** Fixed. `src/linter/runners.ts` now accepts an optional `files` parameter and calls `filterViolationsByFiles()` to filter violations to only include requested files.

---

### ✅ FIXED in v1.5.9: Path Traversal in MCP `check_files`

**Previous Issue:** The `validateFiles()` function didn't validate that resolved paths stay within the project root.

**Status:** Fixed. `src/mcp/utils.ts` now has `isWithinProjectRoot()` function that rejects paths starting with `..`.

**Verified:** Path traversal attempts like `../../../../etc/passwd` are silently rejected (only valid files within project are checked).

---

### ✅ FIXED in v1.5.9: Silent Failure When Linter Output is Malformed JSON

**Previous Issue:** Parser functions silently returned empty arrays when JSON parsing failed.

**Status:** Fixed. `src/linter/parsers.ts` now returns a `ParseResult` with a `parseError` field, and runners properly throw `LinterError` when `parseError` is returned.

---

### ✅ FIXED in v1.5.7: MCP Server `check_files` Tool Path Resolution

**Previous Issue:** The `check_files` tool failed to find files - relative paths returned "No valid files found" and absolute paths had the leading `/` stripped.

**Status:** Fixed. Both relative and absolute paths now work correctly.

---

## Test Environment
- **OS:** macOS Darwin 24.6.0
- **cmc version:** 1.5.9
- **Node version:** >= 20 (as required)
- **Install method:** npm global install
