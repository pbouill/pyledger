from typing import TYPE_CHECKING, Any, Self

from sqlalchemy import ForeignKey, Integer, TypeDecorator
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TableNames
from .user import User

if TYPE_CHECKING:
    pass


class Permission(int):
    READ_MASK = 0b100  # 4
    WRITE_MASK = 0b010  # 2
    EXECUTE_MASK = 0b001  # 1

    def __new__(cls, value: Any) -> Self:
        return int.__new__(cls, value)

    @classmethod
    def from_mask(
        cls,
        read: bool = False,
        write: bool = False,
        execute: bool = False,
    ) -> Self:
        value = 0
        if read:
            value |= cls.READ_MASK
        if write:
            value |= cls.WRITE_MASK
        if execute:
            value |= cls.EXECUTE_MASK
        return cls(value)

    def can_read(self) -> bool:
        return bool(self & self.READ_MASK)

    def can_write(self) -> bool:
        return bool(self & self.WRITE_MASK)

    def can_execute(self) -> bool:
        return bool(self & self.EXECUTE_MASK)

    def to_mask(self) -> tuple[bool, bool, bool]:
        return (
            self.can_read(),
            self.can_write(),
            self.can_execute(),
        )

    def __str__(self) -> str:
        # Returns a string like 'rwx', 'rw-', etc.
        return (
            ("r" if self.can_read() else "-") +
            ("w" if self.can_write() else "-") +
            ("x" if self.can_execute() else "-")
        )

class PermissionType(TypeDecorator):
    impl = Integer
    cache_ok = True

    def process_bind_param(
        self, value: Permission | int | None, dialect: Any
    ) -> int | None:
        if value is None:
            return None
        if isinstance(value, Permission):
            return int(value)
        return int(Permission(value))

    def process_result_value(
        self, value: int | None, dialect: Any
    ) -> Permission | None:
        if value is None:
            return None
        return Permission(value)


class UserPermission(Base):
    __tablename__ = TableNames.USER_PERMISSION
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey(User.id),
        nullable=False,
    )
    from .user import User
    user: Mapped[User] = relationship(
        User,
        back_populates="permissions",
    )
    company_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey(f"{TableNames.COMPANY}.id"),
        nullable=False,
    )
    from .company import Company
    company: Mapped[Company] = relationship(
        Company,
        back_populates="user_permissions",
    )
    permission: Mapped[Permission] = mapped_column(
        PermissionType,
        nullable=False,
        default=lambda: Permission.from_mask(read=True),
    )