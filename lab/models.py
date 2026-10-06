
class Student:

    def __init__(self, id: int, name: str, grades: list[int | None]) -> None:
        self.id = id
        self.name = name
        self.grades = list(grades)

    @property
    def average(self) -> float:
        valid = [g for g in self.grades if g is not None]
        if not valid:
            return 0.0
        return sum(valid) / len(valid)

    def __repr__(self) -> str:
        return f"Student(id={self.id!r}, name={self.name!r}, grades={self.grades!r})"