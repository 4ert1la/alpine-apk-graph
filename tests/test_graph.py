"""Тесты прямого и обратного обхода графа."""

import unittest

from src.graph import breadth_first, direct_dependencies, induced_graph
from src.reverse import reverse_dependencies, reverse_graph


class GraphTests(unittest.TestCase):
    """Проверки BFS, глубины, фильтра и циклов."""

    def test_diamond(self):
        """Ромбовидный граф посещает общий узел один раз."""
        graph = {"A": {"B", "C"}, "B": {"D"}, "C": {"D"}, "D": set()}
        result = breadth_first(graph, "A", 3)
        self.assertEqual(result.nodes, {"A", "B", "C", "D"})
        self.assertEqual(result.depths["D"], 2)

    def test_depth_limit(self):
        """Глубина 1 включает только прямых соседей."""
        graph = {"A": {"B"}, "B": {"C"}, "C": set()}
        result = breadth_first(graph, "A", 1)
        self.assertEqual(result.nodes, {"A", "B"})
        self.assertEqual(result.edges, {("A", "B")})

    def test_cycle(self):
        """Цикл не приводит к повторному обходу."""
        graph = {"A": {"B"}, "B": {"C"}, "C": {"A"}}
        result = breadth_first(graph, "A", 10)
        self.assertEqual(result.nodes, {"A", "B", "C"})

    def test_filter(self):
        """Узлы с фильтруемой подстрокой исключаются."""
        graph = {"A": {"B", "TESTLIB"}, "B": set(), "TESTLIB": set()}
        result = breadth_first(graph, "A", 3, "TEST")
        self.assertNotIn("TESTLIB", result.nodes)

    def test_direct(self):
        """Прямые зависимости возвращаются отдельно."""
        self.assertEqual(
            direct_dependencies({"A": {"B", "C"}}, "A"), ["B", "C"]
        )

    def test_reverse_edges(self):
        """Рёбра обратного графа имеют противоположное направление."""
        reversed_graph = reverse_graph({"A": {"B"}, "B": set()})
        self.assertEqual(reversed_graph["B"], {"A"})

    def test_reverse_transitive(self):
        """Обратный BFS находит транзитивных зависимых."""
        graph = {"A": {"B"}, "B": {"C"}, "C": set()}
        result = reverse_dependencies(graph, "C", 2)
        self.assertEqual(result.nodes, {"A", "B", "C"})

    def test_induced_graph(self):
        """Подграф содержит только посещённые рёбра."""
        graph = {"A": {"B", "C"}, "B": set(), "C": set()}
        result = breadth_first(graph, "A", 1, "C")
        self.assertEqual(
            induced_graph(graph, result), {"A": {"B"}, "B": set()}
        )


if __name__ == "__main__":
    unittest.main()
