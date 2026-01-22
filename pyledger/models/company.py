
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, ForeignKey, Integer, LargeBinary, String
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from .address import AddressSchema, AddressType
from .base import Base, TableNames
from .company_settings import CompanySettingsSchema, CompanySettingsType
from .currency import Currency

if TYPE_CHECKING:
    from .user import User


class Company(Base):
    __tablename__ = TableNames.COMPANY
    user_permissions = relationship(
        "UserPermission",
        back_populates="company",
        cascade="all, delete-orphan",
    )
    users = association_proxy("user_permissions", "user")
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    legal_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    tax_number: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    address: Mapped[Optional[AddressSchema]] = mapped_column(
        AddressType, nullable=True
    )  # JSON-serialized address
    currency_code: Mapped[Optional[str]] = mapped_column(
        String(8),
        ForeignKey(f"{TableNames.CURRENCY}.code"),
        nullable=True,
    )
    currency: Mapped[Optional[Currency]] = relationship("Currency")
    logo_blob: Mapped[Optional[bytes]] = mapped_column(LargeBinary, nullable=True)
    settings: Mapped[Optional[CompanySettingsSchema]] = mapped_column(
        CompanySettingsType, nullable=True
    )
    primary_contact_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey(f"{TableNames.USER}.id"),
        nullable=True,
    )
    primary_contact: Mapped[Optional["User"]] = relationship(
        "User", foreign_keys=[primary_contact_id]
    )
    created_at: Mapped[Optional[DateTime]] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[Optional[DateTime]] = mapped_column(
        DateTime(timezone=True), onupdate=func.now()
    )
    users = association_proxy("user_permissions", "user")
