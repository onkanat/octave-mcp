from __future__ import annotations

import ast
from typing import List


class VectorizationIssue:
    def __init__(self, lineno: int, col_offset: int, message: str) -> None:
        self.lineno = lineno
        self.col_offset = col_offset
        self.message = message

    def to_dict(self) -> dict:
        return {
            "lineno": self.lineno,
            "col": self.col_offset,
            "message": self.message,
        }


class VectorizationAnalyzer(ast.NodeVisitor):
    """
    Minimal döngü sezgisel analizörü. Amaç: Vektörizasyon rehberi için uyarı üretmek.
    - for/while döngülerini işaretler
    - potansiyel büyüklük sezgisi: range(N) / len(x)
    Not: Bu yalnızca Python modundaki kod için rehber niteliğindedir.
    """

    def __init__(self) -> None:
        self.issues: List[VectorizationIssue] = []

    def visit_For(self, node: ast.For) -> None:
        self.issues.append(
            VectorizationIssue(
                node.lineno,
                node.col_offset,
                "Döngü tespit edildi; mümkünse vektörize etmeyi düşünün.",
            )
        )
        self.generic_visit(node)

    def visit_While(self, node: ast.While) -> None:
        self.issues.append(
            VectorizationIssue(
                node.lineno,
                node.col_offset,
                "While döngüsü tespit edildi; vektörizasyon veya erken çıkış koşullarını değerlendirin.",
            )
        )
        self.generic_visit(node)


def analyze_vectorization(code: str) -> List[dict]:
    """Kod içindeki basit döngü kalıplarını raporlar."""
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return []
    analyzer = VectorizationAnalyzer()
    analyzer.visit(tree)
    return [i.to_dict() for i in analyzer.issues]


class VectorizationChecker:
    @staticmethod
    def check_vectorization(code: str) -> bool:
        # TODO: Kodda gereksiz döngü var mı kontrol et
        raise NotImplementedError()
