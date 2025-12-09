<!-- cmc:context:start:1845d01fe083 -->
## TypeScript 5.5 Coding Standards - PRODUCTION

Strict standards for production-grade, customer-facing code.

### Target Version

- Target TypeScript 5.5 specifically.
- Target Node.js 20 runtime.

### Tooling

- Use `pnpm` for package management.
- Use `package.json` for project configuration with `engines` field specifying Node version.
- Use `.nvmrc` to specify Node.js version.
- Use `eslint` for linting.
- Use `tsc --noEmit` for type checking (must pass with zero errors).

### Dependencies

- Pin versions with caret in `package.json` (e.g., `"express": "^4.18.0"`).
- Commit `pnpm-lock.yaml` to ensure deterministic builds.
- Use `pnpm install --frozen-lockfile` in CI/CD to fail if lockfile is out of date.

### Containers

- Use Docker for all production deployments (APIs, services, etc.).
- Use `pnpm install --frozen-lockfile` in Dockerfile for reproducible builds.
- Pin Node.js version explicitly in Dockerfile base image.

### Imports

- Remove all unused imports.
- Sort imports in the standard order: external dependencies, then internal modules.
- Use ES module imports (`import`/`export`), not CommonJS.
- No circular dependencies.

### Testing

- Every new feature must include unit tests and integration tests

### Type Checking

- Run `tsc --noEmit` in CI/CD pipeline - must pass with zero errors.
- Add type annotations to ALL function signatures (public and private).
- Enable `strict: true` in tsconfig.json.
- Enable `noUncheckedIndexedAccess: true` for safer array/object access.
- Enable `exactOptionalPropertyTypes: true` for stricter optional properties.
- Avoid `any` - use `unknown` and narrow with type guards.
- Avoid using free strings, use enums or union types where appropriate.
- Avoid using loose object types, use interfaces or type aliases for all object shapes.
- Use Zod schemas for runtime validation of external data.
- Use `readonly` for immutable properties and arrays.
- Use `as const` for literal types where applicable.

### Error Handling

- Handle errors explicitly. NEVER swallow errors silently.
- Prefer `unknown` over `any` in catch clauses.
- Use custom error classes for domain-specific errors.

### Security

- Never log sensitive data (passwords, tokens, PII).
- Validate all external inputs with runtime checks.
- Use parameterized queries for database operations.
- Avoid `eval()` and dynamic code execution.

<!-- cmc:context:end -->
