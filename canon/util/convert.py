

from typing import Any

from pydantic import BaseModel, create_model
from sqlalchemy.orm import DeclarativeMeta


def sqlalchemy_to_pydantic(
    sa_model: type[Any] | DeclarativeMeta,
    *,
    name: str | None = None,
    exclude: set[str] | None = None,
) -> type[BaseModel]:
    """
    Dynamically create a Pydantic model from a SQLAlchemy model class.
    - Only includes columns (not relationships or hybrid properties).
    - Use "exclude" to skip fields.
    - Sets from_attributes=True for Pydantic v2 compatibility.
    """
    if not hasattr(sa_model, "__mapper__"):
        raise TypeError(
            f"Provided model {sa_model} does not have a __mapper__ attribute."
        )
    exclude = exclude or set()
    # Allow any type here because we may use PEP-604 unions (e.g., "X | None")
    fields: dict[str, tuple[Any, Any]] = {}
    import datetime

    from canon.models.base import PydanticTypeDecorator
    excluded_fields = []
    allowed_types = {
        int, float, str, bool, bytes, dict, list, set, tuple, type(None),
        datetime.datetime, datetime.date, datetime.time
    }
    for attr_name, attr in sa_model.__mapper__.c.items():
        if attr_name in exclude:
            continue
        try:
            attr_type_cls = type(attr.type)
            # 1. If PydanticTypeDecorator, use its Pydantic model
            if issubclass(attr_type_cls, PydanticTypeDecorator) and hasattr(
                attr.type, "__pydantic_model__"
            ):
                python_type = attr.type.__pydantic_model__
            else:
                python_type = (
                    attr.type.python_type if hasattr(attr.type, "python_type") else Any
                )
            # 2. Use (type, ...) for required, (type | None, None) for nullable
            if attr.nullable and python_type is not Any:
                field_type: type[Any] = python_type
                default = None
            else:
                field_type = python_type
                default = ...
            # 3. Only add fields with a standard Python type or detected Pydantic model
            valid_type = False
            if isinstance(python_type, type):
                if (
                    python_type in allowed_types
                    or issubclass(python_type, BaseModel)
                ):
                    valid_type = True
            if valid_type:
                # For nullable, use type | None as the type
                if attr.nullable and python_type is not Any:
                    fields[attr_name] = (
                        field_type | type(None),
                        default,
                    )
                else:
                    fields[attr_name] = (field_type, default)
            else:
                raise TypeError(
                    f"Non-standard python_type: {python_type}"
                )
        except (NotImplementedError, TypeError) as err:
            type_info = (
                type(attr.type).__name__ if hasattr(attr, "type")
                else str(type(attr))
            )
            excluded_fields.append((attr_name, type_info, str(err)))
    # You may want to log excluded_fields here if needed
    # Build the Pydantic model
    model_name = name or f"{sa_model.__name__}Pydantic"
    # Always inherit from PydanticBase for config
    from canon.models.base import PydanticBase
    model_fields: dict[str, Any] = {
        k: v[0] if v[1] is ... else (v[0], v[1])
        for k, v in fields.items()
    }
    return create_model(
        model_name,
        __base__=PydanticBase,
        **model_fields,
    )
    