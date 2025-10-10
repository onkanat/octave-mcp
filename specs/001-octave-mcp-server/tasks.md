# Tasks: Octave MCP Server

**Input**: Design documents from `/specs/001-octave-mcp-server/`
**Prerequisites**: plan.md (required), research.md, data-model.md, contracts/

## Execution Flow (main)
```
1. Load plan.md from feature directory
   → Extract: tech stack, libraries, structure
2. Load optional design documents:
   → data-model.md: Extract entities → model tasks
   → contracts/: Each file → contract test task
   → research.md: Extract decisions → setup tasks
3. Generate tasks by category:
   → Setup: project init, dependencies, linting
   → Tests: contract tests, integration tests
   → Core: models, services, CLI commands
   → Integration: DB, middleware, logging
   → Polish: unit tests, performance, docs
4. Apply task rules:
   → Different files = mark [P] for parallel
   → Same file = sequential (no [P])
   → Tests before implementation (TDD)
5. Number tasks sequentially (T001, T002...)
6. Generate dependency graph
7. Create parallel execution examples
8. Validate task completeness:
   → All contracts have tests?
   → All entities have models?
   → All endpoints implemented?
9. Return: SUCCESS (tasks ready for execution)
```

## Format: `[ID] [P?] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- Include exact file paths in descriptions

---

## Phase 3.1: Setup
- [ ] T001 Create project structure per plan.md (src/, tests/, scripts/, etc.)
- [ ] T002 Initialize Python 3.11+ project with FastAPI and GNU Octave dependencies
- [ ] T003 [P] Configure linting and formatting tools (e.g., black, flake8, isort)
- [ ] T004 [P] Add .env and config templates for resource limits and session management

## Phase 3.2: Tests First (TDD) ⚠️ MUST COMPLETE BEFORE 3.3
- [ ] T005 [P] Contract test: POST /run_octave in tests/contract/test_run_octave_post.py
- [ ] T006 [P] Contract test: POST /publish in tests/contract/test_publish_post.py
- [ ] T007 [P] Contract test: POST /grabcode in tests/contract/test_grabcode_post.py
- [ ] T008 [P] Integration test: persistent session flow in tests/integration/test_persistent_session.py
- [ ] T009 [P] Integration test: resource limit enforcement in tests/integration/test_resource_limits.py
- [ ] T010 [P] Integration test: error reporting format in tests/integration/test_error_reporting.py
- [ ] T011 [P] Integration test: publish/grabcode concurrency in tests/integration/test_publish_grabcode_concurrency.py

## Phase 3.3: Core Implementation (ONLY after tests are failing)
- [ ] T012 [P] Implement Session model in src/models/session.py
- [ ] T013 [P] Implement Run model in src/models/run.py
- [ ] T014 [P] Implement Publish model in src/models/publish.py
- [ ] T015 [P] Implement Grabcode model in src/models/grabcode.py
- [ ] T016 [P] Implement session management logic in src/services/session_service.py
- [ ] T017 [P] Implement Octave runner logic in src/services/octave_runner.py
- [ ] T018 [P] Implement publish logic in src/services/publish_service.py
- [ ] T019 [P] Implement grabcode logic in src/services/grabcode_service.py
- [ ] T020 [P] Implement FastAPI endpoints: /run_octave, /publish, /grabcode in src/api/endpoints.py
- [ ] T021 [P] Implement CLI commands: run, publish, grabcode in src/cli/cli.py
- [ ] T022 [P] Implement error reporting utility in src/utils/error_format.py
- [ ] T023 [P] Implement resource limit enforcement in src/utils/resource_limits.py
- [ ] T024 [P] Implement vectorization enforcement in src/utils/vectorization.py
- [ ] T025 [P] Implement logging and observability in src/utils/logging.py

## Phase 3.4: Integration & Polish
- [ ] T026 [P] Integrate session persistence and cleanup in src/services/session_service.py
- [ ] T027 [P] Integrate API rate limiting and retention policy in src/api/middleware.py
- [ ] T028 [P] Add smoke_test.py for end-to-end validation in tests/smoke_test.py
- [ ] T029 [P] Add documentation: setup, usage, API, CLI in docs/
- [ ] T030 [P] Add versioning and changelog in CHANGELOG.md

---

## Dependency Graph
- T001 → T002 → (T003, T004)
- (T003, T004) → (T005-T011) [all tests in parallel]
- (T005-T011) → (T012-T025) [all core impl. in parallel]
- (T012-T025) → (T026-T030) [integration/polish in parallel]

## Parallel Execution Examples
- T003, T004: Linting/config setup can run in parallel
- T005-T011: All contract/integration tests can be written in parallel
- T012-T025: All models/services/utils can be implemented in parallel after tests
- T026-T030: Integration, docs, and polish tasks can be parallelized

## Completeness Validation
- [x] All contract endpoints have tests
- [x] All entities have models
- [x] All endpoints are implemented
- [x] TDD enforced: tests before implementation
- [x] Constitution and plan.md requirements mapped to tasks

---

# SUCCESS: tasks.md ready for execution
