"""Тесты чтения/записи CSV."""
import pytest

from lab.errors import CSVError, ValidationError
from lab.io_utils import export_top_n, read_csv, write_csv
from lab.models import Student


def test_read_csv_with_header(sample_csv_file) -> None:
    """Чтение CSV с заголовком."""
    students = read_csv(sample_csv_file)
    assert len(students) == 3
    assert students[0].id == 1
    assert students[0].name == "Иванов Иван"
    assert students[0].grades == [78, 85, 90]


def test_read_csv_with_empty_cells(tmp_path) -> None:
    """Пустые ячейки → None."""
    path = tmp_path / "in.csv"
    path.write_text(
        "id,name,grade1,grade2,grade3\n"
        "1,Олег,100,90,\n"
        "2,Юлия,80,,\n",
        encoding="utf-8",
    )
    students = read_csv(str(path))
    assert students[0].grades == [100, 90, None]
    assert students[1].grades == [80, None, None]


def test_read_csv_without_header(tmp_path) -> None:
    """CSV без заголовка — первая строка сразу данные."""
    path = tmp_path / "in.csv"
    path.write_text(
        "1,Иванов Иван,78,85\n"
        "2,Иванов Петр,65,70\n",
        encoding="utf-8",
    )
    students = read_csv(str(path))
    assert len(students) == 2
    assert students[0].id == 1


def test_read_csv_file_not_found() -> None:
    """Несуществующий файл → CSVError."""
    with pytest.raises(CSVError):
        read_csv("no_such_file.csv")


def test_read_csv_bad_id(tmp_path) -> None:
    """Нечисловой id → CSVError."""
    path = tmp_path / "in.csv"
    path.write_text("id,name\nabc,Тест\n", encoding="utf-8")
    with pytest.raises(CSVError):
        read_csv(str(path))


def test_read_csv_duplicate_id(tmp_path) -> None:
    """Дубликат id в файле → CSVError."""
    path = tmp_path / "in.csv"
    path.write_text(
        "id,name\n1,A\n1,B\n",
        encoding="utf-8",
    )
    with pytest.raises(CSVError):
        read_csv(str(path))


def test_read_csv_grade_out_of_range(tmp_path) -> None:
    """Оценка > 100 → CSVError."""
    path = tmp_path / "in.csv"
    path.write_text("id,name,grade1\n1,A,150\n", encoding="utf-8")
    with pytest.raises(CSVError):
        read_csv(str(path))


def test_read_csv_empty_file(tmp_path) -> None:
    """Пустой файл → пустой список."""
    path = tmp_path / "in.csv"
    path.write_text("", encoding="utf-8")
    assert read_csv(str(path)) == []

def test_write_and_read_round_trip(tmp_path, sample_students) -> None:
    """Записали → прочитали → получили то же."""
    path = tmp_path / "out.csv"
    write_csv(str(path), sample_students)
    loaded = read_csv(str(path))
    assert len(loaded) == len(sample_students)
    for orig, back in zip(sample_students, loaded):
        assert orig.id == back.id
        assert orig.name == back.name
        assert orig.grades == back.grades


def test_write_csv_aligns_columns(tmp_path) -> None:
    """Строки выравниваются по максимальному числу оценок."""
    students = [
        Student(1, "A", [80, 90, 100]),
        Student(2, "B", [70]),
    ]
    path = tmp_path / "out.csv"
    write_csv(str(path), students)
    content = path.read_text(encoding="utf-8")
    lines = content.strip().split("\n")
    # Заголовок + 2 строки, все по 5 колонок
    assert lines[0] == "id,name,grade1,grade2,grade3"
    assert lines[1] == "1,A,80,90,100"
    assert lines[2] == "2,B,70,,"        # добито пустыми


def test_write_csv_none_as_empty(tmp_path) -> None:
    """None в оценках → пустая ячейка в файле."""
    students = [Student(1, "A", [80, None, 90])]
    path = tmp_path / "out.csv"
    write_csv(str(path), students)
    content = path.read_text(encoding="utf-8")
    assert "80,,90" in content


def test_export_top_n(tmp_path, sample_students) -> None:
    """Экспорт ТОП-2."""
    path = tmp_path / "top.csv"
    export_top_n(str(path), sample_students, 2)
    content = path.read_text(encoding="utf-8")
    lines = content.strip().split("\n")
    assert lines[0] == "id,name,average,grades"
    assert "3,Иванова Анна" in lines[1]   # лучший
    assert "1,Иванов Иван" in lines[2]


def test_export_top_n_bad_n(tmp_path, sample_students) -> None:
    """N <= 0 → ValidationError."""
    with pytest.raises(ValidationError):
        export_top_n(str(tmp_path / "top.csv"), sample_students, 0)