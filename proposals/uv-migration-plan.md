---
date: 2025-10-15
author: Claude Code
git_commit: 2863a34d6fed68ebdf42914b6e356220ce2084f7
branch: chore/crdant/converts-to-uv
repository: replicatedhq/replicated-python
topic: "UV Migration Implementation Plan for Replicated Python SDK"
tags: [plan, uv, dependency-management, python-packaging, migration, implementation]
status: approved
based_on: proposals/research/uv-migration-analysis.md
research_date: 2025-10-14
plan_date: 2025-10-15
---

# UV Migration Implementation Plan

**Plan Created**: 2025-10-15
**Author**: Claude Code
**Based On**: [UV Migration Analysis](./research/uv-migration-analysis.md) (2025-10-14)
**Branch**: chore/crdant/converts-to-uv
**Repository**: replicatedhq/replicated-python

## Executive Summary

This plan outlines the implementation of UV (modern Python package installer) support for the Replicated Python SDK. This migration is **non-breaking** and uses a **phased approach** over approximately 4 weeks.

### What is UV?

UV is a fast Python package installer and project manager written in Rust by Astral (the creators of Ruff). It provides 10-100x faster dependency resolution and installation compared to pip, along with improved reproducibility through lock files.

### What This Plan Accomplishes

- ✅ **Add UV support** for faster, more reproducible builds
- ✅ **Maintain full pip compatibility** (zero breaking changes for users)
- ✅ **Update documentation** to recommend UV while fully supporting pip
- ✅ **Validate UV in CI/CD** before full adoption
- ✅ **Provide clear migration path** for contributors

### What This Plan Does NOT Do

- ❌ **No breaking changes** for end users (pip continues to work)
- ❌ **No forced migration** (UV is recommended, not required)
- ❌ **No changes to published package** (PyPI package format unchanged)
- ❌ **No changes to public API** or SDK functionality

## Project Context

### Current State

The Replicated Python SDK uses:
- **Build System**: setuptools with setuptools_scm for git-based versioning
- **Dependency Management**: pyproject.toml with pip installation
- **CI/CD**: GitHub Actions with pip-based workflows
- **Development**: Makefile + check.sh for local automation
- **Environment**: direnv with Python 3.12

### Target State

After migration, the SDK will support:
- **Build System**: Unchanged (setuptools + setuptools_scm)
- **Dependency Management**: pyproject.toml + uv.lock for reproducibility
- **CI/CD**: Parallel pip and UV workflows (eventually UV primary)
- **Development**: Makefile with both pip and UV targets
- **Environment**: direnv with UV integration

### Migration Strategy

**Additive, Not Replacement**: UV is added alongside pip, not replacing it. This ensures:
- No breaking changes for end users
- Contributors can choose their preferred tool
- Gradual transition with safety checkpoints
- Easy rollback at any phase

## Implementation Timeline

### Phase 1: Local Proof of Concept (Week 1)
**Duration**: 3 hours
**Goal**: Validate UV works with existing project structure

### Phase 2: Documentation (Week 1-2)
**Duration**: 2.25 hours
**Goal**: Update docs to show both pip and UV methods

### Phase 3: CI/CD Integration (Week 2-3)
**Duration**: 5.5 hours
**Goal**: Add UV to CI/CD, validate in parallel with pip

### Phase 4: Full Adoption (Week 3-4)
**Duration**: 3.5 hours
**Goal**: Make UV primary recommendation, maintain pip support

**Total Estimated Effort**: ~14 hours over 4 weeks

## Detailed Implementation Tasks

### Phase 1: Local Proof of Concept (Week 1)

#### Task 1.1: Create `.python-version` File
**Duration**: 15 minutes
**Prerequisites**: None

Create a `.python-version` file in the project root specifying Python 3.12 (matching current .envrc setup). UV uses this file to determine which Python version to use.

**Deliverables**:
- `.python-version` file at project root containing `3.12`

**Validation**:
- `uv python install` recognizes and uses Python 3.12

---

#### Task 1.2: Test UV Sync and Dependency Installation
**Duration**: 30 minutes
**Prerequisites**: Task 1.1

Verify UV can correctly sync dependencies from the existing `pyproject.toml` file, including both runtime (httpx, typing-extensions) and dev dependencies (pytest, black, mypy, etc.).

**Deliverables**:
- Confirmation that `uv sync` and `uv sync --extra dev` work correctly
- Notes on any dependency resolution differences from pip

**Validation**:
- All dependencies install without errors
- `uv run python -c "import httpx; import typing_extensions"` succeeds
- `uv run pytest --version` works

---

#### Task 1.3: Verify setuptools_scm Compatibility
**Duration**: 1 hour
**Prerequisites**: Task 1.2
**🚨 CRITICAL**: Must pass before Phase 3

Verify that `uv build` works with setuptools_scm to automatically derive the version from git tags. This is critical functionality that must work correctly.

**Deliverables**:
- Confirmation that `uv build` produces correctly versioned packages
- Test artifacts in dist/ directory

**Validation**:
- `uv build` completes successfully
- Version in wheel/sdist filenames matches git-derived version
- No warnings about missing version information

---

#### Task 1.4: Test Development Tools with uv run
**Duration**: 1 hour
**Prerequisites**: Task 1.2

Test all development tools (pytest, black, mypy, flake8, isort) with the `uv run` prefix to ensure they work correctly and exit codes behave properly (important for CI).

**Deliverables**:
- Confirmation that all dev tools work with `uv run` prefix
- Notes on any behavioral differences

**Validation**:
- All tools execute successfully
- Exit codes work correctly (0 for success, non-zero for failures)
- Tool output is identical to direct execution

---

### Phase 2: Documentation (Week 1-2)

#### Task 2.1: Add UV Targets to Makefile
**Duration**: 1 hour
**Prerequisites**: Phase 1 complete

Add UV-equivalent targets for all existing Makefile commands using `uv-` prefix (e.g., `uv-dev`, `uv-test`). Keep all existing pip targets unchanged for backward compatibility.

**Deliverables**:
- Updated Makefile with UV targets
- All existing pip targets maintained

**Validation**:
- `make uv-dev` installs all dev dependencies
- `make uv-test` runs the test suite
- `make uv-lint`, `make uv-format`, `make uv-build` all work
- All existing `make` targets still work unchanged

---

#### Task 2.2: Update README.md with UV Installation
**Duration**: 30 minutes
**Prerequisites**: Task 2.1

Add UV installation instructions to README.md while keeping pip instructions visible and valid. Briefly explain UV's benefits (speed, reproducibility).

**Deliverables**:
- Updated README.md with dual installation instructions

**Validation**:
- README renders correctly
- Both installation methods are accurate
- UV presented as recommended but not required

---

#### Task 2.3: Update API_REFERENCE.md
**Duration**: 15 minutes
**Prerequisites**: Task 2.1

Update API_REFERENCE.md to include UV installation alongside pip, maintaining consistency with README.md.

**Deliverables**:
- Updated API_REFERENCE.md with UV installation

**Validation**:
- API_REFERENCE.md renders correctly
- Installation instructions match README.md style

---

#### Task 2.4: Update examples/README.md
**Duration**: 30 minutes
**Prerequisites**: Task 2.1

Update examples README to show how to run examples with both UV (`uv run examples/basic_example.py`) and pip.

**Deliverables**:
- Updated examples/README.md with UV instructions

**Validation**:
- Examples README is clear
- Both UV and pip methods shown

---

### Phase 3: CI/CD Integration (Week 2-3)

#### Task 3.1: Create UV-Based Test Workflow
**Duration**: 2 hours
**Prerequisites**: Phase 2 complete
**🚨 CRITICAL**: Must validate across Python 3.8-3.12

Create a UV-based GitHub Actions workflow that runs tests across Python 3.8-3.12, using the astral-sh/setup-uv action. Run in parallel with existing pip workflow.

**Deliverables**:
- New UV-based CI workflow (test-uv.yml or updated test.yml)

**Validation**:
- Workflow runs successfully on push
- All Python versions (3.8-3.12) pass
- Tests, linting, and formatting checks all pass
- Workflow completes faster than pip workflow

---

#### Task 3.2: Update Publish Workflow
**Duration**: 1 hour
**Prerequisites**: Task 1.3 (setuptools_scm validation)

Update the publish workflow to use `uv build` instead of `python -m build`. Maintain setuptools_scm version derivation and PyPI trusted publishing.

**Deliverables**:
- Updated publish.yml using uv build

**Validation**:
- Workflow builds successfully
- Package version is correct (from setuptools_scm)
- Trusted publishing continues to work

---

#### Task 3.3: Test Parallel Workflows
**Duration**: 2 hours
**Prerequisites**: Tasks 3.1, 3.2
**✅ CHECKPOINT**: Both workflows must pass before Phase 4

Run both pip and UV workflows on the same code changes to ensure they produce consistent results. This validates UV as a reliable alternative.

**Deliverables**:
- Confirmation that both workflows work correctly
- Performance comparison data

**Validation**:
- Both workflows pass consistently
- Test results are identical
- UV workflow is faster
- No unexpected errors

---

#### Task 3.4: Generate and Commit uv.lock
**Duration**: 30 minutes
**Prerequisites**: Task 3.1

Generate and commit uv.lock to the repository for reproducible development environments. While lock files are sometimes controversial for libraries, this helps contributors get consistent setups.

**Deliverables**:
- uv.lock file committed to repository

**Validation**:
- Lock file contains all expected dependencies
- `uv sync` with lock file produces consistent environment
- CI workflows use the lock file correctly

---

### Phase 4: Full Adoption (Week 3-4)

#### Task 4.1: Update Documentation to Recommend UV
**Duration**: 1 hour
**Prerequisites**: Phase 3 complete

Update all documentation to recommend UV as the primary installation method while maintaining pip as a fully supported option. Add brief explanation of UV benefits.

**Deliverables**:
- Updated README.md, API_REFERENCE.md, examples/README.md emphasizing UV

**Validation**:
- Documentation is clear and helpful
- UV recommended but not mandated
- Pip remains valid, supported option

---

#### Task 4.2: Update .envrc for UV
**Duration**: 30 minutes
**Prerequisites**: Task 1.1

Update .envrc to use UV for environment management, improving integration with direnv while maintaining Python 3.12 as default.

**Deliverables**:
- Updated .envrc using UV

**Validation**:
- `direnv allow` succeeds
- Entering directory activates UV environment
- UV commands work correctly

---

#### Task 4.3: Create Migration/Contributing Guide
**Duration**: 2 hours
**Prerequisites**: All previous tasks

Create or update CONTRIBUTING.md with clear documentation for contributors explaining both UV and pip workflows. Include setup, daily commands, dependency management, lock file maintenance, and troubleshooting.

**Deliverables**:
- New or updated CONTRIBUTING.md

**Validation**:
- Documentation is clear and complete
- Both workflows well-documented
- Examples are accurate
- Troubleshooting section is helpful

---

## Key Architecture Decisions

### 1. Lock File Strategy
**Decision**: Commit uv.lock to repository
**Rationale**: Provides reproducible development environments for contributors, even though this is a library not an application
**Trade-off**: Slightly larger repo, but better contributor experience

### 2. Parallel Workflows
**Decision**: Run both pip and UV workflows during Phase 3
**Rationale**: Validates UV without risking CI stability; provides safety net
**Trade-off**: Slightly longer CI times during transition

### 3. Documentation Emphasis
**Decision**: Recommend UV but fully support pip
**Rationale**: UV offers significant benefits, but pip is more familiar and universally available
**Trade-off**: Must maintain documentation for both methods

### 4. Makefile Approach
**Decision**: Add UV targets with `uv-` prefix, keep existing targets
**Rationale**: Zero breaking changes for existing contributors; clear naming convention
**Trade-off**: More Makefile targets to maintain

### 5. Build Backend
**Decision**: Keep setuptools as build backend
**Rationale**: UV supports setuptools; setuptools_scm compatibility proven; no need to change
**Trade-off**: None - this is the safe choice

## Risk Assessment and Mitigation

### Risk 1: setuptools_scm Compatibility
**Severity**: High
**Likelihood**: Low
**Mitigation**: Task 1.3 explicitly validates this before any CI changes
**Contingency**: If incompatible, document limitation and use UV only for dev dependencies

### Risk 2: CI Performance or Reliability
**Severity**: Medium
**Likelihood**: Low
**Mitigation**: Parallel workflows in Phase 3; keep pip workflow as fallback
**Contingency**: Can revert to pip-only if UV workflow proves unstable

### Risk 3: User Confusion
**Severity**: Low
**Likelihood**: Medium
**Mitigation**: Clear documentation showing both methods; "recommended" not "required"
**Contingency**: Gather feedback and adjust documentation emphasis

### Risk 4: Tool Compatibility Issues
**Severity**: Low
**Likelihood**: Low
**Mitigation**: Task 1.4 validates all dev tools with `uv run`
**Contingency**: Document any tools requiring special UV configuration

### Risk 5: Lock File Maintenance Burden
**Severity**: Low
**Likelihood**: Low
**Mitigation**: Document lock file updates in contributing guide
**Contingency**: Can remove lock file from repo if it causes issues

## Success Criteria

### Phase 1 Success
- [ ] UV can sync all dependencies from pyproject.toml
- [ ] `uv build` produces correct versioned packages
- [ ] All dev tools work with `uv run`

### Phase 2 Success
- [ ] Documentation clearly shows both UV and pip methods
- [ ] Makefile has working UV targets
- [ ] No confusion about which method to use

### Phase 3 Success
- [ ] UV workflow passes all tests on all Python versions
- [ ] Both pip and UV workflows run successfully in parallel
- [ ] uv.lock is committed and works in CI

### Phase 4 Success
- [ ] UV is recommended in all documentation
- [ ] Contributors have clear guidance for both methods
- [ ] No breaking changes for any users

## Rollback Plan

The migration is designed to be **reversible at any point** with no user impact:

**During Phase 1-2**: Simply don't commit the changes; no impact

**During Phase 3**: Disable UV workflow; keep pip workflow running; no user impact

**During Phase 4**: Revert documentation emphasis; UV remains optional; no user impact

**After completion**: UV can be removed entirely by reverting to pip-only setup without any breaking changes for users

## Files Modified and Created

### Files to Modify (6)
1. `/Makefile` - Add UV targets (Task 2.1)
2. `/README.md` - Update installation (Task 2.2)
3. `/API_REFERENCE.md` - Update installation (Task 2.3)
4. `/examples/README.md` - Update setup (Task 2.4)
5. `/.github/workflows/test.yml` - Add UV workflow (Task 3.1)
6. `/.github/workflows/publish.yml` - Use uv build (Task 3.2)
7. `/.envrc` - UV integration (Task 4.2)

### Files to Create (2+)
1. `/.python-version` - Python version spec (Task 1.1)
2. `/uv.lock` - Lock file (Task 3.4)
3. `/CONTRIBUTING.md` - Migration guide (Task 4.3) [if doesn't exist]

### Files Unchanged
- All source code in `replicated/`
- All test code in `tests/`
- All example scripts in `examples/`
- `pyproject.toml` (works as-is with UV)

## Next Steps

1. **Review this plan** with the team
2. **Start Phase 1** with Task 1.1 (Create .python-version)
3. **Complete Phase 1** validation tasks before proceeding
4. **Proceed phase-by-phase** with checkpoints
5. **Monitor and adjust** based on findings

## Related Documents

- **Research**: [UV Migration Analysis](./research/uv-migration-analysis.md) (2025-10-14)
- **Repository**: replicatedhq/replicated-python
- **Branch**: chore/crdant/converts-to-uv

## Approval and Sign-off

**Plan Status**: Approved (no formal proposal required per proposal-needed agent)
**Rationale**: Low-risk, reversible, developer-tooling change with zero breaking changes
**Approved By**: Based on automated proposal-needed analysis (2025-10-15)

---

*This plan was generated by Claude Code based on comprehensive codebase research. It provides a detailed, phased approach to UV migration with clear checkpoints, validation criteria, and rollback options at every stage.*
