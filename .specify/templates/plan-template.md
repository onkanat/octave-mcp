# Implementation Plan: [FEATURE]

**Branch**: `[###-feature-name]` | **Date**: [DATE] | **Spec**: [link]
**Input**: Feature specification from `/specs/[###-feature-name]/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

[Extract from feature spec: primary requirement + technical approach from research]

## Technical Context

<!--
  ACTION REQUIRED: Replace the content in this section with the technical details
  for the project. The structure here is presented in advisory capacity to guide
  the iteration process.
-->

**Language/Version**: [e.g., Python 3.11, Swift 5.9, Rust 1.75 or NEEDS CLARIFICATION]  
**Primary Dependencies**: [e.g., FastAPI, UIKit, LLVM or NEEDS CLARIFICATION]  
**Storage**: [if applicable, e.g., PostgreSQL, CoreData, files or N/A]  
**Testing**: [e.g., pytest, XCTest, cargo test or NEEDS CLARIFICATION]  
**Target Platform**: [e.g., Linux server, iOS 15+, WASM or NEEDS CLARIFICATION]
**Project Type**: [single/web/mobile - determines source structure]  
**Performance Goals**: [domain-specific, e.g., 1000 req/s, 10k lines/sec, 60 fps or NEEDS CLARIFICATION]  
**Constraints**: [domain-specific, e.g., <200ms p95, <100MB memory, offline-capable or NEEDS CLARIFICATION]  
**Scale/Scope**: [domain-specific, e.g., 10k users, 1M LOC, 50 screens or NEEDS CLARIFICATION]

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Constitution Version**: 1.1.0 (Last updated: 2025-10-13)

### Core Principles Compliance

- [ ] **I. Modularity**: Feature designed as independent, testable module?
- [ ] **II. CLI & API**: Both interfaces planned (if applicable)?
- [ ] **III. Test-First (TDD)**: Tests will be written first, RED-GREEN-REFACTOR?
- [ ] **IV. Integration & Contract Tests**: API/MCP tool contracts defined?
- [ ] **V. Observability & Versioning**: Logging strategy, semantic versioning?
- [ ] **VI. MCP Protocol**: Core feature exposed as MCP tool (if applicable)?
- [ ] **VII. Error Handling**: ERROR_SCHEMA.md compliance planned?
- [ ] **VIII. Bilingual Docs**: TR/EN documentation planned?
- [ ] **IX. Import Path**: Module/script execution modes supported?

### Detailed Gate Checks

#### MCP Protocol Integration (if feature adds/modifies MCP tools)

- [ ] Tool name follows snake_case convention (e.g., `octave_run`)
- [ ] Tool parameters have type annotations and descriptions
- [ ] LM Studio config example will be provided
- [ ] Contract test for MCP tool interface planned
- [ ] Transport modes (STDIO/SSE) considered

#### Error Handling

- [ ] All error paths will use MCPException with ERROR_SCHEMA.md format
- [ ] Error types identified (runtime_error, timeout, resource_violation, etc.)
- [ ] Resource violations will populate resource_violation block
- [ ] HTTP 4xx/5xx responses will include error block

#### Bilingual Documentation

- [ ] Feature documentation planned in both TR and EN
- [ ] API endpoint docs will exist in `docs/API.md` and `docs/en/API.md`
- [ ] Migration guide (if breaking changes) in both languages

#### Testing Strategy

- [ ] Unit tests: Coverage target ≥80% for core modules
- [ ] Integration tests: Critical flows identified
- [ ] Contract tests: API/MCP tool schemas validated
- [ ] CI/CD: Coverage tracking enabled

**Notes**: Document any principle violations with justification. Breaking changes require migration plan.

## Project Structure

### Documentation (this feature)

```
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)
<!--
  ACTION REQUIRED: Replace the placeholder tree below with the concrete layout
  for this feature. Delete unused options and expand the chosen structure with
  real paths (e.g., apps/admin, packages/something). The delivered plan must
  not include Option labels.
-->

```
# [REMOVE IF UNUSED] Option 1: Single project (DEFAULT)
src/
├── models/
├── services/
├── cli/
└── lib/

tests/
├── contract/
├── integration/
└── unit/

# [REMOVE IF UNUSED] Option 2: Web application (when "frontend" + "backend" detected)
backend/
├── src/
│   ├── models/
│   ├── services/
│   └── api/
└── tests/

frontend/
├── src/
│   ├── components/
│   ├── pages/
│   └── services/
└── tests/

# [REMOVE IF UNUSED] Option 3: Mobile + API (when "iOS/Android" detected)
api/
└── [same as backend above]

ios/ or android/
└── [platform-specific structure: feature modules, UI flows, platform tests]
```

**Structure Decision**: [Document the selected structure and reference the real
directories captured above]

## Complexity Tracking

*Fill ONLY if Constitution Check has violations that must be justified*

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |
