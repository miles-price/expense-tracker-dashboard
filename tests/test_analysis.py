import pandas as pd

from analysis import (
    average_transaction,
    category_summary,
    load_dataframe,
    monthly_total,
    spending_over_time,
    top_category,
    total_spent,
)


def test_load_dataframe_normalizes_rows():
    raw = [
        {"amount": "12.50", "category": "Food", "description": "Lunch", "date": "2026-02-01"},
        {"amount": 5, "category": None, "description": None, "date": "2026-02-02"},
    ]

    df = load_dataframe(raw)

    assert list(df.columns) == ["id", "amount", "category", "description", "date"]
    assert df.shape[0] == 2
    assert pd.api.types.is_datetime64_any_dtype(df["date"])


def test_aggregate_helpers():
    df = load_dataframe(
        [
            {"amount": 10, "category": "Food", "description": "", "date": "2026-02-01"},
            {"amount": 20, "category": "Food", "description": "", "date": "2026-02-02"},
            {"amount": 15, "category": "Transport", "description": "", "date": "2026-02-02"},
        ]
    )

    assert total_spent(df) == 45.0
    assert average_transaction(df) == 15.0
    assert top_category(df) == "Food"

    by_category = category_summary(df)
    assert by_category.loc["Food"] == 30

    trend = spending_over_time(df, frequency="D")
    assert len(trend) >= 2


def test_monthly_total_uses_current_month():
    today = pd.Timestamp.today().strftime("%Y-%m-%d")
    df = load_dataframe(
        [
            {"amount": 100, "category": "Bills", "description": "", "date": today},
            {"amount": 50, "category": "Bills", "description": "", "date": "2024-01-01"},
        ]
    )

    assert monthly_total(df) == 100.0
