from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from typing import Any
from uuid import uuid4


@dataclass
class Expense:
    """Canonical expense record used by the app and persistence layer."""

    amount: float
    category: str
    description: str = ""
    expense_date: date | None = None
    expense_id: str | None = None

    def __post_init__(self) -> None:
        self.amount = round(float(self.amount), 2)
        self.category = self.category.strip()
        self.description = self.description.strip()

        if self.expense_date is None:
            self.expense_date = datetime.now().date()
        elif isinstance(self.expense_date, datetime):
            self.expense_date = self.expense_date.date()

        if not self.expense_id:
            self.expense_id = str(uuid4())

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "Expense":
        raw_date = payload.get("date")
        parsed_date = None

        if isinstance(raw_date, str):
            # Support both historical format "%Y-%m-%d %H:%M:%S" and ISO date.
            for fmt in ("%Y-%m-%d", "%Y-%m-%d %H:%M:%S"):
                try:
                    parsed_date = datetime.strptime(raw_date, fmt).date()
                    break
                except ValueError:
                    continue

        return cls(
            amount=payload.get("amount", 0),
            category=str(payload.get("category", "")),
            description=str(payload.get("description", "")),
            expense_date=parsed_date,
            expense_id=payload.get("id"),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.expense_id,
            "amount": self.amount,
            "category": self.category,
            "description": self.description,
            "date": self.expense_date.isoformat() if self.expense_date else None,
        }
