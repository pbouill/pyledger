







import logging
from typing import TYPE_CHECKING, Optional

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .address import AddressType
from .base import Base, TableNames
from .company_settings import CompanySettingsSchema, CompanySettingsType
from .currency import Currency
from .relationships import build_single_relationship, get_parent_relationship_def
from .user import User

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from .user_permission import UserPermission

USER_PERMISSIONS_RELATIONSHIP_DEF = (
    TableNames.USER_PERMISSION,
    get_parent_relationship_def(TableNames.COMPANY, TableNames.USER_PERMISSION),
)

class Company(Base):
    __tablename__ = TableNames.COMPANY
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    legal_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    tax_number: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    address: Mapped[Optional[dict]] = mapped_column(AddressType, nullable=True)
    currency_code: Mapped[Optional[str]] = mapped_column(
        String(8), ForeignKey(Currency.code), nullable=True
    )
    currency: Mapped[Optional[Currency]] = relationship(
        Currency,
        foreign_keys=[currency_code],
        uselist=False,
    )
    logo_blob: Mapped[Optional[bytes]] = mapped_column(nullable=True)
    settings: Mapped[Optional[CompanySettingsSchema]] = mapped_column(
        CompanySettingsType, nullable=True
    )
    primary_contact_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey(User.id), nullable=True
    )
    primary_contact: Mapped[Optional[User]] = relationship(
        User,
        foreign_keys=[primary_contact_id],
        uselist=False,
    )
    user_permissions: Mapped[list["UserPermission"]] = build_single_relationship(
        *USER_PERMISSIONS_RELATIONSHIP_DEF
    )

    @property
    def users(self) -> set[User]:
        return {up.user for up in self.user_permissions}

