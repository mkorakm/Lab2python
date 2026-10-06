"""Тесты функций обработки."""
from __future__ import annotations

import pytest

from lab.errors import DuplicateIdError, StudentNotFoundError, ValidationError
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


def test_find_by_id_found(sample_students) -> None:
    """Находит студента по существующему id."""
    s = find_by_id(sample_students, 2)
    assert s is not None
    assert s.name == "Иванов Петр"


def test_find_by_id_not_found(sample_students) -> None:
    """Возвращает None, если студента нет."""
    assert find_by_id(sample_students, 999) is None

def test_add_student_ok(empty_students) -> None:
    """Добавляет нового студента."""
    s = add_student(empty_students, 1, "Тестов Тест", [80, 90])
    assert len(empty_students) == 1
    assert s.id == 1
    assert s.name == "Тестов Тест"


def test_add_student_duplicate(sample_students) -> None:
    """Дубликат id → DuplicateIdError."""
    with pytest.raises(DuplicateIdError):
        add_student(sample_students, 1, "Другой", [50])


def test_add_student_empty_name(empty_students) -> None:
    """Пустое имя → ValidationError."""
    with pytest.raises(ValidationError):
        add_student(empty_students, 1, "   ", [80])


def test_add_student_bad_grade(empty_students) -> None:
    """Оценка вне диапазона → ValidationError."""
    with pytest.raises(ValidationError):
        add_student(empty_students, 1, "Тест", [150])


def test_remove_student_ok(sample_students) -> None:
    """Удаляет студента и возвращает его."""
    removed = remove_student(sample_students, 1)
    assert removed.name == "Иванов Иван"
    assert len(sample_students) == 2
    assert find_by_id(sample_students, 1) is None


def test_remove_student_not_found(sample_students) -> None:
    """Нет студента → StudentNotFoundError."""
    with pytest.raises(StudentNotFoundError):
        remove_student(sample_students, 999)

def test_update_grades_ok(sample_students) -> None:
    """Обновляет оценки."""
    update_grades(sample_students, 1, [100, 100])
    s = find_by_id(sample_students, 1)
    assert s is not None
    assert s.grades == [100, 100]


def test_update_grades_with_none(sample_students) -> None:
    """Обновление с None-оценками (пустые)."""
    update_grades(sample_students, 1, [80, None, 90])
    s = find_by_id(sample_students, 1)
    assert s is not None
    assert s.grades == [80, None, 90]


def test_update_grades_bad_value(sample_students) -> None:
    """Оценка вне диапазона → ValidationError."""
    with pytest.raises(ValidationError):
        update_grades(sample_students, 1, [200])


def test_update_grades_not_found(sample_students) -> None:
    """Нет студента → StudentNotFoundError."""
    with pytest.raises(StudentNotFoundError):
        update_grades(sample_students, 999, [80])


def test_sort_by_avg(sample_students) -> None:
    """Сортировка по убыванию среднего."""
    result = sort_students(sample_students, "avg")
    assert [s.id for s in result] == [3, 1, 2]


def test_sort_by_name(sample_students) -> None:
    """Сортировка по имени."""
    result = sort_students(sample_students, "name")
    assert [s.name for s in result] == ["Иванов Иван", "Иванов Петр", "Иванова Анна"]


def test_sort_by_id(sample_students) -> None:
    """Сортировка по id."""
    result = sort_students(sample_students, "id")
    assert [s.id for s in result] == [1, 2, 3]


def test_sort_bad_key(sample_students) -> None:
    """Неизвестный ключ → ValidationError."""
    with pytest.raises(ValidationError):
        sort_students(sample_students, "unknown")


def test_sort_does_not_mutate(sample_students) -> None:
    """Сортировка не меняет исходный список."""
    original = [s.id for s in sample_students]
    sort_students(sample_students, "avg")
    assert [s.id for s in sample_students] == original

def test_group_stats_empty(empty_students) -> None:
    """Пустой список → count=0, overall=0.0, best=None, worst=None."""
    stats = group_stats(empty_students)
    assert stats["count"] == 0
    assert stats["overall"] == 0.0
    assert stats["best"] is None
    assert stats["worst"] is None


def test_group_stats_nonempty(sample_students) -> None:
    """Статистика на непустом списке."""
    stats = group_stats(sample_students)
    assert stats["count"] == 3
    # Все оценки: 78,85,90,65,70,92,88,95 = 663 / 8 = 82.875
    assert stats["overall"] == pytest.approx(82.875)
    assert stats["best"].id == 3        # Анна, avg ~91.67
    assert stats["worst"].id == 2       # Петр, avg ~67.5


def test_top_n_basic(sample_students) -> None:
    """ТОП-2 — два лучших по среднему."""
    result = top_n(sample_students, 2)
    assert len(result) == 2
    assert result[0].id == 3   # Анна
    assert result[1].id == 1   # Иван


def test_top_n_more_than_exists(sample_students) -> None:
    """N больше, чем студентов → возвращает всех."""
    result = top_n(sample_students, 100)
    assert len(result) == 3


def test_top_n_bad_n(sample_students) -> None:
    """N <= 0 → ValidationError."""
    with pytest.raises(ValidationError):
        top_n(sample_students, 0)