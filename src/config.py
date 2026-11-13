"""Разбор и валидация параметров командной строки."""

import argparse
import re
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse

DEFAULT_OUTPUT = "graph.svg"
DEFAULT_DEPTH = 3
MIN_DEPTH = 0
MAX_TIMEOUT = 30
VERSION_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._+~:-]*$")
PACKAGE_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9+_.-]*$")


@dataclass
class Config:
    """Все настройки CLI в одном объекте."""

    package: str
    repo: str
    test_mode: bool
    version: str | None
    output: str
    max_depth: int
    filter_text: str
    show_config: bool
    show_direct: bool
    reverse: bool


def build_parser():
    """Создать парсер аргументов CLI."""
    parser = argparse.ArgumentParser(
        description="Визуализация зависимостей пакетов Alpine APK."
    )
    parser.add_argument("--package", default="alpine-base")
    parser.add_argument("--repo", default="")
    parser.add_argument("--test-mode", action="store_true")
    parser.add_argument("--version")
    parser.add_argument("--output", default=DEFAULT_OUTPUT)
    parser.add_argument("--max-depth", default=str(DEFAULT_DEPTH))
    parser.add_argument("--filter", dest="filter_text", default="")
    parser.add_argument("--show-config", action="store_true")
    parser.add_argument("--show-direct", action="store_true")
    parser.add_argument("--reverse", action="store_true")
    return parser


def validate_package(value):
    """Проверить имя пакета."""
    if not value or not PACKAGE_RE.fullmatch(value):
        raise ValueError("Параметр --package: укажите корректное имя пакета.")
    return value


def validate_repo(value, test_mode):
    """Проверить путь тестового графа или URL репозитория."""
    if not value:
        raise ValueError("Параметр --repo обязателен и не может быть пустым.")
    if test_mode:
        path = Path(value).expanduser()
        if not path.is_file():
            raise ValueError(f"Параметр --repo: файл не найден: {value}")
        return str(path)
    parsed = urlparse(value)
    if parsed.scheme != "https" or not parsed.netloc:
        raise ValueError(
            "Параметр --repo: нужен корректный HTTPS URL Alpine."
        )
    if parsed.query or parsed.fragment:
        raise ValueError("Параметр --repo: query и fragment не допускаются.")
    return value


def validate_version(value):
    """Проверить необязательную версию пакета."""
    if value is not None and not VERSION_RE.fullmatch(value):
        raise ValueError("Параметр --version: некорректный формат версии.")
    return value


def validate_output(value):
    """Проверить имя выходного SVG-файла."""
    if not value or Path(value).suffix.lower() != ".svg":
        raise ValueError("Параметр --output должен иметь расширение .svg.")
    if Path(value).name in {"", ".", ".."}:
        raise ValueError("Параметр --output: некорректное имя файла.")
    return value


def validate_depth(value):
    """Преобразовать глубину и запретить отрицательные значения."""
    try:
        depth = int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError("--max-depth должен быть целым числом.") from exc
    if depth < MIN_DEPTH:
        raise ValueError("--max-depth не может быть отрицательным.")
    return depth


def parse_args(argv=None):
    """Разобрать CLI и вернуть валидированный Config."""
    args = build_parser().parse_args(argv)
    config = Config(
        package=validate_package(args.package),
        repo=(
            "" if args.show_config and not args.repo
            else validate_repo(args.repo, args.test_mode)
        ),
        test_mode=args.test_mode,
        version=validate_version(args.version),
        output=validate_output(args.output),
        max_depth=validate_depth(args.max_depth),
        filter_text=args.filter_text,
        show_config=args.show_config,
        show_direct=args.show_direct,
        reverse=args.reverse,
    )
    if config.filter_text == "":
        config.filter_text = ""
    return config


def config_lines(config):
    """Вернуть параметры конфигурации в формате ключ-значение."""
    return [
        f"{key}={value}"
        for key, value in vars(config).items()
    ]
