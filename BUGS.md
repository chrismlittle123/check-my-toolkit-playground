# Bugs Found in check-my-code (cmc)

> **Last Verified:** December 10, 2025 against v1.8.0

## Active Bugs

### BUG: MCP Server Path Traversal Vulnerability in check_files

**Severity:** High (Security)

**Description:** The MCP `check_files` tool does not properly validate file paths. When a path with directory traversal sequences (e.g., `../../../../../../etc/passwd`) is passed, the MCP server changes its `project_root` to the traversed directory instead of rejecting the request. This allows potential access to files outside the intended project directory.

**Steps to Reproduce:**
```bash
# Start MCP server and call check_files with path traversal
# Via MCP client:
check_files({ files: ["../../../../../../etc/passwd"] })

# Then call get_status to see the project_root changed:
get_status()
# Returns: { "project_root": "/etc", ... }
```

**Expected Behavior:** The MCP server should:
1. Reject paths that contain `..` sequences
2. Validate that resolved paths remain within the project root
3. Return a security error for path traversal attempts

**Actual Behavior:** The `project_root` is changed to follow the traversal path (e.g., `/etc`), potentially exposing sensitive system information.

**Impact:** AI agents using the MCP server could be tricked into reading files outside the project directory.

---

### BUG: Confusing Version Semantics in [extends] - Git Ref vs Manifest Version

**Severity:** Medium (UX)

**Description:** The `[extends]` feature uses `@version` syntax that is ambiguous and confusing. The version after `@` is NOT a git ref (branch/tag), but rather a manifest version from `rulesets.json`. However, error messages and initial attempts to clone use it as a git ref, leading to confusing errors.

**Steps to Reproduce:**
```bash
cat > cmc.toml << 'EOF'
[project]
name = "test"

[extends]
eslint = "github:chrismlittle123/check-my-code-community/production/typescript/5.5/eslint@1.0.0"
EOF

rm -rf ~/.cmc/cache/
cmc generate eslint
# Error: Failed to clone... fatal: Remote branch 1.0.0 not found
```

**Expected Behavior:** Either:
1. The `@version` should be a git ref (branch/tag), OR
2. The syntax should be clearer, like `github:owner/repo@gitref#ruleset/path:manifest-version`

**Actual Behavior:**
- First, cmc fetches the repo at `@latest` (hardcoded?) to read `rulesets.json`
- Then it tries to use the `@version` to fetch again, failing if it's not a git ref
- Using `@main` fails because it's not in the manifest
- Only `@latest` works, which is resolved from the manifest

**Workaround:** Always use `@latest` in extends:
```toml
[extends]
eslint = "github:chrismlittle123/check-my-code-community/production/typescript/5.5/eslint@latest"
```

---

### BUG: Local Rule Overrides Not Allowed with Extends (Design Question)

**Severity:** Low (UX/Design)

**Description:** When using `[extends]` to inherit from a remote ruleset, local rules in `[rulesets.eslint.rules]` cannot override inherited rules. Any conflict results in an error requiring removal of the local rule.

**Steps to Reproduce:**
```bash
cat > cmc.toml << 'EOF'
[project]
name = "test"

[extends]
eslint = "github:chrismlittle123/check-my-code-community/production/typescript/5.5/eslint@latest"

[rulesets.eslint.rules]
no-console = "warn"  # Trying to relax inherited "error" to "warn"
EOF

cmc generate eslint
# Error: Config conflict detected
#   Setting: "no-console" (eslint)
#   Inherited value: "error"
#   Local value: "warn"
# Local config cannot override inherited config.
```

**Expected Behavior:** Users should be able to override inherited rules for local customization (with optional warning).

**Actual Behavior:** Conflicts are rejected outright. Users can only ADD new rules, not modify inherited ones.

**Note:** This may be intentional design to enforce consistency. However, the inability to relax rules locally limits the flexibility of the extends feature.

---

## Design Notes / Expected Behavior

These items were initially reported as bugs but are actually intentional design decisions or working as expected.

### TSC Type Checking Configuration

**Status:** Working as expected

TSC runs correctly when `[rulesets.tsc]` is properly configured. The key is to use the correct configuration options directly in the `[rulesets.tsc]` section (e.g., `strict = true`, `noUncheckedIndexedAccess = true`), not nested under an `options` key.

**Correct Configuration:**
```toml
[rulesets.tsc]
enabled = true
strict = true
noUncheckedIndexedAccess = true
noImplicitReturns = true
```

---

### `cmc generate tsc` Options

**Status:** Working as expected

Options ARE included in the generated tsconfig.json output when configured correctly. Use top-level keys in `[rulesets.tsc]` like `strict`, `noUncheckedIndexedAccess`, `noImplicitReturns`.

---

### `cmc generate ruff` Configuration

**Status:** Working as expected

Rules ARE included in the generated ruff.toml when using the correct schema. Use `line-length`, `[rulesets.ruff.lint]` with `select` and `ignore` arrays.

**Correct Configuration:**
```toml
[rulesets.ruff]
line-length = 100

[rulesets.ruff.lint]
select = ["E", "F", "I", "UP"]
ignore = ["E501"]
```

---

### ESLint Rule Names Not Validated at Config Time

**Status:** Intentional design

ESLint rule names are arbitrary strings that depend on installed plugins. The tool cannot validate rule names at config time because:
1. Different projects use different ESLint plugins
2. Plugin rules are discovered at runtime by ESLint itself
3. Custom rules can have any name

Invalid rules will cause ESLint to fail at runtime with an appropriate error.

---

### `cmc audit` Allows Stricter Configs (warn → error)

**Status:** Intentional design

The audit command intentionally allows configs to be *stricter* than the cmc.toml baseline. This means:
- Changing `"warn"` to `"error"` in eslint.config.js is allowed (stricter)
- Changing `"error"` to `"warn"` IS detected as a mismatch (weaker)
- Changing to `"off"` IS detected as a mismatch (weaker)

This design allows teams to have a baseline config in cmc.toml while individual projects can opt into stricter rules.

---

## Fixed Bugs

### ~~BUG: Unknown Top-Level Sections in cmc.toml Are Silently Accepted~~ ✅ FIXED in v1.7.2

**Severity:** Medium

**Description:** Unknown top-level sections in cmc.toml passed validation without any warning or error.

**Fix:** v1.7.2 now rejects unknown top-level sections:
```
✗ cmc.toml has validation errors:
  - /: has unknown property 'totally_made_up_section'
```

---

### ~~BUG: Unknown Properties in `[project]` Section Are Silently Accepted~~ ✅ FIXED in v1.7.2

**Severity:** Medium

**Description:** Unknown properties within the `[project]` section passed validation without any warning.

**Fix:** v1.7.2 now rejects unknown properties in `[project]`:
```
✗ cmc.toml has validation errors:
  - /project: has unknown property 'unknown_key'
```

---

### ~~BUG: Race Condition in `cmc context` When Fetching Remote Templates~~ ✅ FIXED in v1.7.2

**Severity:** High

**Description:** Running multiple concurrent `cmc context` commands caused a race condition when cloning the remote templates repository.

**Fix:** v1.7.2 now handles concurrent context commands correctly with proper file locking.

---

### ~~BUG: Duplicate Templates in `[prompts]` Are Accepted and Duplicated in Output~~ ✅ FIXED in v1.7.2

**Severity:** Low

**Description:** When the same template was listed multiple times in `[prompts].templates`, content was duplicated in the output file.

**Fix:** v1.7.2 now deduplicates templates when generating output (duplicate templates in config are still accepted but only output once).

---

### ~~BUG: Invalid `[prompts]` Templates Pass Validation But Fail at Runtime~~ ✅ FIXED in v1.7.0

**Severity:** Medium

**Description:** Invalid template names in `[prompts].templates` pass schema validation but fail at runtime when using `cmc context`. Templates should be validated against the known list during `cmc validate`.

**Steps to Reproduce:**
```bash
cat > cmc.toml << 'EOF'
[project]
name = "test"

[prompts]
templates = ["invalid/template/name"]
EOF

cmc validate
# Output: ✓ cmc.toml is valid

cmc context --target claude
# Output: Error: Template "invalid/template/name" not found.
```

**Expected Behavior:** `cmc validate` should reject invalid template names with an error listing valid templates.

**Actual Behavior:** Validation passes, error only appears at runtime.

**Valid Templates:** `prototype/python/3.12`, `prototype/typescript/5.5`, `internal/python/3.12`, `internal/typescript/5.5`, `production/python/3.12`, `production/typescript/5.5`

**Fix:** v1.7.0 now validates template names during `cmc validate` using pattern matching:
```
✗ cmc.toml has validation errors:
  - /prompts/templates/0: must match pattern: ^(prototype|internal|production)/(python|typescript)/[0-9]+\.[0-9]+$
```

---

### ~~BUG: Non-Lintable Files Counted as "Checked"~~ ✅ FIXED in v1.6.6

**Severity:** Low

**Description:** Files without recognized extensions (or with non-lintable extensions like `.json`) are reported in the "files checked" count, even though no linter actually processes them.

**Steps to Reproduce:**
```bash
cat > cmc.toml << 'EOF'
[project]
name = "test"
EOF

echo 'const x = 1;' > noextension
echo '{"test": true}' > config.json

cmc check noextension config.json
# Output: ✓ No violations found (2 files checked)
```

**Expected Behavior:** Either:
1. Only count files that were actually linted, or
2. Warn that files have unrecognized extensions

**Actual Behavior:** Files are counted as "checked" even though no linter ran on them, which is misleading.

**Fix:** v1.6.6 now correctly reports "0 files checked" for non-lintable files.

---

### ~~BUG: `[files]` Section `include`/`exclude` Patterns Have No Effect~~ ✅ FIXED in v1.6.5

**Severity:** High

**Description:** The `[files]` section in `cmc.toml` with `include` and `exclude` patterns is completely ignored. Files are linted regardless of these patterns. The config validates successfully but has no effect on which files are checked.

**Steps to Reproduce:**
```bash
mkdir -p src vendor
echo 'const x = 1;' > src/app.ts
echo 'const y = 2;' > vendor/lib.ts
echo 'const z = 3;' > root.ts

cat > cmc.toml << 'EOF'
[project]
name = "test"

[files]
include = ["src/**/*.ts"]
exclude = ["vendor/**/*"]
EOF

cmc check .
# Expected: Only src/app.ts checked
# Actual: All 3 files are checked!
```

**Expected Behavior:** Only files matching `include` patterns (excluding those matching `exclude`) should be checked.

**Actual Behavior:** All TypeScript files in the directory are checked regardless of `[files]` settings.

**Additional Finding:** The `[files]` section accepts any arbitrary keys without validation:
```bash
cat > cmc.toml << 'EOF'
[project]
name = "test"

[files]
totally_invalid_key = ["test"]
EOF

cmc validate
# Output: ✓ cmc.toml is valid
```

**Fix:** v1.6.5 now correctly respects `[files]` include/exclude patterns and rejects unknown keys in the `[files]` section.

---

### ~~BUG: Invalid Linter Names in `[rulesets]` Are Silently Ignored~~ ✅ FIXED in v1.6.5

**Severity:** Medium

**Description:** Using an invalid linter name in the `[rulesets]` section (e.g., `[rulesets.invalidlinter]`) passes validation and is silently ignored at runtime. Users could misconfigure their rulesets without any warning.

**Steps to Reproduce:**
```bash
cat > cmc.toml << 'EOF'
[project]
name = "test"

[rulesets.invalidlinter]
enabled = true
rules = { "some-rule" = "error" }
EOF

cmc validate
# Output: ✓ cmc.toml is valid

cmc check .
# Runs without any warning about invalid linter
```

**Expected Behavior:** Validation should fail for unknown linter names. Valid linters are: `eslint`, `ruff`, `tsc`.

**Actual Behavior:** Invalid linter names are accepted and silently ignored.

**Fix:** v1.6.5 now validates linter names and rejects unknown properties in `[rulesets]` with error: "has unknown property 'invalidlinter'".

---

### ~~BUG: `--quiet --json` Flags Together Produce No Output~~ ✅ FIXED in v1.6.3

**Severity:** Medium

**Description:** When using both `--quiet` and `--json` flags together, `cmc check` produces zero output. The `--json` flag should take precedence and output JSON even in quiet mode, or at minimum the flags should be mutually exclusive with an error message.

**Steps to Reproduce:**
```bash
cmc check --quiet --json .
# Output: (empty)
echo $?
# Output: 1 (or 0 if no violations)
```

**Expected Behavior:** Either output JSON (--json should override --quiet for output), or error saying flags are mutually exclusive.

**Actual Behavior:** No output at all, only exit code.

**Fix:** v1.6.3 now correctly outputs JSON when both flags are used together.

---

### ~~BUG: Invalid `[extends]` Entries Are Silently Ignored~~ ✅ FIXED in v1.6.3

**Severity:** High

**Description:** Invalid entries in the `[extends]` section of `cmc.toml` are silently ignored instead of producing validation errors. This includes non-existent local files, invalid github format strings, and unknown protocols.

**Steps to Reproduce:**
```bash
cat > cmc.toml << 'EOF'
[project]
name = "test"

[extends]
invalid = "github:invalid"
nonexistent = "./does-not-exist.toml"
unknown = "ftp://example.com/config.toml"
EOF

cmc check
# Output: ✓ No violations found (0 files checked)

cmc validate
# Output: ✓ cmc.toml is valid
```

**Expected Behavior:** Validation should fail for:
- `github:invalid` - invalid github format (missing owner/repo/path)
- `./does-not-exist.toml` - file does not exist
- `ftp://...` - unknown protocol

**Actual Behavior:** All invalid extends are silently ignored, `cmc validate` reports config as valid.

**Fix:** v1.6.3 now validates extends entries:
- Unknown keys in `[extends]` are rejected
- Invalid `github:` format strings are rejected with pattern validation
- Only `github:owner/repo/path@version` format is now accepted

---

### ~~BUG: `[tools]` Section Does Not Disable Linters~~ ✅ FIXED in v1.6.3

**Severity:** High

**Description:** Setting `eslint = false`, `ruff = false`, or `tsc = false` in the `[tools]` section has no effect. Linters still run regardless of these settings.

**Steps to Reproduce:**
```bash
cat > cmc.toml << 'EOF'
[project]
name = "test"

[tools]
eslint = false
ruff = false
tsc = false
EOF

echo 'import os' > test.py
echo 'const x: number = "wrong";' > test.ts

cmc check .
# Output still shows eslint and ruff violations!
```

**Expected Behavior:** When `eslint = false`, ESLint should not run. Same for ruff and tsc.

**Actual Behavior:** All linters run regardless of `[tools]` settings.

**Note:** TSC requires `[rulesets.tsc] enabled = true` to run, but `[tools] tsc = true` alone does nothing. This is inconsistent - either `[tools]` should work for all linters, or documentation should clarify the correct configuration.

**Fix:** v1.6.3 now correctly respects `[tools]` settings. Setting `eslint = false` or `ruff = false` properly disables those linters.

---

### ~~BUG: Race Condition When Multiple Extends Reference Same Repository~~ ✅ FIXED in v1.6.2

**Severity:** High

**Description:** When `cmc.toml` has multiple `[extends]` entries that reference the same remote repository (e.g., both eslint and ruff configs from the same standards repo), a race condition occurs. Both extends try to clone/access the same cache directory simultaneously, causing either `ENOTEMPTY` or `File exists` errors.

**Steps to Reproduce:**
```bash
# Create cmc.toml with multiple extends from same repo
cat > cmc.toml << 'EOF'
[project]
name = "test"

[extends]
eslint = "github:chrismlittle123/check-my-code-community/rulesets/production/typescript/5.5/eslint@latest"
ruff = "github:chrismlittle123/check-my-code-community/rulesets/production/python/3.12@latest"
EOF

# Clear cache and run
rm -rf ~/.cmc/cache/
cmc check
```

**Error Output (one of two variants):**
```
Error: ENOTEMPTY, Directory not empty: /Users/.../cache/chrismlittle123-check-my-code-community-latest-xxx
```
or:
```
Error: Failed to load rulesets.json manifest: Failed to clone...: fatal: could not create work tree dir '...': File exists
```

**Expected Behavior:** Multiple extends from the same repository should share a single cache clone and resolve sequentially or use file locking.

**Actual Behavior:** Both extends try to clone the repository in parallel into the same cache directory, causing a race condition.

**Root Cause:** The `loadConfig()` function processes multiple `[extends]` entries in parallel (likely via `Promise.all`), but the cache key is derived from the repository (owner/repo@version), not the full ruleset path. When two extends reference the same repo, both attempt to clone simultaneously.

**Workaround:** Use extends from different repositories, or use pinned versions (may help in some cases).

---

## Test Environment
- **OS:** macOS Darwin 24.6.0
- **cmc version:** 1.8.0
- **Node version:** >= 20 (as required)
- **Install method:** npm global install
