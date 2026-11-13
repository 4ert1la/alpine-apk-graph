"""Алгоритмы обхода графа зависимостей."""

from dataclasses import dataclass


@dataclass
class Traversal:
    """Результат ограниченного BFS: узлы и рёбра обхода."""

    nodes: set[str]
    edges: set[tuple[str, str]]
    depths: dict[str, int]


def breadth_first(graph, root, max_depth=3, filter_text=""):
    """Обойти граф рекурсивным BFS с ограничением глубины."""
    if root not in graph:
        raise ValueError(f"Пакет '{root}' не найден в графе.")
    if filter_text and filter_text in root:
        raise ValueError("Корневой пакет исключён параметром --filter.")
    result = Traversal({root}, set(), {root: 0})
    return _visit_frontier(
        graph, [root], result, max_depth, filter_text
    )


def _visit_frontier(graph, frontier, result, max_depth, filter_text):
    """Обработать фронт BFS и рекурсивно перейти к следующему."""
    if not frontier:
        return result
    next_frontier = []
    for source in frontier:
        depth = result.depths[source]
        if depth >= max_depth:
            continue
        for target in sorted(graph.get(source, set())):
            if filter_text and filter_text in target:
                continue
            result.edges.add((source, target))
            if target in result.nodes:
                continue
            result.nodes.add(target)
            result.depths[target] = depth + 1
            next_frontier.append(target)
    return _visit_frontier(
        graph, next_frontier, result, max_depth, filter_text
    )


def induced_graph(graph, traversal):
    """Оставить в графе только найденные узлы и рёбра."""
    return {
        node: {
            target for target in graph.get(node, set())
            if (node, target) in traversal.edges
        }
        for node in traversal.nodes
    }


def direct_dependencies(graph, root, filter_text=""):
    """Вернуть отсортированные прямые зависимости корневого пакета."""
    if root not in graph:
        raise ValueError(f"Пакет '{root}' не найден в графе.")
    return sorted(
        target for target in graph[root]
        if not filter_text or filter_text not in target
    )


def edge_list(graph):
    """Преобразовать dict смежности в отсортированный список рёбер."""
    return sorted(
        (source, target)
        for source, targets in graph.items()
        for target in targets
    )
