
from lab.errors import AppError, ValidationError
from lab.io_utils import export_top_n, read_csv, write_csv
from lab.models import Student
from lab.processing import (
    add_student,
    find_by_id,
    group_stats,
    remove_student,
    sort_students,
    top_n,
    update_grades,
)

def ask_int(prompt: str) -> int:
    while True:
        raw = input(prompt).strip()
        try:
            return int(raw)
        except ValueError:
            print(f"  Ошибка: нужно целое число, получено {raw!r}")


def ask_grades(prompt: str) -> list[int | None]:

    print(prompt)
    print("  Формат: числа через пробел (0..100). Пустая ячейка — пропуск.")
    print("  Enter без ввода — нет оценок. 'q' — отмена.")
    raw = input("> ").strip()

    if raw.lower() == "q":
        raise ValidationError("Ввод отменён пользователем")

    if raw == "":
        return []


    parts = raw.split()
    grades: list[int | None] = []
    for p in parts:
        if p in ("", "-", "_"):
            grades.append(None)
            continue
        try:
            g = int(p)
        except ValueError:
            raise ValidationError(f"Оценка должна быть целым числом, получено {p!r}")
        if not (0 <= g <= 100):
            raise ValidationError(f"Оценка вне диапазона 0..100: {g}")
        grades.append(g)
    return grades


def format_students_table(students: list[Student]) -> str:
    if not students:
        return "(список пуст)"

    max_grades = max((len(s.grades) for s in students), default=0)

    id_w = max(4, max(len(str(s.id)) for s in students))
    name_w = max(6, max(len(s.name) for s in students))
    grade_w = 5

    head = f"| {'id':^{id_w}} | {'name':^{name_w}} |"
    for i in range(1, max_grades + 1):
        head += f" {'gr.' + str(i):^{grade_w}} |"

    sep = "+" + "-" * (id_w + 2) + "+" + "-" * (name_w + 2) + "+"
    for _ in range(max_grades):
        sep += "-" * (grade_w + 2) + "+"

    lines = [sep, head, sep]

    for s in students:
        line = f"| {s.id:>{id_w}} | {s.name:<{name_w}} |"
        for i in range(max_grades):
            if i < len(s.grades) and s.grades[i] is not None:
                cell = str(s.grades[i])
            else:
                cell = "-"
            line += f" {cell:^{grade_w}} |"
        lines.append(line)

    lines.append(sep)
    return "\n".join(lines)


def print_stats(students: list[Student]) -> None:
    stats = group_stats(students)
    print(f"Всего студентов: {stats['count']}")
    print(f"Средний балл по группе: {stats['overall']:.2f}")
    if stats["best"] is not None:
        b = stats["best"]
        print(f"Лучший: {b.name} (id={b.id}, avg={b.average:.2f})")
    else:
        print("Лучший: —")
    if stats["worst"] is not None:
        w = stats["worst"]
        print(f"Худший: {w.name} (id={w.id}, avg={w.average:.2f})")
    else:
        print("Худший: —")



def action_load(students: list[Student]) -> list[Student]:

    path = input("Путь к CSV [data/students.csv]: ").strip() or "data/students.csv"
    loaded = read_csv(path)
    print(f"Загружено студентов: {len(loaded)}")
    return loaded


def action_save(students: list[Student]) -> None:

    path = input("Путь для сохранения [data/students.csv]: ").strip() or "data/students.csv"
    write_csv(path, students)
    print(f"Сохранено студентов: {len(students)} в {path}")


def action_show(students: list[Student]) -> None:

    print(format_students_table(students))


def action_add(students: list[Student]) -> None:

    sid = ask_int("id нового студента: ")
    name = input("ФИО: ").strip()
    grades = ask_grades("Оценки студента:")
    add_student(students, sid, name, grades)
    print(f"Добавлен: {name} (id={sid})")


def action_remove(students: list[Student]) -> None:

    sid = ask_int("id для удаления: ")
    removed = remove_student(students, sid)
    print(f"Удалён: {removed.name} (id={removed.id})")


def action_update(students: list[Student]) -> None:

    sid = ask_int("id студента: ")
    student = find_by_id(students, sid)
    if student is None:
        raise AppError(f"Студент с id={sid} не найден")
    print(f"Текущие оценки {student.name}: {student.grades}")
    new_grades = ask_grades("Новые оценки:")
    update_grades(students, sid, new_grades)
    print(f"Обновлено: {student.name} → {new_grades}")


def action_stats(students: list[Student]) -> None:

    print_stats(students)


def action_top(students: list[Student]) -> None:

    n = ask_int("N (сколько лучших выгрузить): ")
    path = input("Путь для экспорта [data/top.csv]: ").strip() or "data/top.csv"
    export_top_n(path, students, n)
    print(f"ТОП-{n} сохранён в {path}")


def action_sort(students: list[Student]) -> None:

    print("Ключ сортировки: avg | name | id")
    key = input("> ").strip().lower()
    sorted_list = sort_students(students, key)
    print(format_students_table(sorted_list))


MENU = """
==================== МЕНЮ ====================
1. Загрузить из CSV
2. Сохранить в CSV
3. Показать всех студентов
4. Добавить студента
5. Удалить студента по id
6. Обновить оценки по id
7. Показать статистику группы
8. Экспорт ТОП-N в CSV
9. Сортировать (avg | name | id)
0. Выход
==============================================
"""


def main() -> None:
    """Главный цикл приложения."""
    import json
    from pathlib import Path

    base = Path(__file__).resolve().parent.parent
    session_path = base / "data" / "session.json"

    students: list[Student] = []

    def save_session() -> None:

        try:
            data = [
                {"id": s.id, "name": s.name, "grades": s.grades}
                for s in students
            ]
            session_path.write_text(
                json.dumps(data, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
        except OSError as e:
            print(f"Не удалось сохранить состояние: {e}")

    save_session()

    while True:
        print(MENU)
        choice = input("Выбор: ").strip()
        try:
            if choice == "1":
                students = action_load(students)
                save_session()
            elif choice == "2":
                action_save(students)
            elif choice == "3":
                action_show(students)
            elif choice == "4":
                action_add(students)
                save_session()
            elif choice == "5":
                action_remove(students)
                save_session()
            elif choice == "6":
                action_update(students)
                save_session()
            elif choice == "7":
                action_stats(students)
            elif choice == "8":
                action_top(students)
            elif choice == "9":
                action_sort(students)
            elif choice == "0":
                print("До свидания!")
                break
            else:
                print(f"Неизвестный пункт меню: {choice!r}")
        except AppError as e:
            print(f"Ошибка: {e}")
        except KeyboardInterrupt:
            print("\nПрервано пользователем")
            break

if __name__ == "__main__":
    main()