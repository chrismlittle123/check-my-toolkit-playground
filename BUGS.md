# Bugs Found in check-my-code (cmc)

> **Last Verified:** December 9, 2025 against v1.6.2

## Active Bugs

### BUG: `--quiet --json` Flags Together Produce No Output

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

---

### BUG: Invalid `[extends]` Entries Are Silently Ignored

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

---

### BUG: `[tools]` Section Does Not Disable Linters

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

---

## Fixed Bugs

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
- **cmc version:** 1.6.2
- **Node version:** >= 20 (as required)
- **Install method:** npm global install
