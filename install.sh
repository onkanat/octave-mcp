#!/bin/bash
set -e

echo "🐙 Installing OctaveMCP..."

# Check if pip is available
if ! command -v pip &> /dev/null; then
    echo "❌ pip is required but not installed. Please install Python and pip first."
    exit 1
fi

# Check if GNU Octave is available
if ! command -v octave &> /dev/null; then
    echo "⚠️  GNU Octave not found. Please install GNU Octave for code execution."
    echo "   macOS: brew install octave"
    echo "   Ubuntu: sudo apt-get install octave"
    echo "   Windows: https://octave.org/download"
    echo ""
fi

# Install the package
echo "📦 Installing octave-mcp package..."
pip install octave-mcp

echo "✅ OctaveMCP installed successfully!"
echo ""
echo "🚀 Usage:"
echo "   Run MCP server: octave-mcp"
echo "   Run with custom config: MCP_RUNS_ROOT=/custom/path octave-mcp"
echo ""
echo "📚 Documentation: https://hakankilicaslan.github.io/octave-mcp"
echo "🔧 LM Studio Setup: https://hakankilicaslan.github.io/octave-mcp/en/MCP_TOOLS.html"