---
date: 2025-10-14 22:12:30 UTC
researcher: Claude Code
git_commit: 2863a34d6fed68ebdf42914b6e356220ce2084f7
branch: chore/crdant/converts-to-uv
repository: replicatedhq/replicated-python
topic: "UV Migration Analysis for Replicated Python SDK"
tags: [research, codebase, uv, dependency-management, python-packaging, migration]
status: complete
last_updated: 2025-10-14
last_updated_by: Claude Code
---

# Research: UV Migration Analysis for Replicated Python SDK

**Date**: 2025-10-14 22:12:30 UTC
**Researcher**: Claude Code
**Git Commit**: 2863a34d6fed68ebdf42914b6e356220ce2084f7
**Branch**: chore/crdant/converts-to-uv
**Repository**: replicatedhq/replicated-python

## Research Question

Research this Python repository to understand its current structure and determine what changes are needed to use `uv` (the modern Python package installer and project manager) and recommend it to users.

## Summary

The Replicated Python SDK currently uses a **modern setuptools-based build system** with `pyproject.toml` as the primary configuration file. The project has no legacy setup.py or requirements.txt files, making it an ideal candidate for uv migration. The current setup includes:

- **Build System**: setuptools with setuptools_scm for version management
- **Dependency Management**: All dependencies declared in pyproject.toml
- **Development Tools**: Black, isort, mypy, flake8, pytest
- **CI/CD**: GitHub Actions for testing (Python 3.8-3.12) and PyPI publishing
- **Local Development**: Makefile and check.sh script for common tasks, direnv for environment management

The migration to uv can be achieved with **minimal breaking changes** while providing significant developer experience improvements through faster dependency resolution and installation.

## Detailed Findings

### 1. Current Python Packaging Setup

#### pyproject.toml Structure
**Location**: `/pyproject.toml`

The project uses a fully modern pyproject.toml-based setup:

```toml
[build-system]
requires = ["setuptools>=45", "wheel", "setuptools_scm[toml]>=6.2"]
build-backend = "setuptools.build_meta"

[project]
name = "replicated"
requires-python = ">=3.8"
dependencies = [
    "httpx>=0.24.0",
    "typing-extensions>=4.0.0",
]
dynamic = ["version"]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-asyncio>=0.21.0",
    "pytest-mock>=3.10.0",
    "black>=23.0.0",
    "isort>=5.12.0",
    "mypy>=1.0.0",
    "flake8>=6.0.0",
]
```

**Key Observations**:
- No legacy setup.py or requirements.txt files present
- Uses setuptools_scm for automatic version management from git tags
- Clean separation of runtime vs development dependencies
- Supports Python 3.8-3.12 (6 versions)
- Only 2 runtime dependencies (httpx, typing-extensions)
- 7 development dependencies for testing and linting

#### Version Management
The project uses **setuptools_scm** which automatically derives version from git tags. This is critical for the migration - uv supports this pattern but requires careful configuration.

### 2. Documentation and User Guides

#### Installation Instructions
**Location**: `/README.md:6-11`

Current installation command:
```bash
pip install --upgrade replicated
```

The README provides clear examples for:
- Basic synchronous usage
- Asynchronous usage with context managers
- Custom state directory configuration
- Links to external documentation

**Location**: `/API_REFERENCE.md:1-7`

API reference also shows standard pip installation:
```bash
pip install replicated
```

#### Developer Setup
**Location**: `/examples/README.md`

Examples directory includes:
- basic_example.py - Basic SDK usage
- sync_example.py - Comprehensive synchronous example
- async_example.py - Asynchronous usage patterns
- metrics_example.py - Metrics and telemetry

Examples assume users can run Python scripts directly after pip install.

### 3. CI/CD and Automation

#### GitHub Actions Workflows

**Test Workflow** (`/.github/workflows/test.yml`):
```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.8', '3.9', '3.10', '3.11', '3.12']

    steps:
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -e .[dev]

    - name: Run tests
      run: pytest

    - name: Run linting
      run: |
        flake8 replicated tests examples
        mypy replicated

    - name: Check formatting
      run: |
        black --check replicated tests examples
        isort --check-only replicated tests examples
```

**Publish Workflow** (`/.github/workflows/publish.yml`):
```yaml
jobs:
  publish:
    - name: Install build dependencies
      run: |
        python -m pip install --upgrade pip
        python -m pip install build

    - name: Build package
      run: python -m build
```

Uses PyPA's trusted publishing for secure PyPI deployment.

#### Local Development Scripts

**Makefile** (`/Makefile`):
- `make install`: pip install -e .
- `make dev`: pip install -e .[dev]
- `make test`: pytest
- `make lint`: flake8 + mypy
- `make format`: black + isort
- `make build`: python -m build
- `make ci`: Comprehensive local CI simulation

**check.sh** (`/check.sh`):
Bash script that runs the full CI suite locally (tests, linting, formatting checks).

#### Environment Management

**direnv** (`/.envrc`):
```bash
layout python python3.12
dotenv_if_exists
```

Uses direnv to automatically activate a Python 3.12 virtual environment.

### 4. Files and Changes Needed for UV Adoption

#### Files to Modify

1. **pyproject.toml** - Core configuration changes
2. **README.md** - Update installation instructions
3. **API_REFERENCE.md** - Update installation instructions
4. **examples/README.md** - Add uv-based setup instructions
5. **.github/workflows/test.yml** - Add uv-based CI workflow
6. **.github/workflows/publish.yml** - Update to use uv for building
7. **Makefile** - Add uv targets while keeping pip targets
8. **.envrc** - Update to use uv's environment management
9. **check.sh** - Update to optionally use uv

#### Files to Create

1. **uv.lock** - Lock file for reproducible builds (generated by uv)
2. **.python-version** - Python version specification for uv
3. **MIGRATION.md** - Guide for users migrating to uv (optional)

#### Files That Don't Need Changes

- All source code in `replicated/`
- Test code in `tests/`
- Example scripts (just run with uv run instead of python)

### 5. UV Best Practices and Integration Patterns

#### Core UV Commands for This Project

**Installation and Setup**:
```bash
# Install uv itself
curl -LsSf https://astral.sh/uv/install.sh | sh

# Sync dependencies from pyproject.toml
uv sync

# Install development dependencies
uv sync --extra dev

# Install the project in editable mode
uv pip install -e .
```

**Running Commands**:
```bash
# Run tests
uv run pytest

# Run linting
uv run flake8 replicated tests examples
uv run mypy replicated

# Format code
uv run black replicated tests examples
uv run isort replicated tests examples

# Run example scripts
uv run examples/basic_example.py
```

**Building and Publishing**:
```bash
# Build package
uv build

# Publish to PyPI (if uv adds publish support)
# Otherwise: uv run twine upload dist/*
```

#### UV Configuration in pyproject.toml

UV doesn't require extensive configuration changes. The existing pyproject.toml will work with minimal modifications:

**Recommended additions**:
```toml
[tool.uv]
dev-dependencies = [
    # Same as [project.optional-dependencies.dev]
    # UV prefers this location for dev deps
]

[tool.uv.sources]
# Only needed if using custom package sources
```

#### Lock File Management

UV will generate a `uv.lock` file that should be:
- **Committed to git** for reproducible builds
- **Updated** when dependencies change
- **Synced** regularly with pyproject.toml

#### Python Version Management

Create `.python-version`:
```
3.12
```

This tells uv which Python version to use by default.

### 6. Migration Path and Backwards Compatibility

#### Recommended Migration Strategy

**Phase 1: Additive Changes (Non-Breaking)**
1. Add `.python-version` file
2. Add uv-based alternatives to Makefile (keep pip targets)
3. Update documentation to show both pip and uv methods
4. Add uv.lock to .gitignore initially (optional)

**Phase 2: CI/CD Integration**
1. Add parallel uv-based CI workflow (keep existing pip workflow)
2. Update publish workflow to use uv build
3. Test both workflows in parallel

**Phase 3: Documentation Updates**
1. Update README.md to recommend uv (show pip as alternative)
2. Update API_REFERENCE.md
3. Update examples/README.md
4. Add migration guide for contributors

**Phase 4: Full Adoption**
1. Commit uv.lock file
2. Make uv the primary recommendation
3. Keep pip compatibility for users who prefer it
4. Update direnv configuration to use uv

#### Backwards Compatibility Considerations

**Users Installing the Package**:
- No breaking changes - pip install replicated will continue to work
- PyPI package format remains the same
- Users can choose pip or uv

**Contributors/Developers**:
- Both pip and uv workflows should work
- Makefile should support both methods
- CI should test both installation methods (initially)

**Build System**:
- Continue using setuptools as build backend (uv supports this)
- Keep setuptools_scm for version management
- uv build will use the same build backend

### 7. Specific File Changes Required

#### pyproject.toml Changes

**Minimal changes** (uv works with existing format):
```toml
# Optional: Add uv-specific configuration
[tool.uv]
# UV can use the existing [project.optional-dependencies.dev]
# Or you can move them here:
dev-dependencies = [
    "pytest>=7.0.0",
    "pytest-asyncio>=0.21.0",
    "pytest-mock>=3.10.0",
    "black>=23.0.0",
    "isort>=5.12.0",
    "mypy>=1.0.0",
    "flake8>=6.0.0",
]
```

**Note**: The existing setuptools build-backend will continue to work with uv.

#### .github/workflows/test.yml Changes

Add uv-based workflow (parallel to existing):
```yaml
- name: Install uv
  uses: astral-sh/setup-uv@v3
  with:
    version: "latest"

- name: Set up Python ${{ matrix.python-version }}
  run: uv python install ${{ matrix.python-version }}

- name: Install dependencies
  run: uv sync --extra dev

- name: Run tests
  run: uv run pytest

- name: Run linting
  run: |
    uv run flake8 replicated tests examples
    uv run mypy replicated

- name: Check formatting
  run: |
    uv run black --check replicated tests examples
    uv run isort --check-only replicated tests examples
```

#### Makefile Changes

Add uv targets:
```makefile
# UV-based targets
.PHONY: uv-sync uv-dev uv-test uv-lint uv-format

uv-sync:
	uv sync

uv-dev:
	uv sync --extra dev

uv-test:
	uv run pytest

uv-lint:
	uv run flake8 replicated tests examples
	uv run mypy replicated

uv-format:
	uv run black replicated tests examples
	uv run isort replicated tests examples

# Keep existing pip targets for compatibility
```

#### README.md Changes

Update installation section:
```markdown
## Installation

### Using uv (recommended)

```bash
uv pip install replicated
```

### Using pip

```bash
pip install --upgrade replicated
```
```

#### .python-version Creation

Create new file:
```
3.12
```

This ensures uv uses Python 3.12 by default (matching .envrc).

## Code References

- `/pyproject.toml:1-83` - Main project configuration
- `/README.md:6-11` - Current installation instructions
- `/Makefile:1-63` - Development automation
- `/.github/workflows/test.yml:1-44` - CI testing workflow
- `/.github/workflows/publish.yml:1-38` - PyPI publishing workflow
- `/.envrc:1-2` - direnv Python environment setup
- `/examples/README.md:1-49` - Example usage documentation

## Architecture Insights

### Current Architecture Strengths

1. **Modern from the Start**: No legacy setup.py or requirements.txt to migrate from
2. **Clean Dependencies**: Minimal runtime dependencies (httpx, typing-extensions)
3. **Standard Tooling**: Uses standard Python packaging (PEP 517/518 compliant)
4. **Version Automation**: setuptools_scm eliminates manual version management
5. **Comprehensive Testing**: Multi-version Python testing (3.8-3.12)
6. **Development Automation**: Makefile and check.sh for consistent workflows

### UV Benefits for This Project

1. **Speed**: 10-100x faster dependency resolution and installation
2. **Reproducibility**: uv.lock ensures exact dependency versions
3. **Simplicity**: Single tool for virtual environments, dependencies, and building
4. **Modern**: Better support for modern Python packaging standards
5. **Cross-platform**: Consistent behavior across macOS, Linux, Windows
6. **Monorepo-friendly**: Better support for workspace-style projects

### Potential Challenges

1. **setuptools_scm Compatibility**: Need to verify uv build works with setuptools_scm
2. **Version Management**: Ensure git-based versioning continues to work
3. **CI/CD Transition**: Need to test uv in GitHub Actions environment
4. **User Communication**: Need to clearly communicate uv benefits without forcing migration
5. **Lock File Size**: uv.lock may be large with transitive dependencies

## Migration Recommendations

### Phase 1: Proof of Concept (Week 1)

1. Create `.python-version` file
2. Test `uv sync` locally
3. Test `uv build` with setuptools_scm
4. Verify all make targets work with uv
5. Test examples with `uv run`

### Phase 2: Documentation (Week 1-2)

1. Add uv installation instructions to README.md
2. Update API_REFERENCE.md with uv examples
3. Create CONTRIBUTING.md with both pip and uv workflows
4. Add uv examples to examples/README.md

### Phase 3: CI/CD Integration (Week 2)

1. Add uv-based test workflow (parallel to pip)
2. Update publish workflow to use `uv build`
3. Test both workflows in pull requests
4. Monitor for any build or test failures

### Phase 4: Full Adoption (Week 3)

1. Make uv the primary recommendation in docs
2. Commit uv.lock file
3. Update Makefile to default to uv (keep pip fallback)
4. Update .envrc to use uv venv management
5. Add migration guide for contributors

### Phase 5: Optimization (Week 4+)

1. Remove redundant pip-based CI workflow if uv proves stable
2. Optimize uv.lock updates in CI
3. Consider using uv for faster local development
4. Explore uv's workspace features for future monorepo needs

## Best Practices for UV Integration

### 1. Maintain Pip Compatibility

**Why**: Not all users have adopted uv yet
**How**: Keep both pip and uv instructions in documentation

### 2. Commit uv.lock

**Why**: Reproducible builds for contributors
**How**: Add uv.lock to git after Phase 3

### 3. Use uv in CI/CD

**Why**: Faster CI runs, better reliability
**How**: Migrate workflows incrementally

### 4. Document the Migration

**Why**: Help users and contributors understand the change
**How**: Create MIGRATION.md or update CONTRIBUTING.md

### 5. Test Thoroughly

**Why**: Ensure no breaking changes
**How**: Run full test suite with both pip and uv before switching

### 6. Version Pinning Strategy

**Why**: Balance between security updates and stability
**How**: Use minimum version specifiers (>=) in pyproject.toml, exact versions in uv.lock

## Open Questions

1. **setuptools_scm + uv build compatibility**: Does `uv build` properly invoke setuptools_scm to derive version from git tags?
   - **Action**: Test `uv build` and verify version in built wheel/sdist

2. **Lock file in library projects**: Should a library project commit uv.lock?
   - **Standard practice**: Libraries typically don't commit lock files (only applications do)
   - **Alternative**: Use uv.lock for development but not for end users
   - **Recommendation**: Commit uv.lock for reproducible contributor environments

3. **GitHub Actions uv cache**: How to optimize uv caching in GitHub Actions?
   - **Action**: Research astral-sh/setup-uv caching strategies
   - **Potential**: Cache `~/.cache/uv` to speed up CI

4. **Migration timeline**: Should this be a gradual or immediate switch?
   - **Recommendation**: Gradual (4-week phased approach outlined above)

5. **User impact**: Will recommending uv confuse users who are familiar with pip?
   - **Mitigation**: Show both methods, make pip still prominent
   - **Communication**: Emphasize uv as "optional but recommended"

6. **Tool compatibility**: Do all dev tools (black, mypy, flake8) work well with `uv run`?
   - **Action**: Test each tool with `uv run` prefix
   - **Expected**: Should work transparently

## Related Research

No existing research documents found in proposals/ directory. This is the first comprehensive analysis of uv migration for this project.

## Conclusion

The Replicated Python SDK is an **ideal candidate for uv adoption** due to its modern packaging setup and lack of legacy configuration files. The migration can be accomplished with minimal breaking changes through a phased approach:

1. **Non-breaking additions** (uv as alternative option)
2. **Parallel CI/CD** (both pip and uv)
3. **Documentation updates** (recommend uv, support pip)
4. **Full adoption** (uv as primary, pip as fallback)

The key benefits include:
- **10-100x faster** dependency installation
- **Reproducible builds** via uv.lock
- **Simplified tooling** (one tool instead of pip + venv + build)
- **Better developer experience** for contributors

The migration requires changes to:
- 6 existing files (documentation + CI)
- 2 new files (.python-version, uv.lock)
- 0 breaking changes for end users

**Recommendation**: Proceed with Phase 1 (Proof of Concept) to validate compatibility, then execute the 4-week phased migration plan.
