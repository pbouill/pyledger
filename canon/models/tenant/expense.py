from .base import TenantBase
from sqlalchemy import Integer, String, Float, Column, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime

class Expense(TenantBase):
    __tablename__ = "expense"
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("project.id"), nullable=True)
    employee_id = Column(Integer, ForeignKey("employee.id"), nullable=True)
    wbs4_id = Column(Integer, ForeignKey("project_wbs4.id"), nullable=True)
    due_date = Column(DateTime, nullable=True)
    submitted_date = Column(DateTime, nullable=True)
    status = Column(String, nullable=True)
    total = Column(Float, nullable=True)
    notes = Column(Text, nullable=True)
    items = relationship("ExpenseItem", back_populates="expense")

    async def recalculate_total(self, session) -> float:
        """Recalculate and persist the expense total from its items."""
        from sqlalchemy import select, func
        # Local import to avoid circular import issues
        from .expense_item import ExpenseItem

        res = await session.execute(select(func.coalesce(func.sum(ExpenseItem.value), 0)).where(ExpenseItem.expense_id == self.id))
        total = res.scalar_one()
        self.total = float(total)
        session.add(self)
        await session.flush()
        return self.total
