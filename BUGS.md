# Bugs Found in check-my-code (cmc)

> **Last Verified:** December 9, 2025 against v1.6.2

## Active Bugs

None currently.

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
- **cmc version:** 1.6.0
- **Node version:** >= 20 (as required)
- **Install method:** npm global install
