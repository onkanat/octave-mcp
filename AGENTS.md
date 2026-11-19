# AGENTS.md

## Build/Lint/Test Commands

### Testing
- `pytest` - Run all tests with coverage (90% minimum required)
- `pytest tests/unit/test_specific.py` - Run single test file
- `pytest -m unit` - Run unit tests only
- `pytest -m integration` - Run integration tests only
- `pytest -m contract` - Run contract tests only
- `pytest -m "not slow"` - Skip slow tests

### Code Quality
- `black .` - Format code (99 character line length)
- `isort .` - Sort imports (black profile)
- `flake8` - Lint code (99 character max line length)
- `mypy src/` - Type checking with strict mode
- `coverage report` - View coverage report
- `coverage html` - Generate HTML coverage report

## Code Style Guidelines

### General
- Python 3.11+ with strict type hints required
- Use Black formatter with 99 character line length
- Import sorting with isort (black profile)
- Domain-driven design with clear separation of concerns

### Imports & Structure
- Absolute imports from `src` package preferred
- Group imports: standard library, third-party, local
- Use `from pathlib import Path` for file operations
- Async/await patterns throughout services layer

### Models & Types
- Pydantic models for all entities with Field descriptions
- Use Optional[T] for nullable fields
- Custom validators in Pydantic models
- Strict type checking with mypy

### Error Handling
- Custom exceptions from `src.exceptions` module
- Comprehensive error logging with structured messages
- MCPException handler for standardized HTTP errors
- Validation errors use Pydantic ValidationError

### Testing
- Test markers: unit, integration, contract, slow, external
- Use pytest fixtures for setup/teardown
- Mock external dependencies with unittest.mock
- Coverage minimum 90% enforced

### Naming Conventions
- Classes: PascalCase (Session, ResourceLimits, OctaveService)
- Functions/variables: snake_case
- Constants: UPPER_SNAKE_CASE
- Private methods: prefix with underscore

### Documentation
- Docstrings for all modules, classes, and public methods
- Field descriptions in Pydantic models
- Type hints required for all function parameters and returns