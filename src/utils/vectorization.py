"""Modern vectorization analysis utilities for Octave/MATLAB code optimization hints."""

from __future__ import annotations

import ast
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


@dataclass
class VectorizationIssue:
    """Represents a vectorization improvement opportunity in code."""

    lineno: int
    col_offset: int
    message: str
    severity: str = "info"
    suggestion: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format for API responses."""
        return asdict(self)


class VectorizationAnalyzer(ast.NodeVisitor):
    """
    Advanced loop detection analyzer for vectorization guidance.

    Analyzes Python code for loops that could potentially benefit from
    vectorization when translated to Octave/MATLAB.

    Features:
    - Detects for/while loops with vectorization potential
    - Identifies array operations that could be optimized
    - Provides contextual suggestions for improvement
    - Assigns severity levels based on loop complexity
    """

    def __init__(self) -> None:
        self.issues: List[VectorizationIssue] = []
        self._nested_level = 0

    def visit_For(self, node: ast.For) -> None:
        """Analyze for loops for vectorization opportunities."""
        self._nested_level += 1

        severity = "warning" if self._nested_level > 1 else "info"
        message = self._analyze_for_loop(node)
        suggestion = self._get_for_loop_suggestion(node)

        self.issues.append(
            VectorizationIssue(
                lineno=node.lineno,
                col_offset=node.col_offset,
                message=message,
                severity=severity,
                suggestion=suggestion
            )
        )

        self.generic_visit(node)
        self._nested_level -= 1

    def visit_While(self, node: ast.While) -> None:
        """Analyze while loops for potential optimization."""
        self._nested_level += 1

        severity = "warning" if self._nested_level > 1 else "info"
        message = (
            "While döngüsü tespit edildi; vektörizasyon veya erken çıkış "
            "koşulunu değerlendirin."
        )
        suggestion = "Koşul sabit sayıda iterasyon içeriyorsa for döngüsüne çevirmeyi düşünün."

        self.issues.append(
            VectorizationIssue(
                lineno=node.lineno,
                col_offset=node.col_offset,
                message=message,
                severity=severity,
                suggestion=suggestion
            )
        )

        self.generic_visit(node)
        self._nested_level -= 1

    def visit_ListComp(self, node: ast.ListComp) -> None:
        """Analyze list comprehensions for vectorization hints."""
        message = "List comprehension tespit edildi; NumPy/array işlemleri daha hızlı olabilir."
        suggestion = "numpy.array() operations veya broadcasting kullanmayı düşünün."

        self.issues.append(
            VectorizationIssue(
                lineno=node.lineno,
                col_offset=node.col_offset,
                message=message,
                severity="info",
                suggestion=suggestion
            )
        )

        self.generic_visit(node)

    def _analyze_for_loop(self, node: ast.For) -> str:
        """Analyze specific for loop patterns."""
        if self._nested_level > 1:
            return (
                f"İç içe döngü (seviye {self._nested_level}) tespit edildi; "
                f"vektörizasyon için yüksek öncelik."
            )

        # Check if iterating over range
        if isinstance(node.iter, ast.Call) and isinstance(node.iter.func, ast.Name):
            if node.iter.func.id == "range":
                return "Range döngüsü tespit edildi; array işlemleri ile vektörize edilebilir."

        # Check if iterating over enumerate
        if isinstance(node.iter, ast.Call) and isinstance(node.iter.func, ast.Name):
            if node.iter.func.id == "enumerate":
                return "Enumerate döngüsü tespit edildi; index tabanlı array işlemleri düşünün."

        return "Döngü tespit edildi; mümkünse vektörize etmeyi düşünün."

    def _get_for_loop_suggestion(self, node: ast.For) -> str:
        """Generate specific suggestions for for loop optimization."""
        if self._nested_level > 1:
            return "İç içe döngüleri tek boyutlu array işlemlerine dönüştürmeyi düşünün."

        if isinstance(node.iter, ast.Call) and isinstance(node.iter.func, ast.Name):
            if node.iter.func.id == "range":
                return "range(n) yerine numpy.arange() veya direct array operations kullanın."
            elif node.iter.func.id == "enumerate":
                return "enumerate yerine numpy array indexing kullanmayı düşünün."

        return "Element-wise işlemler için broadcasting veya vectorized functions kullanın."


async def analyze_vectorization(code: str) -> List[Dict[str, Any]]:
    """
    Analyze code for vectorization opportunities.

    Args:
        code: Python code string to analyze

    Returns:
        List of dictionaries containing vectorization issues

    Raises:
        ValueError: If code cannot be parsed
    """
    if not code or not code.strip():
        return []

    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        logger.warning(f"Syntax error in code analysis: {e}")
        raise ValueError(f"Code syntax error: {e}")

    analyzer = VectorizationAnalyzer()
    analyzer.visit(tree)

    issues = [issue.to_dict() for issue in analyzer.issues]
    logger.info(f"Found {len(issues)} vectorization opportunities")

    return issues


class VectorizationChecker:
    """Advanced vectorization checking utilities."""

    @staticmethod
    async def check_vectorization_potential(code: str) -> bool:
        """
        Check if code has vectorization potential.

        Args:
            code: Code string to analyze

        Returns:
            True if vectorization opportunities exist
        """
        try:
            issues = await analyze_vectorization(code)
            return len(issues) > 0
        except ValueError:
            return False

    @staticmethod
    async def get_optimization_score(code: str) -> float:
        """
        Calculate optimization score based on vectorization opportunities.

        Args:
            code: Code string to analyze

        Returns:
            Score from 0.0 (no optimization needed) to 1.0 (high optimization potential)
        """
        try:
            issues = await analyze_vectorization(code)
            if not issues:
                return 0.0

            # Weight by severity
            severity_weights = {"info": 0.3, "warning": 0.7, "error": 1.0}
            total_weight = sum(
                severity_weights.get(issue.get("severity", "info"), 0.3)
                for issue in issues
            )

            # Normalize by code length (rough estimate)
            code_lines = len([line for line in code.split('\n') if line.strip()])
            normalized_score = min(total_weight / max(code_lines, 1), 1.0)

            return normalized_score
        except ValueError:
            return 0.0

    @staticmethod
    async def get_detailed_analysis(code: str) -> Dict[str, Any]:
        """
        Get comprehensive vectorization analysis.

        Args:
            code: Code string to analyze

        Returns:
            Detailed analysis including issues, score, and recommendations
        """
        try:
            issues = await analyze_vectorization(code)
            score = await VectorizationChecker.get_optimization_score(code)

            # Categorize issues
            by_severity = {}
            for issue in issues:
                severity = issue.get("severity", "info")
                if severity not in by_severity:
                    by_severity[severity] = []
                by_severity[severity].append(issue)

            return {
                "issues": issues,
                "optimization_score": score,
                "total_issues": len(issues),
                "by_severity": by_severity,
                "recommendations": _get_general_recommendations(issues)
            }
        except ValueError as e:
            return {
                "error": str(e),
                "issues": [],
                "optimization_score": 0.0,
                "total_issues": 0,
                "by_severity": {},
                "recommendations": []
            }


def _get_general_recommendations(issues: List[Dict[str, Any]]) -> List[str]:
    """Generate general optimization recommendations based on issues."""
    recommendations = []

    if not issues:
        recommendations.append("Kod zaten iyi optimize edilmiş görünüyor.")
        return recommendations

    # Count issue types
    loop_count = sum(1 for issue in issues if "döngü" in issue.get("message", "").lower())
    nested_count = sum(1 for issue in issues if "iç içe" in issue.get("message", "").lower())
    list_comp_count = sum(
        1 for issue in issues
        if "comprehension" in issue.get("message", "").lower()
    )

    if nested_count > 0:
        recommendations.append("İç içe döngüleri numpy broadcasting ile optimize edin.")

    if loop_count > 2:
        recommendations.append(
            "Çoklu döngüleri vectorized operations ile birleştirmeyi düşünün."
        )

    if list_comp_count > 0:
        recommendations.append(
            "List comprehensions yerine numpy array operations kullanın."
        )

    recommendations.append("Performans kritik kod bölümleri için profiling yapın.")

    return recommendations
