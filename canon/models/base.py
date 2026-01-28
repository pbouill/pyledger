








import json
from enum import StrEnum, auto
from typing import Any, Generic, Optional, Self, Type, TypeVar, get_args

from pydantic import BaseModel, ConfigDict
from sqlalchemy import DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql import func
from sqlalchemy.types import String, TypeDecorator


# Canonical DRY Pydantic base class for all models
class PydanticBase(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        arbitrary_types_allowed=True,
    )


class Base(DeclarativeBase):
    created_at: Mapped[Optional[DateTime]] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), sort_order=100
    )
    updated_at: Mapped[Optional[DateTime]] = mapped_column(
        DateTime(timezone=True), onupdate=func.now(), sort_order=101
    )

    @classmethod
    def get_class_by_table_name(cls, table_name: str) -> Optional[Type[Self]]:
        for subcls in cls.registry._class_registry.values():
            if isinstance(subcls, type):
                if issubclass(subcls, cls):
                    if subcls.__tablename__ == table_name:
                        return subcls
        return None

T = TypeVar("T", bound=BaseModel)

class PydanticTypeDecorator(TypeDecorator, Generic[T]):
    """
    Generic SQLAlchemy TypeDecorator for serializing/deserializing Pydantic models.
    Usage: subclass as PydanticTypeDecorator[YourModel].
    """
    impl = String
    cache_ok = True
    __pydantic_model__: Type[BaseModel]

    def __init_subclass__(cls) -> None:
        super().__init_subclass__()
        # Automatically set __pydantic_model__ from generic type argument
        args = get_args(cls)
        if args:
            cls.__pydantic_model__ = args[0]

    def process_bind_param(self, value: T | dict | None, dialect: Any) -> str | None:
        if value is None:
            return None
        if isinstance(value, self.__pydantic_model__):
            return value.model_dump_json()
        return json.dumps(value)

    def process_result_value(self, value: str | None, dialect: Any) -> T | None:
        if value is None:
            return None
        elif issubclass(self.__pydantic_model__, BaseModel):
            return self.__pydantic_model__.model_validate_json(value)  # type: ignore[return-value]
        else:
            raise TypeError("Unsupported Pydantic model type for deserialization.")


class TableNames(StrEnum):
    COMPANY = auto()
    USER = auto()
    CURRENCY = auto()
    CURRENCY_RATE = auto()
    USER_PERMISSION = auto()
    # Add more table names as needed