"""Тесты CLI через monkeypatch и capsys."""
from __future__ import annotations

import pytest

from lab import main as main_module
from lab.main import ask_grades, ask_int, format_students_table
from lab.models import Student


def test_ask_int_ok(monkeypatch) -> None:
    """Ввод целого числа."""
    monkeypatch.setattr("builtins.input", lambda prompt="": "42")
    assert ask_int("id: ") == 42


def test_ask_int_retries_on_bad(monkeypatch, capsys) -> None:
    """Сначала буквы, потом число — должен переспросить."""
    answers = iter(["abc", "42"])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(answers))
    assert ask_int("id: ") == 42
    out = capsys.readouterr().out
    assert "Ошибка" in out

def test_ask_grades_numbers(monkeypatch) -> None:
    """Обычный ввод оценок."""
    monkeypatch.setattr("builtins.input", lambda prompt="": "80 90 100")
    assert ask_grades(": ") == [80, 90, 100]


def test_ask_grades_empty(monkeypatch) -> None:
    """Пустой ввод → пустой список."""
    monkeypatch.setattr("builtins.input", lambda prompt="": "")
    assert ask_grades(": ") == []


def test_ask_grades_with_dash(monkeypatch) -> None:
    """Прочерк → None (пустая оценка)."""
    monkeypatch.setattr("builtins.input", lambda prompt="": "80 - 90")
    assert ask_grades(": ") == [80, None, 90]


def test_format_table_empty() -> None:
    """Пустой список → сообщение."""
    assert "пуст" in format_students_table([])


def test_format_table_contains_data() -> None:
    """Таблица содержит id, имя, оценки."""
    students = [
        Student(1, "Иванов Иван", [80, 90]),
        Student(2, "Петров Петр", [70, None]),
    ]
    table = format_students_table(students)
    assert "Иванов Иван" in table
    assert "Петров Петр" in table
    assert "80" in table
    assert "90" in table
    # None показывается как прочерк
    assert "-" in table


def test_main_exit(monkeypatch, capsys) -> None:
    """Выбор '0' → выход."""
    monkeypatch.setattr("builtins.input", lambda prompt="": "0")
    main_module.main()
    out = capsys.readouterr().out
    assert "До свидания" in out


def test_main_unknown_choice(monkeypatch, capsys) -> None:
    """Неизвестный пункт → сообщение, но не падаем."""
    answers = iter(["abc", "0"])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(answers))
    main_module.main()
    out = capsys.readouterr().out
    assert "Неизвестный пункт" in out


def test_main_show_empty(monkeypatch, capsys) -> None:
    """Показать пустой список → не падаем."""
    answers = iter(["3", "0"])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(answers))
    main_module.main()
    out = capsys.readouterr().out
    assert "пуст" in out


def test_main_add_student(monkeypatch, capsys) -> None:
    """Сценарий: добавить студента и показать."""
    answers = iter([
        "4",            # меню — добавить
        "10",           # id
        "Тестов Тест",  # имя
        "50 60 70",     # оценки
        "3",            # показать
        "0",            # выход
    ])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(answers))
    main_module.main()
    out = capsys.readouterr().out
    assert "Добавлен" in out
    assert "Тестов Тест" in out


def test_main_remove_not_found(monkeypatch, capsys) -> None:
    """Удаление несуществующего → ошибка, но программа не падает."""
    answers = iter([
        "5",     # удалить
        "999",   # id
        "0",     # выход
    ])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(answers))
    main_module.main()
    out = capsys.readouterr().out
    assert "не найден" in out.lower()