from typing import Callable, Type

from pydantic import BaseModel

from bootstrap.db.models import Base

from bootstrap.exceptions import DetailedError


class DoesNotExists(DetailedError):
    default_message: str = 'Does not exists.'


def get_conditions(model, **filters) -> list:
    def _get_cond(key, value):
        if isinstance(value, bool):
            return getattr(model, key).is_(value)
        elif isinstance(value, list):
            return getattr(model, key).in_(value)
        elif isinstance(value, Callable):
            return value(getattr(model, key))
        return getattr(model, key) == value

    return [
        _get_cond(key, value)
        for key, value in filters.items()
    ]


def get_returning_fields(model: Type[Base], dto: Type[BaseModel]) -> list[str]:
    return [
        getattr(model, field)
        for field in dto.model_fields.keys()
        if hasattr(model, field)
    ]
