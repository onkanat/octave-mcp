"""octave_mcp compatibility module.

This small shim ensures `import octave_mcp` works for the distribution named
`octave-mcp` (hyphenated). It exposes the package version and acts as a
lightweight namespace for consumers that expect `import octave_mcp`.
"""

__all__ = ["__version__"]

__version__ = "0.2.2"
