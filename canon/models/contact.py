








from typing import Optional

from pydantic import EmailStr, Field

from canon.models.base import PydanticBase

from .address import AddressSchema


class ContactSchema(PydanticBase):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[AddressSchema]
    # company: Optional[str] = None
    notes: Optional[str] = None
    is_active: bool = Field(
        default=True,
        description="Indicates if the contact is active",
    )