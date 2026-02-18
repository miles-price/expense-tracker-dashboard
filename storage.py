from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from expense import Expense

FILE_NAME = Path("data.json")


def _write_json(payload: list[dict[str, Any]]) -> None:
    FILE_NAME.write_text(json.dumps(payload, indent=4), encoding="utf-8")


def load_expenses() -> list[dict[str, Any]]:
    if not FILE_NAME.exists():
        return []

    try:
        raw = json.loads(FILE_NAME.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []

    if not isinstance(raw, list):
        return []

    normalized: list[dict[str, Any]] = []
    has_changes = False

    for item in raw:
        if not isinstance(item, dict):
            has_changes = True
            continue

        expense = Expense.from_dict(item)
        normalized_item = expense.to_dict()
        normalized.append(normalized_item)

        if normalized_item != item:
            has_changes = True

    if has_changes:
        _write_json(normalized)

    return normalized


def save_all_expenses(expenses: list[dict[str, Any]]) -> None:
    cleaned = [Expense.from_dict(item).to_dict() for item in expenses]
    _write_json(cleaned)


def save_expense(expense: dict[str, Any]) -> dict[str, Any]:
    expenses = load_expenses()
    normalized = Expense.from_dict(expense).to_dict()
    expenses.append(normalized)
    _write_json(expenses)
    return normalized


def delete_expense(expense_id: str) -> bool:
    expenses = load_expenses()
    remaining = [item for item in expenses if item.get("id") != expense_id]

    if len(remaining) == len(expenses):
        return False

    _write_json(remaining)
    return True
