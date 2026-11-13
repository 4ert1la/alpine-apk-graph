"""Получение и ручной разбор APKINDEX Alpine Linux."""

import gzip
import io
import tarfile
import urllib.error
import urllib.request
from dataclasses import dataclass

TIMEOUT = 20
USER_AGENT = "apk-dependency-graph/1.0"


@dataclass
class PackageRecord:
    """Запись пакета из APKINDEX."""

    name: str
    version: str
    dependencies: list[str]
    provides: list[str]


def download_index(repo):
    """Скачать APKINDEX.tar.gz по URL файла или каталога."""
    url = repo
    if not url.endswith("APKINDEX.tar.gz"):
        url = url.rstrip("/") + "/APKINDEX.tar.gz"
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
            return response.read()
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        raise ValueError(f"Не удалось загрузить APKINDEX: {exc}") from exc


def extract_index(payload):
    """Извлечь текст APKINDEX из gzip tar-архива."""
    try:
        with tarfile.open(fileobj=io.BytesIO(payload), mode="r:gz") as archive:
            member = next(
                (item for item in archive.getmembers()
                 if item.name.endswith("APKINDEX")), None
            )
            if member is None:
                raise ValueError("В архиве отсутствует APKINDEX.")
            stream = archive.extractfile(member)
            if stream is None:
                raise ValueError("Не удалось прочитать APKINDEX.")
            return stream.read().decode("utf-8", errors="replace")
    except (tarfile.TarError, OSError) as exc:
        raise ValueError(f"Некорректный архив APKINDEX: {exc}") from exc


def parse_record(block):
    """Разобрать одну запись APKINDEX."""
    fields = {}
    for line in block.splitlines():
        if len(line) > 1 and line[1] == ":":
            fields[line[0]] = line[2:].strip()
    name = fields.get("P", "")
    if not name:
        return None
    return PackageRecord(
        name=name,
        version=fields.get("V", ""),
        dependencies=fields.get("D", "").split(),
        provides=fields.get("p", "").split(),
    )


def parse_index(text):
    """Разобрать весь APKINDEX и вернуть записи по имени."""
    records = {}
    for block in text.strip().split("\n\n"):
        record = parse_record(block)
        if record is not None:
            records[record.name] = record
    return records


def dependency_name(token):
    """Убрать версионное ограничение и распознать виртуальный токен."""
    if not token or "!" in token:
        return None
    for operator in (">=", "<=", "=", "<", ">", "~"):
        if operator in token:
            token = token.split(operator, 1)[0]
            break
    if token.startswith(("so:", "cmd:", "pkgconfig:")):
        return token
    return token or None


def build_package_graph(records):
    """Построить граф пакетов с разрешением виртуальных provides."""
    providers = {}
    for record in records.values():
        for provided in record.provides:
            providers.setdefault(provided, set()).add(record.name)
    graph = {}
    for name, record in records.items():
        dependencies = set()
        for token in record.dependencies:
            dependency = dependency_name(token)
            if dependency in records:
                dependencies.add(dependency)
            elif dependency in providers:
                dependencies.update(providers[dependency])
        graph[name] = dependencies
    return graph


def load_repository(repo):
    """Загрузить APKINDEX и вернуть записи вместе с графом."""
    text = extract_index(download_index(repo))
    records = parse_index(text)
    if not records:
        raise ValueError("APKINDEX не содержит записей пакетов.")
    return records, build_package_graph(records)
