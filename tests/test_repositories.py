"""Тесты разбора APKINDEX и тестового графа."""

import tempfile
import unittest
from pathlib import Path

from src.apk_repo import build_package_graph, parse_index, parse_record
from src.test_repo import load_test_graph, parse_graph_text


class RepositoryTests(unittest.TestCase):
    """Офлайн-проверки парсеров источников графа."""

    def test_parse_apk_record(self):
        """Одна запись APKINDEX разбирается по полям."""
        record = parse_record(
            "P:curl\nV:8.8-r0\nD:ca-certificates libcurl>=8\n"
        )
        self.assertEqual(record.name, "curl")
        self.assertEqual(record.version, "8.8-r0")
        self.assertEqual(record.dependencies, ["ca-certificates", "libcurl>=8"])

    def test_parse_apk_index(self):
        """Несколько записей APKINDEX разделяются пустой строкой."""
        text = "P:a\nV:1\nD:b\n\nP:b\nV:2\n"
        records = parse_index(text)
        self.assertEqual(set(records), {"a", "b"})

    def test_virtual_provides(self):
        """Виртуальная зависимость разрешается через provides."""
        records = parse_index(
            "P:provider\nV:1\np:so:libx.so.1\n\n"
            "P:consumer\nV:1\nD:so:libx.so.1\n"
        )
        graph = build_package_graph(records)
        self.assertEqual(graph["consumer"], {"provider"})

    def test_parse_test_graph(self):
        """Тестовый граф создаёт также узлы без исходящих рёбер."""
        graph = parse_graph_text("A: B C\nB: D\n")
        self.assertEqual(graph["A"], {"B", "C"})
        self.assertEqual(graph["D"], set())

    def test_lowercase_line_error(self):
        """Строка с lowercase выдаёт ошибку с номером."""
        with self.assertRaisesRegex(ValueError, "Строка 2"):
            parse_graph_text("A: B\nb: C\n")

    def test_load_test_file(self):
        """Файл тестового графа читается в UTF-8."""
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "g.txt"
            path.write_text("A: B\n", encoding="utf-8")
            self.assertEqual(load_test_graph(path)["A"], {"B"})


if __name__ == "__main__":
    unittest.main()
