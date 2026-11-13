"""Генерация PlantUML и получение SVG через публичный сервер."""

import base64
import urllib.error
import urllib.request
import zlib
from pathlib import Path

PLANTUML_ALPHABET = (
    "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-_"
)
SERVER_URL = "https://www.plantuml.com/plantuml/svg/"
TIMEOUT = 20


def plantuml_text(graph):
    """Сформировать PlantUML с прямоугольниками и направленными рёбрами."""
    nodes = sorted(set(graph) | {
        target for targets in graph.values() for target in targets
    })
    lines = ["@startuml", "left to right direction"]
    aliases = {node: f"node_{index}" for index, node in enumerate(nodes)}
    for node in nodes:
        safe = node.replace('"', "'")
        lines.append(f'rectangle "{safe}" as {aliases[node]}')
    for source in sorted(graph):
        for target in sorted(graph[source]):
            lines.append(
                f"{aliases[source]} --> {aliases[target]}"
            )
    lines.append("@enduml")
    return "\n".join(lines) + "\n"


def _encode_triplet(first, second, third):
    """Закодировать три байта алфавитом PlantUML."""
    value = (first << 16) | (second << 8) | third
    return "".join(
        PLANTUML_ALPHABET[(value >> shift) & 0x3F]
        for shift in (18, 12, 6, 0)
    )


def plantuml_encode(text):
    """Закодировать PlantUML через raw deflate и base64-алфавит."""
    compressor = zlib.compressobj(level=9, wbits=-15)
    payload = compressor.compress(text.encode("utf-8")) + compressor.flush()
    result = []
    for index in range(0, len(payload), 3):
        chunk = payload[index:index + 3]
        padded = chunk + bytes(3 - len(chunk))
        result.append(_encode_triplet(*padded))
    return "".join(result)


def plantuml_url(text):
    """Получить URL запроса SVG к публичному серверу PlantUML."""
    return SERVER_URL + plantuml_encode(text)


def request_svg(text):
    """Запросить SVG у PlantUML; вернуть None при сетевой ошибке."""
    urls = [plantuml_url(text), SERVER_URL + "~h" + text.encode().hex()]
    for url in urls:
        try:
            request = urllib.request.Request(
                url, headers={"User-Agent": "apk-dependency-graph/1.0"}
            )
            with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
                data = response.read()
            if b"<svg" in data[:1000]:
                return data
        except (urllib.error.URLError, TimeoutError, OSError):
            continue
    return None


def save_visualization(graph, output):
    """Напечатать PlantUML, сохранить .puml и попытаться получить SVG."""
    text = plantuml_text(graph)
    output_path = Path(output)
    puml_path = output_path.with_suffix(".puml")
    puml_path.write_text(text, encoding="utf-8")
    print(text, end="")
    svg = request_svg(text)
    if svg is None:
        print(
            "Предупреждение: PlantUML-сервер недоступен; "
            f"сохранён исходник {puml_path}."
        )
        return False
    output_path.write_bytes(svg)
    return True
