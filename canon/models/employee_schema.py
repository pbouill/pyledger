from typing import Any, Dict, Optional

from canon.models.base import PydanticBase


class EmployeeSchema(PydanticBase):
    first_name: str
    last_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    SIN: Optional[str] = None
    # Arbitrary mapping for TD1 and other payroll-specific per-employee overrides
    payroll_tax_deductions: Optional[Dict[str, Any]] = None
