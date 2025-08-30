"""
Кастомные исключения для приложения
"""

from fastapi import HTTPException, status


class ValidationError(HTTPException):
    """Ошибка валидации данных"""

    def __init__(self, detail: str):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


class NotFoundError(HTTPException):
    """Ошибка - ресурс не найден"""

    def __init__(self, resource: str, resource_id: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{resource} с ID {resource_id} не найден",
        )


class ConflictError(HTTPException):
    """Ошибка конфликта (например, дублирование уникального поля)"""

    def __init__(self, detail: str):
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail)


class DatabaseError(HTTPException):
    """Ошибка базы данных"""

    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка базы данных: {detail}",
        )


class BusinessLogicError(HTTPException):
    """Ошибка бизнес-логики"""

    def __init__(self, detail: str):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)
