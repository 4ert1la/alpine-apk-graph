"""Тесты генерации PlantUML без сетевых запросов."""

import unittest

from src.visualize import plantuml_encode, plantuml_text


class VisualizeTests(unittest.TestCase):
    """Проверки текстового формата и кодирования."""

    def test_plantuml_content(self):
        """PlantUML содержит заголовок, узлы, ребро и конец."""
        text = plantuml_text({"A": {"B"}, "B": set()})
        self.assertIn("@startuml", text)
        self.assertIn('rectangle "A" as node_0', text)
        self.assertIn("node_0 --> node_1", text)
        self.assertIn("@enduml", text)

    def test_encode_is_nonempty(self):
        """Кодирование PlantUML возвращает строку."""
        self.assertTrue(plantuml_encode("@startuml\n@enduml\n"))


if __name__ == "__main__":
    unittest.main()
