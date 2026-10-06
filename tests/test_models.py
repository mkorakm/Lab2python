"""Тесты модели Student."""
from __future__ import annotations

import pytest

from lab.models import Student


def test_student_creation() -> None:
    """Студент создаётся с переданными полями."""
    s = Student(1, "Иванов Иван", [80, 90])
    assert s.id == 1
    assert s.name == "Иванов Иван"
    assert s.grades == [80, 90]


def test_average_basic() -> None:
    """Среднее считается верно для полного списка оценок."""
    s = Student(1, "Тест", [80, 90, 100])
    assert s.average == pytest.approx(90.0)


def test_average_with_none() -> None:
    """None-оценки игнорируются при расчёте среднего."""
    s = Student(1, "Тест", [80, None, 100])
    assert s.average == pytest.approx(90.0)


def test_average_empty() -> None:
    """Пустой список → 0.0."""
    s = Student(1, "Тест", [])
    assert s.average == 0.0


def test_average_all_none() -> None:
    """Список только из None → 0.0."""
    s = Student(1, "Тест", [None, None])
    assert s.average == 0.0


def test_grades_is_copy() -> None:
    """Student копирует список оценок, а не хранит ссылку."""
    original = [80, 90]
    s = Student(1, "Тест", original)
    original.append(100)
    assert s.grades == [80, 90]   # изменение original не повлияло