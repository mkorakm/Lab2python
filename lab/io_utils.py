import csv
import os

from lab.errors import CSVError, ValidationError
from lab.models import Student



def _parse_int(value: str, field: str, line_no: int) -> int:
    try:
        return int(value)
    except (ValueError, TypeError):
        raise CSVError(f"Строка {line_no}: поле '{field}' должно быть целым числом, получено {value!r}")


def _parse_grade(value: str, line_no: int) -> int | None:
    value = value.strip()
    if value == "":
        return None
    try:
        g = int(value)
    except ValueError:
        raise CSVError(f"Строка {line_no}: оценка должна быть целым числом, получено {value!r}")
    if not (0 <= g <= 100):
        raise CSVError(f"Строка {line_no}: оценка вне диапазона 0..100: {g}")
    return g


def _looks_like_header(row: list[str]) -> bool:

    if not row:
        return False
    try:
        int(row[0].strip())
        return False
    except ValueError:
        return True


def read_csv(path: str) -> list[Student]:

    if not os.path.exists(path):
        raise CSVError(f"Файл не найден: {path}")

    try:
        with open(path, encoding="utf-8", newline="") as f:
            reader = csv.reader(f)
            rows = list(reader)
    except PermissionError:
        raise CSVError(f"Нет прав на чтение файла: {path}")
    except OSError as e:
        raise CSVError(f"Ошибка чтения файла {path}: {e}")

    if not rows:
        return []

    if _looks_like_header(rows[0]):
        rows = rows[1:]

    students: list[Student] = []
    seen_ids: set[int] = set()

    for i, row in enumerate(rows, start=1):

        if not row or all(cell.strip() == "" for cell in row):
            continue

        if len(row) < 2:
            raise CSVError(f"Строка {i}: нужно минимум 2 колонки (id, name), получено {len(row)}")

        student_id = _parse_int(row[0].strip(), "id", i)
        if student_id < 0:
            raise CSVError(f"Строка {i}: id не может быть отрицательным: {student_id}")
        if student_id in seen_ids:
            raise CSVError(f"Строка {i}: дубликат id={student_id}")
        seen_ids.add(student_id)

        name = row[1].strip()
        if not name:
            raise CSVError(f"Строка {i}: имя не может быть пустым")

        grades = [_parse_grade(cell, i) for cell in row[2:]]

        try:
            students.append(Student(student_id, name, grades))
        except ValidationError as e:
            raise CSVError(f"Строка {i}: {e}")

    return students



def write_csv(path: str, students: list[Student]) -> None:

    max_grades = max((len(s.grades) for s in students), default=0)
    header = ["id", "name"] + [f"grade{i}" for i in range(1, max_grades + 1)]

    try:
        with open(path, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(header)
            for s in students:
                row = [str(s.id), s.name]
                for g in s.grades:
                    row.append("" if g is None else str(g))

                while len(row) < 2 + max_grades:
                    row.append("")
                writer.writerow(row)
    except PermissionError:
        raise CSVError(f"Нет прав на запись в файл: {path}")
    except OSError as e:
        raise CSVError(f"Ошибка записи файла {path}: {e}")


def export_top_n(path: str, students: list[Student], n: int) -> None:

    if n <= 0:
        raise ValidationError(f"N должно быть положительным, получено {n}")

    sorted_students = sorted(students, key=lambda s: (-s.average, s.name))[:n]

    try:
        with open(path, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["id", "name", "average", "grades"])
            for s in sorted_students:
                grades_str = " ".join(
                    "" if g is None else str(g) for g in s.grades
                )
                writer.writerow([s.id, s.name, f"{s.average:.2f}", grades_str])
    except PermissionError:
        raise CSVError(f"Нет прав на запись в файл: {path}")
    except OSError as e:
        raise CSVError(f"Ошибка записи файла {path}: {e}")