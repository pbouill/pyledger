from typing import Optional, TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func


from .base import Base, TableNames
from .relationships import get_parent_relationship_def, build_single_relationship

if TYPE_CHECKING:
    from .company import Company
    from .user_permission import UserPermission

PERMISSIONS_RELATIONSHIP_DEF = TableNames.USER_PERMISSION, get_parent_relationship_def(
    TableNames.USER, TableNames.USER_PERMISSION
)


class User(Base):
    __tablename__ = TableNames.USER
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(150), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    oauth_provider: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    oauth_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    permissions: Mapped[list["UserPermission"]] = build_single_relationship(*PERMISSIONS_RELATIONSHIP_DEF)

    @property
    def companies(self) -> set["Company"]:
        return {up.company for up in self.permissions}