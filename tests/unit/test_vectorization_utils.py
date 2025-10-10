import os
import sys

from utils.vectorization import analyze_vectorization

sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../src")))


def test_analyze_vectorization_detects_for_loop():
    code = """
for i in range(10):
    print(i)
"""
    issues = analyze_vectorization(code)
    assert isinstance(issues, list)
    assert any("Döngü tespit edildi" in i.get("message", "") for i in issues)


def test_analyze_vectorization_handles_syntax_error():
    code = "for i in range(10)"
    issues = analyze_vectorization(code)
    assert issues == []
