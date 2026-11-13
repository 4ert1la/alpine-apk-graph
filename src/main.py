"""Тонкая точка входа CLI."""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import sys


def _load_graph(config):
    """Загрузить граф из тестового файла или APKINDEX."""
    if config.test_mode:
        from src.test_repo import load_test_graph
        return load_test_graph(config.repo), None
    from src.apk_repo import load_repository
    records, graph = load_repository(config.repo)
    return graph, records


def _check_root(config, graph, records):
    """Проверить наличие корневого пакета и его версию."""
    if config.package not in graph:
        raise ValueError(f"Пакет '{config.package}' отсутствует в репозитории.")
    if config.version and records:
        actual = records[config.package].version
        if actual != config.version:
            raise ValueError(
                f"Версия {actual} пакета {config.package} не совпадает "
                f"с {config.version}; укажите URL другой ветки репозитория."
            )


def _select_graph(config, graph):
    """Построить прямой или обратный ограниченный подграф."""
    if config.reverse:
        from src.reverse import reverse_dependencies
        traversal = reverse_dependencies(
            graph, config.package, config.max_depth, config.filter_text
        )
    else:
        from src.graph import breadth_first
        traversal = breadth_first(
            graph, config.package, config.max_depth, config.filter_text
        )
    from src.graph import induced_graph
    return induced_graph(
        __import__("src.reverse", fromlist=["reverse_graph"]).reverse_graph(
            graph
        ) if config.reverse else graph,
        traversal,
    )


def run(config):
    """Выполнить выбранный режим CLI."""
    if config.show_config:
        from src.config import config_lines
        print("\n".join(config_lines(config)))
        return 0
    graph, records = _load_graph(config)
    _check_root(config, graph, records)
    if config.show_direct:
        from src.graph import direct_dependencies
        direct = direct_dependencies(
            graph, config.package, config.filter_text
        )
        print("\n".join(direct) if direct else "(нет прямых зависимостей)")
        return 0
    selected = _select_graph(config, graph)
    from src.visualize import save_visualization
    save_visualization(selected, config.output)
    return 0


def main(argv=None):
    """Точка входа: обработать ошибки с кодом возврата 1."""
    from src.config import parse_args
    try:
        return run(parse_args(argv))
    except (ValueError, OSError) as exc:
        print(f"Ошибка: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
