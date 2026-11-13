"""Загрузка простого графа из текстового файла."""

import re
from pathlib import Path

NAME_RE = re.compile(r"^[A-Z]+$")


def parse_graph_text(text):
    """Разобрать строки вида 'A: B C' в dict смежности."""
    graph = {}
    for line_number, raw_line in enumerate(text.splitlines(), 1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.count(":") != 1:
            raise ValueError(f"Строка {line_number}: ожидается формат A: B C.")
        source, targets_text = (part.strip() for part in line.split(":"))
        targets = targets_text.split() if targets_text else []
        names = [source, *targets]
        if any(not NAME_RE.fullmatch(name) for name in names):
            raise ValueError(
                f"Строка {line_number}: имена должны быть [A-Z]+."
            )
        graph.setdefault(source, set()).update(targets)
        for target in targets:
            graph.setdefault(target, set())
    return graph


def load_test_graph(path):
    """Прочитать и разобрать тестовый граф из файла."""
    return parse_graph_text(Path(path).read_text(encoding="utf-8"))
