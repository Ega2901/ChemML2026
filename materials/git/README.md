# 🌿 Git: система контроля версий

> Справочник команд, типовые сценарии работы и разбор кейсов для студентов курса ChemML2026.

---

## Первоначальная настройка

```bash
# Указать имя и email (будут в каждом коммите)
git config --global user.name "Ivan Ivanov"
git config --global user.email "ivan@example.com"

# Посмотреть текущие настройки
git config --list

# Настроить редактор по умолчанию
git config --global core.editor "nano"
```

---

## Основные концепции

```
Working Directory  →  Staging Area (Index)  →  Local Repository  →  Remote Repository
    (рабочая             (подготовлено            (история             (GitHub/GitLab)
     директория)          к коммиту)               коммитов)

      git add ──────►     git commit ──────►       git push ──────►
                ◄──────                  ◄──────                ◄──────
              git restore            git reset              git pull/fetch
```

---

## Создание и клонирование репозитория

| Команда | Описание |
|---------|----------|
| `git init` | Создать новый репозиторий в текущей папке |
| `git clone <url>` | Клонировать удалённый репозиторий |
| `git clone <url> my_dir` | Клонировать в указанную папку |

```bash
# Типичный старт работы с курсовым репозиторием
git clone https://github.com/username/ChemML2026.git
cd ChemML2026
```

---

## Повседневные команды

### Статус и история

| Команда | Описание | Пример |
|---------|----------|--------|
| `git status` | Текущее состояние файлов | |
| `git log` | История коммитов | `git log --oneline --graph` |
| `git log -5` | Последние 5 коммитов | |
| `git diff` | Изменения в рабочей директории | |
| `git diff --staged` | Изменения, добавленные в staging | |
| `git diff branch1..branch2` | Разница между ветками | |
| `git show <commit>` | Содержимое конкретного коммита | `git show abc1234` |
| `git blame <file>` | Кто и когда менял каждую строку | `git blame train.py` |

### Добавление и коммит

| Команда | Описание | Пример |
|---------|----------|--------|
| `git add <file>` | Добавить файл в staging | `git add model.py` |
| `git add .` | Добавить все изменения | |
| `git add -p` | Добавить изменения по частям (интерактивно) | |
| `git commit -m "msg"` | Создать коммит | `git commit -m "Add training script"` |
| `git commit -am "msg"` | Добавить изменённые файлы + коммит | Не добавляет новые файлы! |

> 💡 **Хороший коммит** — атомарный (одно логическое изменение) с понятным сообщением.

### Отмена изменений

| Команда | Описание | Когда использовать |
|---------|----------|--------------------|
| `git restore <file>` | Откатить изменения в рабочей директории | Не нравятся текущие правки |
| `git restore --staged <file>` | Убрать файл из staging (но сохранить правки) | Случайно сделали `git add` |
| `git commit --amend` | Исправить последний коммит | Опечатка в сообщении / забыли файл |
| `git revert <commit>` | Создать новый коммит, отменяющий указанный | Безопасная отмена в общей ветке |
| `git reset --soft HEAD~1` | Отменить коммит, изменения остаются в staging | Хотите переделать коммит |
| `git reset --hard HEAD~1` | Отменить коммит и все изменения | ⚠️ Необратимо! |

---

## Ветвление

```
main  ──●──●──●──────────●──  (стабильная версия)
              \          /
feature        ●──●──●──     (новая функциональность)
```

| Команда | Описание |
|---------|----------|
| `git branch` | Список веток |
| `git branch <name>` | Создать ветку |
| `git checkout <name>` | Переключиться на ветку |
| `git checkout -b <name>` | Создать ветку и переключиться |
| `git branch -d <name>` | Удалить ветку (если смержена) |
| `git merge <branch>` | Влить ветку в текущую |

```bash
# Типичный workflow с веткой
git checkout -b feature/add-model
# ... пишем код ...
git add .
git commit -m "Add neural network model"
git checkout main
git merge feature/add-model
git branch -d feature/add-model
```

---

## Работа с удалённым репозиторием

| Команда | Описание |
|---------|----------|
| `git remote -v` | Список удалённых репозиториев |
| `git remote add <name> <url>` | Добавить удалённый репозиторий |
| `git fetch` | Скачать изменения (без слияния) |
| `git pull` | Скачать и слить изменения (`fetch` + `merge`) |
| `git push` | Отправить коммиты на удалённый репозиторий |
| `git push -u origin <branch>` | Отправить новую ветку и привязать к remote |

---

## Fork и Pull Request (GitHub)

```
[Оригинальный репозиторий]  ◄── Pull Request ──  [Ваш форк]
  (upstream)                                       (origin)
       │                                              │
       ▼                                              ▼
  [Локальная копия] ◄──── git pull ────► [Локальная копия]
```

```bash
# 1. Форкнуть репозиторий на GitHub (кнопка Fork)

# 2. Клонировать свой форк
git clone https://github.com/YOUR_USERNAME/ChemML2026.git
cd ChemML2026

# 3. Добавить оригинальный репозиторий как upstream
git remote add upstream https://github.com/Ega2901/ChemML2026.git

# 4. Создать ветку для задания
git checkout -b stage1

# 5. Выполнить задание, закоммитить
git add .
git commit -m "Complete stage1"

# 6. Отправить ветку в свой форк
git push -u origin stage1

# 7. Создать Pull Request на GitHub: origin/stage1 → upstream/main
```

### Синхронизация форка с оригиналом

```bash
# Получить обновления из оригинального репозитория
git fetch upstream
git checkout main
git merge upstream/main
git push origin main
```

---

## Разбор типичных кейсов

### Кейс 1: «Я редактировал не ту ветку»

Вы сделали изменения в `main`, а нужно было в новой ветке.

```bash
# Изменения ещё не закоммичены:
git stash                       # Сохранить изменения во временное хранилище
git checkout -b correct-branch  # Создать нужную ветку
git stash pop                   # Достать изменения обратно
git add .
git commit -m "Changes in correct branch"
```

### Кейс 2: «Забыл добавить файл в коммит»

```bash
git add forgotten_file.py
git commit --amend --no-edit    # Добавит файл к последнему коммиту
```

> ⚠️ Не используйте `--amend` для коммитов, которые уже отправлены (`push`) — это перезаписывает историю.

### Кейс 3: «Конфликт при merge / pull»

```bash
git pull origin main
# CONFLICT: Merge conflict in model.py

# 1. Открыть файл — найти маркеры конфликта:
<<<<<<< HEAD
x = 10          # ваша версия
=======
x = 20          # версия из remote
>>>>>>> origin/main

# 2. Выбрать нужный вариант, удалить маркеры
x = 20

# 3. Добавить и закоммитить
git add model.py
git commit -m "Resolve merge conflict in model.py"
```

### Кейс 4: «Нужно временно переключиться на другую ветку»

```bash
git stash                    # Спрятать текущие изменения
git checkout other-branch    # Переключиться
# ... сделать что нужно ...
git checkout my-branch       # Вернуться
git stash pop                # Достать изменения
```

### Кейс 5: «Случайно закоммитил большой файл / секрет»

```bash
# Если коммит ещё не отправлен (push):
git reset --soft HEAD~1      # Отменить коммит (файлы останутся в staging)
# Добавить файл в .gitignore
echo "large_data.csv" >> .gitignore
git add .gitignore
git commit -m "Remove large file, update .gitignore"
```

### Кейс 6: «Хочу посмотреть, что было в файле 3 коммита назад»

```bash
git log --oneline            # Найти нужный коммит
git show abc1234:model.py    # Посмотреть файл в том коммите
git diff abc1234 -- model.py # Сравнить с текущей версией
```

### Кейс 7: «Pull request показывает конфликты»

```bash
# Обновить свою ветку относительно main
git checkout my-branch
git fetch upstream
git merge upstream/main       # или git rebase upstream/main

# Разрешить конфликты (см. кейс 3)

git push origin my-branch     # PR обновится автоматически
```

---

## .gitignore — что не должно попасть в репозиторий

```gitignore
# Python
__pycache__/
*.pyc
*.egg-info/
.venv/

# Jupyter
.ipynb_checkpoints/

# Данные (большие файлы)
data/*.csv
data/*.h5
*.pkl

# Среда разработки
.vscode/
.idea/

# Секреты
.env
*.key
credentials.json

# Системные файлы
.DS_Store
Thumbs.db
```

> 💡 Используйте [gitignore.io](https://www.toptal.com/developers/gitignore) для генерации `.gitignore` под ваш стек.

---

## Соглашения по коммитам

Формат сообщения:

```
<тип>: <краткое описание>

<тип> — что сделано:
  feat:     новая функциональность
  fix:      исправление бага
  docs:     изменения в документации
  refactor: рефакторинг без изменения поведения
  test:     добавление/изменение тестов
  data:     изменения в данных или конфигурации
```

Примеры:
```
feat: add random forest classifier
fix: correct feature scaling in pipeline
docs: update README with installation steps
data: add molecule descriptors dataset
```

---

## 📚 Полезные материалы

### Интерактивные курсы
- [Learn Git Branching](https://learngitbranching.js.org/?locale=ru_RU) — визуальный тренажёр по веткам (есть русский язык)
- [Git Immersion](https://gitimmersion.com/) — пошаговый практический курс
- [Oh My Git!](https://ohmygit.org/) — обучающая игра про Git

### Шпаргалки
- [Git Cheat Sheet (GitHub)](https://education.github.com/git-cheat-sheet-education.pdf) — официальная шпаргалка от GitHub
- [devhints.io/git-log](https://devhints.io/git-log) — шпаргалка по `git log`

### Видео и статьи
- [Missing Semester — Version Control (MIT)](https://missing.csail.mit.edu/2020/version-control/) — лекция MIT о Git
- [Pro Git (книга, бесплатная)](https://git-scm.com/book/ru/v2) — полное руководство на русском

### Инструменты
- [GitHub Desktop](https://desktop.github.com/) — GUI-клиент для Git
- [lazygit](https://github.com/jesseduffield/lazygit) — удобный терминальный интерфейс для Git
- [explainshell.com](https://explainshell.com/) — разбор git-команд по частям
