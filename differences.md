# Discrepancies: features.md vs v0.18.0 Documentation

## Version Mismatch
| Item | Local features.md | v0.18.0 Docs |
|------|-------------------|--------------|
| Version | 0.17.1 | 0.18.0 |
| Tool Count | Not specified | 14 integrated tools |

---

## Missing Commands

Local features.md is missing:
- `cm init` - Create check.toml with default configuration
- `cm check` - Alias for `cm code check`
- `cm audit` - Alias for `cm code audit`

---

## Missing Feature: Disable Comments Detection

The entire `[code.quality.disable-comments]` feature is **not documented** in local features.md.

v0.18.0 includes:
```toml
[code.quality.disable-comments]
enabled = true
extensions = ["ts", "tsx", "js", "jsx", "py"]
exclude = ["tests/**", "**/*.test.ts"]
patterns = [
  "eslint-disable",
  "@ts-ignore",
  "# noqa"
]
```

Detects: ESLint disables, TypeScript ignores, Python noqa/type:ignore, Prettier ignores

---

## Missing Section: How `cm validate config` Works

v0.18.0 documents the two-step validation process:
1. TOML parsing via `@iarna/toml`
2. Schema validation via Zod (`configSchema.safeParse()`)

---

## Incomplete Tool Detection Lists

### Knip
| Local | v0.18.0 |
|-------|---------|
| Orphaned files | Unused files (orphaned) |
| Unused dependencies | Unused dependencies |
| Unused exports | Unused devDependencies |
| | Unused exports |
| | Unused types/interfaces |
| | Unlisted dependencies |
| | Duplicate exports |

### Vulture
| Local | v0.18.0 |
|-------|---------|
| Dead functions | Unused functions |
| Unused classes | Unused classes |
| Unused variables | Unused variables |
| | Unused imports |
| | Unused methods |
| | Unused attributes |
| | Unreachable code |

---

## Test Validation Pattern Difference

| Local | v0.18.0 |
|-------|---------|
| `**/*.test.ts` | `**/*.{test,spec}.{ts,tsx,js,jsx,py}` |

v0.18.0 default pattern is more comprehensive, supporting spec files and multiple languages.

---

## Missing Sections in Local

1. **Architecture** - Full `src/` directory structure with all tool files
2. **Tool Summary Table** - 14-tool overview table with Category/Tool/Languages/Config Key
3. **Roadmap Status** - Version milestones v0.1 through v0.4+ and Future items
4. **Registry with ref support** - `github:owner/repo@v1.0.0` format not mentioned

---

## Missing Tool Details

Local features.md lacks detailed tables for each tool showing:
- Underlying command executed
- Config file locations
- Detailed feature lists

Example for ESLint (missing in local):
| Property | Value |
|----------|-------|
| Command | `npx eslint . --format json` |
| Config Files | `eslint.config.js`, `eslint.config.mjs`, `.eslintrc.*` |

---

## Additional Feature in Local (Not in v0.18.0)

Local mentions ESLint feature not in v0.18.0 docs:
> "Built-in eslint-plugin-import rules for circular dependency detection"

---

## Version History Gap

Local version history ends at 0.17.0. Missing:
- 0.18.0 changes (if any beyond what's documented)
- Disable comments feature addition

---

## Summary of Required Updates

To align features.md with v0.18.0:

1. Update version to 0.18.0
2. Add `cm init`, `cm check`, `cm audit` commands
3. Add `[code.quality.disable-comments]` section
4. Add "How cm validate config Works" section
5. Expand Knip detection list (7 items)
6. Expand Vulture detection list (7 items)
7. Update default test pattern
8. Add Architecture section
9. Add Tool Summary table
10. Add Roadmap Status section
11. Document registry ref support (`@v1.0.0`)
12. Add detailed tool property tables
