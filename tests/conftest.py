"""Общие фикстуры для всех тестов."""
from __future__ import annotations

import pytest

from lab.models import Student


@pytest.fixture
def empty_students() -> list[Student]:
    """Пустой список студентов."""
    return []


@pytest.fixture
def sample_students() -> list[Student]:
    """Готовый список из 3 студентов с разными оценками."""
    return [
        Student(1, "Иванов Иван", [78, 85, 90]),
        Student(2, "Иванов Петр", [65, 70, None]),
        Student(3, "Иванова Анна", [92, 88, 95]),
    ]


@pytest.fixture
def sample_csv_file(tmp_path) -> str:
    """Создаёт временный CSV-файл с примером и возвращает путь."""
    path = tmp_path / "students.csv"
    path.write_text(
        "id,name,grade1,grade2,grade3\n"
        "1,Иванов Иван,78,85,90\n"
        "2,Иванов Петр,65,70,\n"
        "3,Иванова Анна,92,88,95\n",
        encoding="utf-8",
    )
    return str(path)