"""Тесты валидации параметров CLI."""

import tempfile
import unittest
from pathlib import Path

from src.config import (
    parse_args, validate_depth, validate_output, validate_package,
    validate_repo, validate_version,
)


class ConfigTests(unittest.TestCase):
    """Проверки валидаторов и сборки Config."""

    def test_empty_package(self):
        """Пустое имя пакета отклоняется."""
        with self.assertRaises(ValueError):
            validate_package("")

    def test_invalid_package(self):
        """Недопустимые символы в имени отклоняются."""
        with self.assertRaises(ValueError):
            validate_package("bad/name")

    def test_invalid_url(self):
        """HTTP URL вместо HTTPS отклоняется."""
        with self.assertRaises(ValueError):
            validate_repo("http://example.org/alpine/", False)

    def test_missing_test_file(self):
        """Несуществующий файл тестового графа отклоняется."""
        with self.assertRaises(ValueError):
            validate_repo("/no/such/graph.txt", True)

    def test_bad_depth(self):
        """Нечисловая глубина отклоняется."""
        with self.assertRaises(ValueError):
            validate_depth("abc")

    def test_negative_depth(self):
        """Отрицательная глубина отклоняется."""
        with self.assertRaises(ValueError):
            validate_depth("-1")

    def test_bad_output(self):
        """Расширение, отличное от SVG, отклоняется."""
        with self.assertRaises(ValueError):
            validate_output("graph.png")

    def test_bad_version(self):
        """Версия с пробелами отклоняется."""
        with self.assertRaises(ValueError):
            validate_version("1.0 beta")

    def test_parse_args(self):
        """Парсер собирает конфигурацию из опций."""
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "graph.txt"
            path.write_text("A: B\n", encoding="utf-8")
            config = parse_args([
                "--package", "A", "--repo", str(path), "--test-mode"
            ])
            self.assertEqual(config.package, "A")
            self.assertEqual(config.max_depth, 3)


if __name__ == "__main__":
    unittest.main()
