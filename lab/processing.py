from lab.errors import (
    DuplicateIdError,
    StudentNotFoundError,
    ValidationError,
)
from lab.models import Student


def find_by_id(students: list[Student], student_id: int) -> Student | None:
    for s in students:
        if s.id == student_id:
            return s
    return None


def add_student(students: list[Student],student_id: int,name: str,grades: list[int | None]) -> Student:

    validate_student_data(student_id, name, grades)
    if find_by_id(students, student_id) is not None:
        raise DuplicateIdError(f"Студент с id={student_id} уже существует")

    student = Student(student_id, name, grades)
    students.append(student)
    return student


def remove_student(students: list[Student], student_id: int) -> Student:

    student = find_by_id(students, student_id)
    if student is None:
        raise StudentNotFoundError(f"Студент с id={student_id} не найден")
    students.remove(student)
    return student


def update_grades(students: list[Student], student_id: int,new_grades: list[int | None]) -> Student:

    validate_grades(new_grades)
    student = find_by_id(students, student_id)
    if student is None:
        raise StudentNotFoundError(f"Студент с id={student_id} не найден")
    student.grades = list(new_grades)
    return student


def validate_student_data(student_id: int,name: str,grades: list[int | None]) -> None:

    if not isinstance(student_id, int) or student_id < 0:
        raise ValidationError(f"id должен быть неотрицательным целым, получено {student_id!r}")
    if not isinstance(name, str) or not name.strip():
        raise ValidationError("Имя не может быть пустым")
    validate_grades(grades)


def validate_grades(grades: list[int | None]) -> None:

    for g in grades:
        if g is None:
            continue
        if not isinstance(g, int) or isinstance(g, bool):
            raise ValidationError(f"Оценка должна быть целым числом, получено {g!r}")
        if not (0 <= g <= 100):
            raise ValidationError(f"Оценка должна быть в диапазоне 0..100, получено {g}")


def sort_students(students: list[Student], key: str) -> list[Student]:

    if key == "avg":
        return sorted(students, key=lambda s: (-s.average, s.name))
    if key == "name":
        return sorted(students, key=lambda s: s.name)
    if key == "id":
        return sorted(students, key=lambda s: s.id)
    raise ValidationError(f"Неизвестный ключ сортировки: {key!r}. Ожидается avg, name или id")


def group_stats(students: list[Student]) -> dict:

    count = len(students)

    all_grades = [g for s in students for g in s.grades if g is not None]
    overall = sum(all_grades) / len(all_grades) if all_grades else 0.0

    best = max(students, key=lambda s: s.average, default=None)
    worst = min(students, key=lambda s: s.average, default=None)

    return {
        "count": count,
        "overall": overall,
        "best": best,
        "worst": worst,
    }


def top_n(students: list[Student], n: int) -> list[Student]:

    if n <= 0:
        raise ValidationError(f"N должно быть положительным, получено {n}")
    return sort_students(students, "avg")[:n]