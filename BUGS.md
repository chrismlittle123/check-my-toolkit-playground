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

## Bug: CLI `check` Command Ignores Multiple File Arguments

**Severity:** High
**Component:** CLI (`cmc check`)
**Affected Versions:** 1.5.7
**Status:** ❌ NOT FIXED

### Description
When passing multiple file paths to `cmc check`, only the first file is processed. All subsequent files are silently ignored.

### Steps to Reproduce

1. Have two Python files with lint violations:
   - `test-bugs/test.py` (2 violations)
   - `test-bugs/newtest/test.py` (2 violations)

2. Run check with multiple files:
```bash
$ cmc check test-bugs/test.py test-bugs/newtest/test.py
```

**Result:**
```
test-bugs/test.py:2 [ruff/F401] `os` imported but unused
test-bugs/test.py:3 [ruff/F401] `sys` imported but unused

✗ 2 violations found
```

3. Reverse the order:
```bash
$ cmc check test-bugs/newtest/test.py test-bugs/test.py
```

**Result:**
```
test-bugs/newtest/test.py:1 [ruff/F401] `os` imported but unused
test-bugs/newtest/test.py:2 [ruff/F401] `sys` imported but unused

✗ 2 violations found
```

4. JSON output confirms only 1 file checked:
```bash
$ cmc check --json test-bugs/test.py test-bugs/newtest/test.py
```
```json
{
  "violations": [...],
  "summary": {
    "files_checked": 1,
    "violations_count": 2
  }
}
```

5. MCP `check_files` handles multiple files correctly (4 violations found):
```json
{"files": ["test-bugs/newtest/test.py", "test-bugs/test.py"]}
// Returns: files_checked: 2, 4 violations
```

### Expected Behavior
All specified files should be checked and violations from all files should be reported.

### Actual Behavior
- Only the first file argument is processed
- Subsequent file arguments are silently ignored
- No warning or error is shown about ignored files
- `files_checked` count confirms only 1 file was processed

### Root Cause
The CLI argument parser likely treats the `path` argument as a single value rather than accepting multiple values (variadic).

### Impact
- Users cannot check specific multiple files in a single command
- Must run separate `cmc check` commands for each file
- Inconsistent with MCP `check_files` which handles multiple files correctly
- Silent failure is particularly problematic - users may think all files were checked

### Workaround
Run `cmc check` separately for each file, or use directory-based checking (`cmc check <directory>`).

---

## Bug: CLI Returns Exit Code 0 for Nonexistent Files

**Severity:** High
**Component:** CLI (`cmc check`)
**Affected Versions:** 1.5.7
**Status:** ❌ NOT FIXED

### Description
When checking a file that doesn't exist, the CLI shows a warning but returns exit code 0 (success) instead of a non-zero error code. This can cause CI pipelines to pass even when file paths are incorrect.

### Steps to Reproduce

```bash
$ cmc check totally-fake-file-that-does-not-exist.py
Warning: Path not found: /path/to/totally-fake-file-that-does-not-exist.py
✓ No violations found (0 files checked)

$ echo $?
0
```

JSON output also shows success with 0 files checked:
```bash
$ cmc check --json nonexistent.py
Warning: Path not found: /path/to/nonexistent.py
{
  "violations": [],
  "summary": {
    "files_checked": 0,
    "violations_count": 0
  }
}
```

### Expected Behavior
- Return a non-zero exit code (e.g., 2 or 3) when the specified file doesn't exist
- Or at minimum, don't show "✓ No violations found" which implies success

### Actual Behavior
- Shows "Warning: Path not found" to stderr
- Shows "✓ No violations found (0 files checked)" - misleading success message
- Returns exit code 0 (success)

### Impact
- **CI/CD pipelines will pass** even with typos in file paths
- Users may not notice their files aren't being checked
- The success checkmark "✓" is misleading when no files were actually checked
- Silent failures in automated workflows

### Workaround
Check the `files_checked` count in JSON output, or verify file existence before running cmc.

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

## Bug: TSC Type Checking Ignores File List and Checks Entire Project

**Severity:** Medium
**Component:** Linter Runner (`runTsc`)
**Affected Versions:** 1.5.7
**Status:** ❌ NOT FIXED

### Description
When TypeScript type checking is enabled and the user checks specific files, `runTsc()` ignores the file list and runs `tsc --noEmit` on the entire project. This is inconsistent with ESLint and Ruff which respect the file list.

### Steps to Reproduce

1. Have a project with multiple TypeScript files, some with type errors
2. Check only a specific clean file:
```bash
$ cmc check src/clean-file.ts
```

**Result:** TSC reports type errors from other files in the project, not just `clean-file.ts`

3. Looking at the source code in `runners.js`:
```javascript
export async function runLinters(projectRoot, files, options) {
    // ESLint and Ruff correctly check only specified files

    if (tsFiles.length > 0 && options?.tscEnabled) {
        const tscViolations = await runTsc(projectRoot);  // No files parameter!
        violations.push(...tscViolations);
    }
}

export async function runTsc(projectRoot) {  // Doesn't accept files parameter
    const args = ["--noEmit", "--pretty", "false"];  // Checks entire project
```

### Expected Behavior
TSC should only report type errors from the files the user requested to check, consistent with ESLint and Ruff behavior.

### Actual Behavior
- TSC checks all TypeScript files in the project regardless of which files were specified
- User sees type errors from files they didn't ask to check
- Wastes time checking files not being worked on

### Impact
- Inconsistent behavior between linters (ESLint/Ruff respect file list, TSC doesn't)
- Slower performance when checking single files
- Confusing output with violations from unrequested files

### Workaround
Filter the TSC violations manually, or disable TSC checking when checking individual files.

---

## Bug: Potential Path Traversal in MCP `check_files`

**Severity:** Medium (Security)
**Component:** MCP Server (`validateFiles`)
**Affected Versions:** 1.5.7
**Status:** ❌ NOT FIXED

### Description
The `validateFiles()` function doesn't validate that resolved paths stay within the project root. A malicious MCP client could potentially check files outside the project directory using path traversal.

### Steps to Reproduce

```javascript
// In MCP check_files call:
{
  "files": ["../../../../etc/passwd", "../../../sensitive-config.json"]
}
```

Looking at the source code in `utils.js`:
```javascript
export async function validateFiles(files, projectRoot, cwd) {
    const baseCwd = cwd ? resolve(cwd) : process.cwd();
    const validFiles = [];
    const checkPromises = files.map(async (file) => {
        const fullPath = isAbsolute(file) ? file : resolve(baseCwd, file);
        const stats = await stat(fullPath).catch(() => null);
        if (stats?.isFile()) {
            return relative(projectRoot, fullPath);  // No check if path starts with "../"
        }
        return null;
    });
```

### Expected Behavior
Paths that resolve outside the project root should be rejected.

### Actual Behavior
- Paths like `../../../sensitive-file` may be accepted
- After `relative(projectRoot, fullPath)`, the result could be `../../sensitive-file`
- This path is then passed to linters

### Impact
- MCP client could potentially scan files outside project directory
- While linters might not process non-JS/Python files, it's still a security concern
- Violation of principle of least privilege

### Recommended Fix
```javascript
const relativePath = relative(projectRoot, fullPath);
if (relativePath.startsWith('..')) {
    return null;  // Reject files outside project root
}
return relativePath;
```

---

## Bug: Silent Failure When Linter Output is Malformed JSON

**Severity:** Low-Medium
**Component:** Linter Parsers (`parsers.js`)
**Affected Versions:** 1.5.7
**Status:** ❌ NOT FIXED

### Description
All parser functions silently return empty arrays when JSON parsing fails. This masks genuine linter errors and makes debugging difficult.

### Steps to Reproduce

When a linter crashes or produces invalid output, the parsers swallow the error:

```javascript
// From parsers.js
export function parseRuffOutput(output, projectRoot) {
    if (!output.trim())
        return [];
    try {
        const results = JSON.parse(output);
        return results.map(/* ... */);
    }
    catch {
        return [];  // Silently swallows parse errors!
    }
}
```

### Expected Behavior
When JSON parsing fails, the error should be logged or reported so users know the linter failed.

### Actual Behavior
- If a linter crashes or produces invalid output, users get "✓ No violations found"
- No indication that the linter failed to run properly
- Same issue exists in `parseESLintOutput()` and error handlers in `runners.js`

### Impact
- Users might think their code is clean when the linter actually failed
- Makes debugging linter issues very difficult
- Could pass CI pipelines incorrectly if linters are broken

### Workaround
Check verbose output or linter logs manually if you suspect issues.

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

### ✅ FIXED in v1.5.7: MCP Server `check_files` Tool Path Resolution

**Previous Issue:** The `check_files` tool failed to find files - relative paths returned "No valid files found" and absolute paths had the leading `/` stripped.

**Status:** Fixed. Both relative and absolute paths now work correctly.

---

## Test Environment
- **OS:** macOS Darwin 24.6.0
- **cmc version:** 1.5.7
- **Node version:** >= 20 (as required)
- **Install method:** npm global install
