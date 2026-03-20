#!/usr/bin/env python3

import json
import os
import subprocess
import sys
import re


REQUIRED_FILES = [
    "Dockerfile",
    "pyproject.toml",
    "uv.lock",
    "generate_data.py",
    "train.py",
]

REQUIRED_DEPS = ["numpy", "pandas", "scikit-learn", "matplotlib"]

REQUIRED_METRICS_KEYS = ["R2_test", "MAE_test", "RMSE_test"]

BASELINE_MODELS = ["LinearRegression", "RandomForest", "GradientBoosting"]

REQUIRED_PLOTS = 3


class CheckResult:
    def __init__(self, name: str, passed: bool, detail: str = "", points: float = 0):
        self.name = name
        self.passed = passed
        self.detail = detail
        self.points = points


def run_cmd(cmd: list[str], cwd: str = None, timeout: int = 300) -> tuple[int, str, str]:
    try:
        proc = subprocess.run(
            cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout
        )
        return proc.returncode, proc.stdout, proc.stderr
    except subprocess.TimeoutExpired:
        return -1, "", f"Timeout ({timeout}s)"


def read_file(path: str) -> str:
    try:
        with open(path, encoding="utf-8") as f:
            return f.read()
    except Exception:
        return ""


def check_files(student_dir: str) -> CheckResult:
    missing = []
    for fname in REQUIRED_FILES:
        if not os.path.isfile(os.path.join(student_dir, fname)):
            missing.append(fname)
    if missing:
        return CheckResult(
            "Обязательные файлы",
            False,
            f"Отсутствуют: {', '.join(missing)}",
            0,
        )
    return CheckResult("Обязательные файлы", True, "Все файлы на месте", 1)


def check_pyproject(student_dir: str) -> CheckResult:
    content = read_file(os.path.join(student_dir, "pyproject.toml")).lower()
    if not content:
        return CheckResult("pyproject.toml", False, "Файл пустой или не читается", 0)

    missing = [dep for dep in REQUIRED_DEPS if dep not in content]
    if missing:
        return CheckResult(
            "pyproject.toml",
            False,
            f"Не найдены зависимости: {', '.join(missing)}",
            0,
        )
    return CheckResult("pyproject.toml", True, "Все зависимости указаны", 1)


def check_docker_build(student_dir: str, image_tag: str) -> CheckResult:
    rc, stdout, stderr = run_cmd(
        ["docker", "build", "-t", image_tag, "."],
        cwd=student_dir,
        timeout=600,
    )
    if rc != 0:
        err_tail = "\n".join((stderr or stdout).strip().splitlines()[-15:])
        return CheckResult(
            "Docker build",
            False,
            f"Сборка завершилась с кодом {rc}:\n```\n{err_tail}\n```",
            0,
        )
    return CheckResult("Docker build", True, "Образ собран успешно", 2)


def check_docker_run(student_dir: str, image_tag: str, output_dir: str) -> CheckResult:
    os.makedirs(output_dir, exist_ok=True)

    rc, stdout, stderr = run_cmd(
        [
            "docker", "run", "--rm",
            "-v", f"{output_dir}:/app/results",
            image_tag,
        ],
        cwd=student_dir,
        timeout=300,
    )
    if rc != 0:
        err_tail = "\n".join((stderr or stdout).strip().splitlines()[-15:])
        return CheckResult(
            "Docker run",
            False,
            f"Контейнер завершился с кодом {rc}:\n```\n{err_tail}\n```",
            0,
        )
    return CheckResult("Docker run", True, "Контейнер отработал успешно", 2)


def check_metrics(output_dir: str) -> tuple[CheckResult, dict | None]:
    metrics_path = os.path.join(output_dir, "metrics.json")
    if not os.path.isfile(metrics_path):
        return CheckResult("metrics.json", False, "Файл не найден в results/", 0), None

    try:
        with open(metrics_path) as f:
            metrics = json.load(f)
    except (json.JSONDecodeError, Exception) as e:
        return CheckResult("metrics.json", False, f"Ошибка парсинга: {e}", 0), None

    if not isinstance(metrics, dict) or len(metrics) == 0:
        return CheckResult("metrics.json", False, "Пустой или не словарь", 0), None

    errors = []
    for model_name, model_metrics in metrics.items():
        if not isinstance(model_metrics, dict):
            errors.append(f"{model_name}: не словарь")
            continue
        for key in REQUIRED_METRICS_KEYS:
            if key not in model_metrics:
                errors.append(f"{model_name}: нет ключа {key}")

    if errors:
        return (
            CheckResult(
                "metrics.json",
                False,
                f"Ошибки структуры: {'; '.join(errors[:5])}",
                0,
            ),
            metrics,
        )

    table_lines = ["| Модель | R² | MAE | RMSE |", "|--------|-----|-----|------|"]
    for name, m in metrics.items():
        table_lines.append(
            f"| {name} | {m.get('R2_test', '?')} | {m.get('MAE_test', '?')} | {m.get('RMSE_test', '?')} |"
        )
    detail = f"{len(metrics)} модел(ей) с корректной структурой\n\n" + "\n".join(table_lines)
    return CheckResult("metrics.json", True, detail, 1), metrics


def check_plots(output_dir: str) -> CheckResult:
    pngs = [f for f in os.listdir(output_dir) if f.endswith(".png")]
    if len(pngs) < REQUIRED_PLOTS:
        return CheckResult(
            "Графики",
            False,
            f"Найдено {len(pngs)} PNG, нужно >= {REQUIRED_PLOTS}: {pngs}",
            0,
        )
    return CheckResult("Графики", True, f"Найдено {len(pngs)} PNG: {', '.join(sorted(pngs))}", 1)


def check_task1_svr(metrics: dict | None, student_dir: str) -> CheckResult:
    train_code = read_file(os.path.join(student_dir, "train.py")).lower()
    has_svr_import = "svr" in train_code

    has_svr_metrics = False
    if metrics:
        has_svr_metrics = any("svr" in name.lower() for name in metrics)

    if has_svr_metrics:
        return CheckResult("Задание 1: SVR", True, "SVR найден в результатах", 1)
    elif has_svr_import:
        return CheckResult(
            "Задание 1: SVR",
            False,
            "SVR импортирован в train.py, но не найден в metrics.json",
            0.5,
        )
    return CheckResult("Задание 1: SVR", False, "SVR не найден ни в коде, ни в метриках", 0)


def check_task2_descriptor(student_dir: str, metrics: dict | None) -> CheckResult:
    gen_code = read_file(os.path.join(student_dir, "generate_data.py"))
    has_descriptor = "FormalCharge" in gen_code or "formalcharge" in gen_code.lower()

    if not has_descriptor:
        return CheckResult(
            "Задание 2: FormalCharge",
            False,
            "FormalCharge не найден в generate_data.py",
            0,
        )

    has_in_formula = bool(
        re.search(r'df\[.?FormalCharge.?\]', gen_code, re.IGNORECASE)
        and "LogS" in gen_code
    )
    if has_in_formula:
        return CheckResult(
            "Задание 2: FormalCharge",
            True,
            "FormalCharge найден в generate_data.py и используется в формуле LogS",
            1,
        )
    return CheckResult(
        "Задание 2: FormalCharge",
        True,
        "FormalCharge найден в generate_data.py (не удалось автоматически проверить влияние на LogS)",
        0.5,
    )


def check_task3_gridsearch(output_dir: str, student_dir: str) -> CheckResult:
    train_code = read_file(os.path.join(student_dir, "train.py")).lower()
    has_gridsearch = "gridsearchcv" in train_code

    best_params_path = os.path.join(output_dir, "best_params.json")
    has_file = os.path.isfile(best_params_path)

    if has_file:
        try:
            with open(best_params_path) as f:
                params = json.load(f)
            return CheckResult(
                "Бонус: GridSearchCV",
                True,
                f"best_params.json найден: {json.dumps(params, ensure_ascii=False)}",
                1,
            )
        except Exception:
            return CheckResult(
                "Бонус: GridSearchCV", False, "best_params.json найден, но невалидный JSON", 0.5
            )

    if has_gridsearch:
        return CheckResult(
            "Бонус: GridSearchCV",
            False,
            "GridSearchCV есть в коде, но best_params.json не сгенерирован",
            0.5,
        )
    return CheckResult("Бонус: GridSearchCV", False, "Не реализовано (бонусное задание)", 0)


def generate_report(results: list[CheckResult], student_name: str) -> str:
    total_points = sum(r.points for r in results)
    max_points = 11
    passed = sum(1 for r in results if r.passed)

    lines = []
    lines.append(f"## Автопроверка: {student_name}")
    lines.append("")
    lines.append(f"**Результат: {total_points}/{max_points} баллов** ({passed}/{len(results)} проверок пройдено)")
    lines.append("")

    if total_points >= 9:
        grade = "Отлично"
    elif total_points >= 7:
        grade = "Хорошо"
    elif total_points >= 5:
        grade = "Удовлетворительно"
    else:
        grade = "Нужна доработка"
    lines.append(f"**Оценка: {grade}**")
    lines.append("")

    lines.append("### Детали проверок")
    lines.append("")
    lines.append("| # | Проверка | Статус | Баллы | Детали |")
    lines.append("|---|----------|--------|-------|--------|")

    for i, r in enumerate(results, 1):
        icon = "PASS" if r.passed else "FAIL"
        short_detail = r.detail.split("\n")[0][:100]
        lines.append(f"| {i} | {r.name} | {icon} | {r.points} | {short_detail} |")

    lines.append("")

    for i, r in enumerate(results, 1):
        if "\n" in r.detail:
            lines.append("<details>")
            lines.append(f"<summary>{r.name} — подробности</summary>")
            lines.append("")
            lines.append(r.detail)
            lines.append("")
            lines.append("</details>")
            lines.append("")

    return "\n".join(lines)


def main():
    if len(sys.argv) < 2:
        print("Использование: python check_docker_uv.py <путь_к_dir_1/Фамилия_Имя>")
        sys.exit(1)

    student_dir = os.path.abspath(sys.argv[1])
    student_name = os.path.basename(student_dir)

    if not os.path.isdir(student_dir):
        print(f"Директория не найдена: {student_dir}")
        sys.exit(1)

    print(f"=== Проверка работы: {student_name} ===")
    print(f"Директория: {student_dir}")
    print()

    image_tag = f"check-{student_name.lower().replace('_', '-')}"
    output_dir = os.path.abspath(os.path.join(student_dir, "..", "..", f".check_output_{student_name}"))

    results: list[CheckResult] = []

    r = check_files(student_dir)
    results.append(r)
    print(f"[{'PASS' if r.passed else 'FAIL'}] {r.name}: {r.detail}")
    if not r.passed:
        report = generate_report(results, student_name)
        print("\n" + report)
        write_report(report)
        sys.exit(1)

    r = check_pyproject(student_dir)
    results.append(r)
    print(f"[{'PASS' if r.passed else 'FAIL'}] {r.name}: {r.detail}")

    print("\n[....] Docker build (это может занять несколько минут)...")
    r = check_docker_build(student_dir, image_tag)
    results.append(r)
    print(f"[{'PASS' if r.passed else 'FAIL'}] {r.name}: {r.detail.split(chr(10))[0]}")
    if not r.passed:
        results.extend([
            CheckResult("Docker run", False, "Пропущено: образ не собрался", 0),
            CheckResult("metrics.json", False, "Пропущено: контейнер не запускался", 0),
            CheckResult("Графики", False, "Пропущено: контейнер не запускался", 0),
            CheckResult("Задание 1: SVR", False, "Пропущено: контейнер не запускался", 0),
            CheckResult("Задание 2: FormalCharge", False, "Пропущено: контейнер не запускался", 0),
            CheckResult("Бонус: GridSearchCV", False, "Пропущено: контейнер не запускался", 0),
        ])
        report = generate_report(results, student_name)
        print("\n" + report)
        write_report(report)
        cleanup(image_tag, output_dir)
        sys.exit(1)

    print("\n[....] Docker run...")
    r = check_docker_run(student_dir, image_tag, output_dir)
    results.append(r)
    print(f"[{'PASS' if r.passed else 'FAIL'}] {r.name}: {r.detail.split(chr(10))[0]}")
    if not r.passed:
        results.extend([
            CheckResult("metrics.json", False, "Пропущено: контейнер упал", 0),
            CheckResult("Графики", False, "Пропущено: контейнер упал", 0),
            CheckResult("Задание 1: SVR", False, "Пропущено: контейнер упал", 0),
            CheckResult("Задание 2: FormalCharge", False, "Пропущено: контейнер упал", 0),
            CheckResult("Бонус: GridSearchCV", False, "Пропущено: контейнер упал", 0),
        ])
        report = generate_report(results, student_name)
        print("\n" + report)
        write_report(report)
        cleanup(image_tag, output_dir)
        sys.exit(1)

    r_metrics, metrics = check_metrics(output_dir)
    results.append(r_metrics)
    print(f"[{'PASS' if r_metrics.passed else 'FAIL'}] {r_metrics.name}: {r_metrics.detail.split(chr(10))[0]}")

    r = check_plots(output_dir)
    results.append(r)
    print(f"[{'PASS' if r.passed else 'FAIL'}] {r.name}: {r.detail}")

    r = check_task1_svr(metrics, student_dir)
    results.append(r)
    print(f"[{'PASS' if r.passed else 'FAIL'}] {r.name}: {r.detail}")

    r = check_task2_descriptor(student_dir, metrics)
    results.append(r)
    print(f"[{'PASS' if r.passed else 'FAIL'}] {r.name}: {r.detail}")

    r = check_task3_gridsearch(output_dir, student_dir)
    results.append(r)
    print(f"[{'PASS' if r.passed else 'FAIL'}] {r.name}: {r.detail}")

    report = generate_report(results, student_name)
    print("\n" + report)
    write_report(report)

    cleanup(image_tag, output_dir)

    total = sum(r.points for r in results)
    if total < 5:
        sys.exit(1)


def write_report(report: str):
    summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary_path:
        with open(summary_path, "a") as f:
            f.write(report + "\n")

    report_path = os.environ.get("REPORT_PATH", "/tmp/check_report.md")
    with open(report_path, "w") as f:
        f.write(report)


def cleanup(image_tag: str, output_dir: str):
    run_cmd(["docker", "rmi", "-f", image_tag])
    if os.path.isdir(output_dir):
        import shutil
        shutil.rmtree(output_dir, ignore_errors=True)


if __name__ == "__main__":
    main()
