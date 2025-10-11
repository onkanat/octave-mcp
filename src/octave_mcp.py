"""octave_mcp compatibility module.

This small shim ensures `import octave_mcp` works for the distribution named
`octave-mcp` (hyphenated). It exposes the package version and acts as a
lightweight namespace for consumers that expect `import octave_mcp`.
"""

__all__ = ["__version__"]

__version__ = "0.2.5"

# Re-export package-level attributes
try:
    from . import __version__ as _pkg_version  # type: ignore

    __version__ = _pkg_version
except Exception:
    # fallback; keep the shim version
    pass
