from pydantic import BaseModel
from typing import TypeVar

T = TypeVar("T", bound=BaseModel)


def mapper(source: BaseModel, target: type[T]) -> T:
    return target.model_validate(source.model_dump())
