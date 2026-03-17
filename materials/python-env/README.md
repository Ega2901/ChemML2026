# 🐍 Python: пакеты и виртуальные окружения

> Полный гайд по управлению зависимостями и изоляции проектов для студентов курса ChemML2026.

---

## Зачем нужны виртуальные окружения?

```
Без виртуального окружения:                С виртуальным окружением:

Системный Python                           Проект A (.venv/)
├── numpy 1.24                             ├── numpy 1.26
├── pandas 2.0                             └── pandas 2.1
├── scikit-learn 1.2
└── ...                                    Проект B (.venv/)
                                           ├── numpy 1.24
Все проекты используют одни и              └── tensorflow 2.15
те же версии → конфликты!
                                           Каждый проект изолирован → нет конфликтов
```

**Проблема без окружений:**
- Проект A требует `numpy==1.24`, проект B — `numpy==1.26` → невозможно одновременно
- Обновление пакета для одного проекта ломает другой
- Невозможно воспроизвести окружение на другом компьютере

---

## pip — менеджер пакетов Python

### Cheat-sheet

| Команда | Описание |
|---------|----------|
| `pip install <pkg>` | Установить пакет |
| `pip install <pkg>==1.2.3` | Установить конкретную версию |
| `pip install <pkg>>=1.2,<2.0` | Установить с ограничением версий |
| `pip install -r requirements.txt` | Установить все зависимости из файла |
| `pip install -e .` | Установить пакет в режиме разработки |
| `pip uninstall <pkg>` | Удалить пакет |
| `pip list` | Список установленных пакетов |
| `pip show <pkg>` | Информация о пакете |
| `pip freeze` | Список пакетов с точными версиями |
| `pip freeze > requirements.txt` | Сохранить зависимости в файл |

### Примеры

```bash
# Установить несколько пакетов
pip install numpy pandas scikit-learn

# Обновить пакет до последней версии
pip install --upgrade numpy

# Установить из GitHub-репозитория
pip install git+https://github.com/user/repo.git

# Посмотреть, какие пакеты устарели
pip list --outdated
```

---

## venv — встроенное виртуальное окружение Python

> `venv` входит в стандартную библиотеку Python 3.3+ и не требует установки.

### Cheat-sheet

| Действие | Команда |
|----------|---------|
| Создать окружение | `python -m venv .venv` |
| Активировать (Linux/macOS) | `source .venv/bin/activate` |
| Активировать (Windows cmd) | `.venv\Scripts\activate.bat` |
| Активировать (Windows PowerShell) | `.venv\Scripts\Activate.ps1` |
| Деактивировать | `deactivate` |
| Удалить окружение | `rm -rf .venv` |

### Полный рабочий цикл

```bash
# 1. Создать окружение
python -m venv .venv

# 2. Активировать
source .venv/bin/activate

# 3. Убедиться, что используется правильный Python
which python    # → .venv/bin/python
python --version

# 4. Установить зависимости
pip install numpy pandas matplotlib

# 5. Сохранить зависимости
pip freeze > requirements.txt

# 6. Работаем...

# 7. Деактивировать когда закончили
deactivate
```

### Что внутри .venv/?

```
.venv/
├── bin/                    # (Linux/macOS) или Scripts/ (Windows)
│   ├── activate            # Скрипт активации
│   ├── python → python3.11 # Символическая ссылка на интерпретатор
│   ├── pip                 # pip внутри окружения
│   └── ...                 # Установленные CLI-утилиты (jupyter, pytest и т.д.)
├── lib/
│   └── python3.11/
│       └── site-packages/  # ← Все установленные пакеты лежат здесь
│           ├── numpy/
│           ├── pandas/
│           └── ...
├── include/                # Заголовочные файлы для C-расширений
└── pyvenv.cfg              # Конфигурация окружения
```

**pyvenv.cfg** — конфигурация:
```ini
home = /usr/bin                   # Путь к базовому Python
include-system-site-packages = false  # Изоляция от системных пакетов
version = 3.11.5                  # Версия Python
```

> ⚠️ **Никогда не коммитьте `.venv/` в git!** Добавьте в `.gitignore`:
> ```
> .venv/
> ```

---

## conda — менеджер пакетов и окружений

> Conda управляет не только Python-пакетами, но и системными библиотеками (CUDA, MKL и др.).
> Это особенно важно для научных вычислений и ML.

### Установка

- **Miniconda** (рекомендуется) — минимальная установка: [docs.conda.io/en/latest/miniconda.html](https://docs.conda.io/en/latest/miniconda.html)
- **Anaconda** — полная сборка с 250+ пакетами: [anaconda.com](https://www.anaconda.com/)

### Cheat-sheet: окружения

| Действие | Команда |
|----------|---------|
| Создать окружение | `conda create -n myenv python=3.11` |
| Создать из файла | `conda env create -f environment.yml` |
| Активировать | `conda activate myenv` |
| Деактивировать | `conda deactivate` |
| Список окружений | `conda env list` |
| Удалить окружение | `conda env remove -n myenv` |
| Экспорт окружения | `conda env export > environment.yml` |
| Экспорт (кроссплатформенный) | `conda env export --from-history > environment.yml` |

### Cheat-sheet: пакеты

| Действие | Команда |
|----------|---------|
| Установить пакет | `conda install numpy` |
| Установить конкретную версию | `conda install numpy=1.26` |
| Установить из conda-forge | `conda install -c conda-forge rdkit` |
| Установить через pip (в conda-окружении) | `pip install package_name` |
| Обновить пакет | `conda update numpy` |
| Обновить все пакеты | `conda update --all` |
| Удалить пакет | `conda remove numpy` |
| Список установленных | `conda list` |
| Поиск пакета | `conda search rdkit` |

### Полный рабочий цикл

```bash
# 1. Создать окружение для проекта
conda create -n chemml python=3.11

# 2. Активировать
conda activate chemml

# 3. Установить пакеты
conda install numpy pandas scikit-learn matplotlib
conda install -c conda-forge rdkit    # Химические библиотеки из conda-forge

# 4. Если пакет есть только в pip
pip install some-rare-package

# 5. Экспортировать окружение
conda env export > environment.yml

# 6. Деактивировать
conda deactivate
```

### Что внутри conda-окружения?

```
~/miniconda3/envs/chemml/
├── bin/
│   ├── python
│   ├── pip
│   ├── conda
│   └── ...
├── lib/
│   ├── python3.11/
│   │   └── site-packages/     # Python-пакеты
│   ├── libopenblas.so         # Системные библиотеки (это суперсила conda!)
│   └── ...
├── include/
├── share/
└── conda-meta/
    ├── history                # История установок
    └── numpy-1.26.0-*.json   # Метаинформация о каждом пакете
```

> 💡 **Conda vs venv:** conda может устанавливать не-Python библиотеки (CUDA, компиляторы, RDKit), а venv — только Python-пакеты через pip.

---

## uv — быстрый менеджер пакетов

> `uv` — современная замена pip + venv, написанная на Rust. В 10-100× быстрее pip.

### Установка uv

```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Или через pip
pip install uv

# Проверить
uv --version
```

### Cheat-sheet

| Действие | Команда |
|----------|---------|
| Создать окружение | `uv venv` |
| Создать с конкретным Python | `uv venv --python 3.11` |
| Активировать | `source .venv/bin/activate` |
| Установить пакет | `uv pip install numpy` |
| Установить из файла | `uv pip install -r requirements.txt` |
| Список пакетов | `uv pip list` |
| Сохранить зависимости | `uv pip freeze > requirements.txt` |
| Заблокировать версии | `uv pip compile requirements.in -o requirements.txt` |

### Проектный режим (uv как замена всему)

```bash
# Инициализировать проект
uv init my-project
cd my-project

# Добавить зависимость (автоматически обновляет pyproject.toml и uv.lock)
uv add numpy pandas scikit-learn

# Запустить скрипт (uv сам создаст окружение и установит зависимости)
uv run python train.py

# Синхронизировать окружение с lock-файлом
uv sync
```

### Что создаёт uv?

```
my-project/
├── .venv/                 # Виртуальное окружение (как в venv)
├── pyproject.toml         # Описание проекта и зависимостей
├── uv.lock                # Заблокированные версии всех зависимостей
└── src/
    └── my_project/
        └── __init__.py
```

---

## Файлы зависимостей: разбор

### requirements.txt

Простой текстовый список пакетов. Используется с `pip` и `uv`.

```
# Точные версии (воспроизводимость)
numpy==1.26.4
pandas==2.1.4
scikit-learn==1.3.2

# Диапазон версий (гибкость)
matplotlib>=3.7,<4.0

# Из GitHub
git+https://github.com/user/repo.git@v1.0

# Без указания версии (последняя)
tqdm
```

**Два подхода:**

```
requirements.in              requirements.txt
(что нужно вам)      →       (что нужно компьютеру)

numpy                        numpy==1.26.4
pandas                       pandas==2.1.4
scikit-learn                  scikit-learn==1.3.2
                              scipy==1.11.4       ← транзитивная зависимость
                              joblib==1.3.2       ← транзитивная зависимость
                              ...

Команда: pip-compile requirements.in → requirements.txt
     или: uv pip compile requirements.in -o requirements.txt
```

### environment.yml (conda)

```yaml
name: chemml                          # Имя окружения
channels:                             # Откуда брать пакеты
  - conda-forge                       # Сначала ищет здесь
  - defaults                          # Потом здесь
dependencies:                         # Пакеты conda
  - python=3.11
  - numpy=1.26
  - pandas=2.1
  - rdkit                             # Доступен только через conda
  - pip:                              # Пакеты через pip (если нет в conda)
    - some-pip-only-package==1.0
```

```bash
# Создать окружение из файла
conda env create -f environment.yml

# Обновить окружение
conda env update -f environment.yml
```

### pyproject.toml

Современный стандарт описания Python-проекта (PEP 621). Один файл вместо `setup.py`, `setup.cfg`, `requirements.txt`.

```toml
[project]
name = "chemml-project"
version = "0.1.0"
description = "ML models for chemistry"
requires-python = ">=3.10"

# Основные зависимости
dependencies = [
    "numpy>=1.24",
    "pandas>=2.0",
    "scikit-learn>=1.3",
]

# Опциональные зависимости (группы)
[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "ruff>=0.1.0",
]
notebooks = [
    "jupyter>=1.0",
    "matplotlib>=3.7",
]

[build-system]
requires = ["setuptools>=68.0"]
build-backend = "setuptools.backends._legacy:_Backend"
```

```bash
# Установить проект
pip install .

# Установить с опциональными зависимостями
pip install ".[dev,notebooks]"

# Установить в режиме разработки
pip install -e ".[dev]"
```

### uv.lock

Автоматически генерируемый lock-файл. **Не редактируется вручную.** Гарантирует, что все получат одинаковые версии.

```
# Этот файл создаётся командами uv add / uv lock
# Содержит точные версии ВСЕХ зависимостей (включая транзитивные)
# и хеши пакетов для безопасности
```

### setup.py / setup.cfg (устаревшие)

> Устаревший способ описания проекта. Если встретите в старом коде — используйте, но для новых проектов берите `pyproject.toml`.

---

## Сравнение инструментов

| Критерий | venv + pip | conda | uv |
|----------|-----------|-------|-----|
| Установка | Встроен в Python | Отдельная установка | `curl` или `pip install uv` |
| Скорость | Средняя | Медленная | Очень быстрая |
| Не-Python пакеты | Нет | Да (CUDA, MKL, RDKit) | Нет |
| Управление Python | Нет | Да | Да (`uv python install`) |
| Lock-файл | Нет (нужен pip-tools) | Нет | Да (`uv.lock`) |
| Научные пакеты | pip install | conda install | uv pip install |
| Рекомендация | Простые проекты | Научные вычисления, хемоинформатика | Новые проекты, скорость |

### Что выбрать?

```
Нужен RDKit, CUDA, или специфичные научные библиотеки?
├── Да  → conda
└── Нет
    ├── Новый проект, хотите скорость → uv
    └── Простой скрипт / учебный проект → venv + pip
```

---

## Разбор типичных кейсов

### Кейс 1: «Клонировал репозиторий, как запустить?»

```bash
# Вариант A: есть requirements.txt
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Вариант B: есть environment.yml
conda env create -f environment.yml
conda activate chemml

# Вариант C: есть pyproject.toml + uv.lock
uv sync

# Вариант D: есть pyproject.toml (без lock)
pip install -e .
```

### Кейс 2: «pip install не работает — ошибка компиляции»

```bash
# Ошибка вида: "error: command 'gcc' failed"
# Решение 1: установить через conda (скомпилированные бинарники)
conda install problematic-package

# Решение 2: установить системные зависимости
# macOS:
brew install cmake openblas
# Ubuntu:
sudo apt install build-essential python3-dev

# Решение 3: установить бинарный пакет (wheel)
pip install --only-binary :all: problematic-package
```

### Кейс 3: «Нужен и conda, и pip в одном окружении»

```bash
# Правило: сначала conda, потом pip. Не наоборот!
conda create -n myenv python=3.11
conda activate myenv

# 1. Сначала установить всё что можно через conda
conda install numpy pandas scikit-learn rdkit -c conda-forge

# 2. Потом оставшееся через pip
pip install some-pip-only-package

# 3. При экспорте — pip-зависимости тоже сохранятся
conda env export > environment.yml
```

> ⚠️ Если после `pip install` снова делать `conda install` — conda может сломать pip-пакеты. Всегда сначала conda, потом pip.

### Кейс 4: «Мой скрипт работает у меня, но не у коллеги»

```bash
# Проблема: разные версии пакетов
# Решение: зафиксировать зависимости

# Вариант 1: requirements.txt
pip freeze > requirements.txt
# Коллега:
pip install -r requirements.txt

# Вариант 2: conda
conda env export > environment.yml
# Коллега:
conda env create -f environment.yml

# Вариант 3: uv (самый надёжный — lock-файл)
uv lock
# Коллега:
uv sync
```

### Кейс 5: «Занимает много места, как почистить?»

```bash
# Удалить кеш pip
pip cache purge

# Удалить кеш conda
conda clean --all

# Удалить неиспользуемые conda-окружения
conda env list                    # посмотреть
conda env remove -n old_env      # удалить

# Удалить venv
rm -rf .venv                     # просто удалить папку
```

### Кейс 6: «Нужна другая версия Python»

```bash
# conda — проще всего
conda create -n py310 python=3.10
conda activate py310

# uv
uv python install 3.10
uv venv --python 3.10

# venv — нужно установить Python отдельно
# macOS:
brew install python@3.10
python3.10 -m venv .venv
```

### Кейс 7: «Как правильно оформить проект для сдачи?»

Минимальная структура:
```
my_project/
├── .gitignore              # Исключить .venv/, __pycache__/ и т.д.
├── README.md               # Как установить и запустить
├── requirements.txt        # Зависимости
└── src/
    └── main.py
```

В README.md:
```markdown
## Установка
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

## Запуск
python src/main.py
```

---

## 📚 Полезные материалы

### Документация
- [pip — официальная документация](https://pip.pypa.io/en/stable/)
- [venv — документация Python](https://docs.python.org/3/library/venv.html)
- [conda — документация](https://docs.conda.io/en/latest/)
- [uv — документация](https://docs.astral.sh/uv/)

### Статьи и гайды
- [Python Packaging User Guide](https://packaging.python.org/) — официальный гайд по упаковке Python-проектов
- [Real Python — Virtual Environments](https://realpython.com/python-virtual-environments-a-primer/) — подробный туториал по виртуальным окружениям
- [Conda vs pip vs venv (Anaconda Blog)](https://www.anaconda.com/blog/understanding-conda-and-pip) — сравнение инструментов

### Инструменты
- [pip-tools](https://github.com/jazzband/pip-tools) — `pip-compile` для генерации lock-файлов
- [pipdeptree](https://github.com/tox-dev/pipdeptree) — дерево зависимостей: `pipdeptree`
