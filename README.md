# Alpine APK Dependency Graph

## 1. Общее описание

CLI-проект строит ориентированный граф зависимостей Alpine Linux из
APKINDEX.tar.gz или локального текстового графа. Зависимости извлекаются
ручным разбором полей `P`, `V`, `D` и `p`; системные менеджеры пакетов
и сторонние Python-библиотеки не используются. Для обхода применяется
рекурсивный BFS, а результат выводится как PlantUML и, при доступности
сети, как SVG через публичный PlantUML server. Требуется Python 3.10+.

## 2. Параметры и функции модулей

| Параметр | Назначение |
|---|---|
| `--package` | Имя корневого пакета |
| `--repo` | HTTPS URL каталога/файла APKINDEX либо файл тестового графа |
| `--test-mode` | Читать `--repo` как локальный текстовый граф |
| `--version` | Проверить точную версию корневого пакета |
| `--output` | Имя SVG, по умолчанию `graph.svg` |
| `--max-depth` | Максимальная глубина BFS, корень имеет глубину 0 |
| `--filter` | Исключить пакеты, имя которых содержит подстроку |
| `--show-config` | Напечатать все параметры |
| `--show-direct` | Напечатать только прямые зависимости |
| `--reverse` | Найти пакеты, зависящие от корневого |

Модули и функции:

- `config.py`: `Config` хранит параметры; `build_parser` создаёт argparse;
  `validate_package`, `validate_repo`, `validate_version`,
  `validate_output`, `validate_depth` проверяют значения;
  `parse_args` собирает конфигурацию; `config_lines` форматирует её.
- `apk_repo.py`: `PackageRecord` описывает запись APKINDEX;
  `download_index` загружает архив; `extract_index` извлекает индекс;
  `parse_record` и `parse_index` разбирают текст; `dependency_name`
  очищает ограничения; `build_package_graph` разрешает provides;
  `load_repository` выполняет полный цикл.
- `test_repo.py`: `parse_graph_text` разбирает формат `A: B C`;
  `load_test_graph` читает файл.
- `graph.py`: `Traversal` хранит результат; `breadth_first` запускает
  рекурсивный BFS; `_visit_frontier` обрабатывает фронт; `induced_graph`
  строит подграф; `direct_dependencies` выдаёт прямые рёбра;
  `edge_list` формирует список рёбер.
- `reverse.py`: `reverse_graph` переворачивает рёбра;
  `reverse_dependencies` выполняет обратный BFS.
- `visualize.py`: `plantuml_text` формирует PlantUML;
  `plantuml_encode` кодирует текст; `plantuml_url` формирует URL;
  `request_svg` получает SVG; `save_visualization` сохраняет результат.
- `main.py`: `_load_graph`, `_check_root`, `_select_graph`, `run` и
  `main` связывают CLI и модули.

В тестовом режиме допустимы только имена `[A-Z]+`. Пустые строки и
строки-комментарии с `#` игнорируются. Строка задаётся как `A: B C`.

## 3. Запуск и тесты

Из корня проекта:

```bash
python -m src.main --package A --repo tests/data/simple.txt --test-mode
python -m unittest discover -s tests -v
make test
make demo
make clean
```

`make demo` строит граф `A` из `tests/data/simple.txt` в `demo.svg`.
Тесты полностью офлайн; тесты визуализации не вызывают PlantUML.

## 4. Примеры использования

Реальный режим загружает актуальный индекс указанной ветки. Вывод ниже
иллюстративный: состав зависимостей зависит от версии Alpine и архитектуры.

```bash
python -m src.main --package curl --repo \
  https://dl-cdn.alpinelinux.org/alpine/v3.20/main/x86_64/ \
  --max-depth 2 --output curl.svg
```

Примерный вывод PlantUML:

```text
@startuml
left to right direction
rectangle "curl" as curl
rectangle "ca-certificates" as ca-certificates
curl --> ca-certificates
@enduml
```

```bash
python -m src.main --package git --repo \
  https://dl-cdn.alpinelinux.org/alpine/v3.20/main/x86_64/
python -m src.main --package alpine-base --repo \
  https://dl-cdn.alpinelinux.org/alpine/v3.20/main/x86_64/
```

Пример тестового цикла:

```bash
python -m src.main --package A --repo tests/data/cycle.txt \
  --test-mode --max-depth 5
```

Ограничение глубины:

```bash
python -m src.main --package A --repo tests/data/deep.txt \
  --test-mode --max-depth 2
```

Фильтрация TESTLIB:

```bash
python -m src.main --package A --repo tests/data/filter.txt \
  --test-mode --filter TEST
```

Обратные зависимости для musl (пример для указанной ветки):

```bash
python -m src.main --package musl --repo \
  https://dl-cdn.alpinelinux.org/alpine/v3.20/main/x86_64/ \
  --reverse --max-depth 1
```

Примеры ошибочных команд:

```bash
python -m src.main --package "" --repo tests/data/simple.txt --test-mode
python -m src.main --package A --repo missing.txt --test-mode
python -m src.main --package A --repo http://example.org/APKINDEX.tar.gz
python -m src.main --package A --repo tests/data/simple.txt \
  --test-mode --max-depth -1
python -m src.main --package A --repo tests/data/simple.txt \
  --test-mode --output graph.png
```

Ошибки валидации и загрузки выводятся в stderr, код возврата равен 1.
При недоступности PlantUML-сервера исходник `.puml` остаётся на диске,
а CLI печатает предупреждение.

## 5. Сравнение со штатными apk info -R и apk dot

`apk info -R` показывает зависимости установленного пакета в контексте
локальной базы apk, тогда как этот проект анализирует выбранный удалённый
APKINDEX. `apk dot` строит граф на основании данных самого apk и его
механизма разрешения зависимостей.

Возможные расхождения:

- В APKINDEX виртуальные возможности задаются `p`; проект разрешает
  `so:`, `cmd:` и `pkgconfig:` через эту карту, но неоднозначные provides
  могут дать несколько рёбер.
- Версии и ветки репозитория влияют на состав пакетов и зависимости.
  `--version` проверяет точное совпадение только у корневого пакета.
- `--max-depth` намеренно обрезает транзитивный обход.
- `--filter` исключает узлы по подстроке и связанные с ними рёбра.
- По умолчанию строится транзитивный граф, а `--show-direct` выводит
  только непосредственные зависимости. Обратный режим ищет зависимые
  пакеты по всем записям индекса.
