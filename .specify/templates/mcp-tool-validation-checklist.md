# MCP Tool Validation Checklist

**Purpose**: Validate MCP tools against Constitution Principle VI (MCP Protocol Integration)  
**Constitution Version**: 1.1.0  
**Last Updated**: 2025-10-13

This checklist ensures that all MCP tools comply with project standards for naming, documentation, testing, and integration.

---

## Pre-Implementation Checklist

### Tool Design

- [ ] Tool name follows `snake_case` convention
- [ ] Tool name is descriptive and action-oriented
- [ ] Tool purpose is clearly defined and scoped
- [ ] Tool fits existing naming patterns (e.g., `octave_*`, `admin_*`)
- [ ] Tool does not duplicate existing functionality

### Documentation Planning

- [ ] Tool description written (one sentence summary)
- [ ] All parameters identified with types
- [ ] Return value structure defined
- [ ] Usage examples planned
- [ ] LM Studio config impact assessed

---

## Implementation Checklist

### Code Structure

- [ ] Tool defined in `src/mcp_server.py` with `@mcp.tool()` decorator
- [ ] Tool name parameter matches planned name
- [ ] Tool description parameter is concise and clear
- [ ] All function parameters have type annotations
- [ ] All function parameters have `Annotated` descriptions
- [ ] Optional parameters have appropriate defaults
- [ ] Return type is clearly defined (usually `Dict[str, Any]`)

### Example

```python
@mcp.tool(
    name="feature_action",
    description="Brief description of what this tool does."
)
def tool_feature_action(
    required_param: Annotated[str, "Description of required parameter"],
    optional_param: Annotated[Optional[int], "Description (default: 100)"] = 100,
) -> Dict[str, Any]:
    # Implementation
    pass
```

### Error Handling

- [ ] Tool uses `MCPException` for error handling
- [ ] All error paths return ERROR_SCHEMA.md compliant format
- [ ] Error types are appropriate (runtime_error, timeout, validation_error, etc.)
- [ ] Resource violations include `resource_violation` block
- [ ] Error messages are user-friendly
- [ ] Errors include helpful `hint` field when applicable

### Service Integration

- [ ] Tool delegates to existing service layer (not duplicating logic)
- [ ] Service layer properly handles business logic
- [ ] Tool acts as thin adapter between MCP and service
- [ ] Configuration pulled from environment variables
- [ ] Resource limits applied consistently

---

## Documentation Checklist

### MCP Tools Reference (`docs/MCP_TOOLS.md`)

#### Turkish Documentation

- [ ] Tool added to TR documentation
- [ ] Tool name and description in Turkish
- [ ] Parameters documented with types and defaults
- [ ] Return value structure documented
- [ ] Usage example provided (JSON)
- [ ] Special notes or warnings included
- [ ] Related tools cross-referenced

#### English Documentation

- [ ] Tool added to EN documentation (`docs/en/MCP_TOOLS.md`)
- [ ] Translation accurate and complete
- [ ] Technical terms consistent with TR version
- [ ] Examples identical (with localized comments if needed)

### LM Studio Configuration

- [ ] Universal config updated in both docs (if env vars changed)
- [ ] Environment variables documented (`MCP_*` prefix)
- [ ] Default values specified
- [ ] Path configurations noted
- [ ] Config example tested in both script and module modes

---

## Testing Checklist

### Contract Tests

- [ ] Contract test file created: `tests/contract/test_mcp_[tool_name].py`
- [ ] Test verifies tool name is registered
- [ ] Test verifies parameter schema
- [ ] Test verifies return value schema
- [ ] Test verifies required parameters
- [ ] Test verifies optional parameters with defaults
- [ ] Test verifies error responses match ERROR_SCHEMA.md

### Example Contract Test Structure

```python
def test_tool_name_contract():
    """Contract test for [tool_name] MCP tool."""
    from src import mcp_server
    
    # Mock dependencies if needed
    # ...
    
    # Call tool
    result = mcp_server.tool_feature_action(
        required_param="value",
        optional_param=42
    )
    
    # Verify contract
    assert "expected_field" in result
    assert isinstance(result["expected_field"], ExpectedType)
    # ... more assertions
```

### Integration Tests

- [ ] Integration test covers tool in realistic scenario
- [ ] Test verifies tool interacts correctly with services
- [ ] Test verifies resource limits are enforced
- [ ] Test covers happy path
- [ ] Test covers error scenarios
- [ ] Test verifies logging behavior

### Unit Tests

- [ ] Service layer has unit tests (≥80% coverage)
- [ ] Edge cases covered
- [ ] Error conditions tested
- [ ] Resource limit violations tested

---

## LM Studio Integration Checklist

### Configuration Testing

- [ ] Tool tested via STDIO transport
- [ ] Tool tested with actual LM Studio (if available)
- [ ] Universal config works in script mode: `python src/mcp_server.py`
- [ ] Universal config works in module mode: `python -m mcp_server`
- [ ] Environment variables respected
- [ ] Paths resolve correctly (absolute/relative)

### User Experience

- [ ] Tool parameters clear for LLM consumption
- [ ] Tool description helps LLM choose when to use tool
- [ ] Return values are structured for LLM parsing
- [ ] Error messages are actionable
- [ ] Examples in docs match real usage

---

## CI/CD Integration Checklist

### Pipeline Updates

- [ ] Contract tests run in CI
- [ ] Integration tests run in CI (if not too slow)
- [ ] Coverage includes new tool and service code
- [ ] No regression in existing tool tests
- [ ] OpenAPI artifact generation still works (for HTTP API)

---

## Pre-Merge Review Checklist

### Code Quality

- [ ] Code follows project style (Black, isort)
- [ ] No linting errors
- [ ] Type hints complete and accurate
- [ ] Docstrings present (if applicable)
- [ ] No hardcoded values (use config)
- [ ] No `sys.path` manipulation (Principle IX)

### Constitution Compliance

- [ ] Principle I: Tool is modular and independent ✓
- [ ] Principle II: CLI/API access if applicable ✓
- [ ] Principle III: Tests written first (TDD) ✓
- [ ] Principle IV: Contract tests present ✓
- [ ] Principle V: Structured logging added ✓
- [ ] Principle VI: MCP protocol standards followed ✓
- [ ] Principle VII: ERROR_SCHEMA.md compliance ✓
- [ ] Principle VIII: Bilingual docs complete ✓
- [ ] Principle IX: Import path resolution clean ✓

### Documentation Review

- [ ] Both TR and EN docs updated
- [ ] API.md updated (if HTTP endpoint exists)
- [ ] MCP_TOOLS.md updated (both languages)
- [ ] CHANGELOG.md entry added
- [ ] Migration guide written (if breaking change)

### Testing Verification

- [ ] All tests pass locally
- [ ] Coverage threshold met (≥80% for core)
- [ ] No flaky tests introduced
- [ ] Contract tests comprehensive
- [ ] Integration tests stable

---

## Post-Merge Checklist

### Deployment Verification

- [ ] Tool works in deployed environment
- [ ] LM Studio config verified by users
- [ ] No production errors reported
- [ ] Monitoring/logging shows expected behavior

### Documentation Publication

- [ ] GitHub Pages updated with new docs
- [ ] TR docs live and accessible
- [ ] EN docs live and accessible
- [ ] Links working (cross-references)

---

## Common Issues and Solutions

### Issue: Tool not appearing in LM Studio

**Solution**: Check STDIO transport is working, verify tool is registered with `@mcp.tool()`, restart LM Studio.

### Issue: Type errors in tool parameters

**Solution**: Ensure all parameters have `Annotated[Type, "Description"]`, check FastMCP version compatibility.

### Issue: Import errors in module mode

**Solution**: Verify package structure, check `pyproject.toml` entry points, avoid `sys.path` manipulation.

### Issue: Error schema not matching

**Solution**: Use `MCPException` base class, ensure error block has all required fields (id, type, message, timestamp).

### Issue: Tests failing in CI but passing locally

**Solution**: Check environment variables are set in CI, verify paths are absolute, check for timing issues.

---

## Quick Reference: MCP Tool Anatomy

```python
from typing import Annotated, Any, Dict, Optional
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("app_name")

@mcp.tool(
    name="tool_name",              # snake_case, descriptive
    description="What it does."    # One sentence, clear
)
def tool_tool_name(
    required: Annotated[str, "Param description"],
    optional: Annotated[Optional[int], "With default"] = 100,
) -> Dict[str, Any]:
    """
    Detailed docstring if needed.
    
    Args:
        required: More details
        optional: More details
        
    Returns:
        Dict with expected structure
    """
    try:
        # Delegate to service layer
        result = service.do_work(required, optional)
        return result
    except SomeError as e:
        # Use MCPException with ERROR_SCHEMA.md format
        raise MCPException(
            message="User-friendly error",
            error_type="runtime_error",
            details={"context": "more info"}
        )
```

---

**Version History**

- **v1.0.0** (2025-10-13): Initial MCP tool validation checklist aligned with Constitution v1.1.0
