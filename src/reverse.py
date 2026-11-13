"""Построение и обход обратного графа зависимостей."""

from src.graph import breadth_first


def reverse_graph(graph):
    """Построить граф, где ребро указывает на зависимый пакет."""
    reversed_graph = {name: set() for name in graph}
    for source, targets in graph.items():
        for target in targets:
            reversed_graph.setdefault(target, set()).add(source)
    return reversed_graph


def reverse_dependencies(graph, root, max_depth=3, filter_text=""):
    """Найти транзитивные пакеты, зависящие от root."""
    return breadth_first(
        reverse_graph(graph), root, max_depth, filter_text
    )
