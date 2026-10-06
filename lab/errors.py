

class AppError(Exception):
    """Базовое исключение приложения
    """


class ValidationError(AppError):
    """Ошибка валидации данных
    """


class CSVError(AppError):
    """Ошибка при работе с CSV-файлом
    """


class DuplicateIdError(AppError):
    """Студент с таким id уже существует
    """


class StudentNotFoundError(AppError):
    """Студент с указанным id не найден
    """