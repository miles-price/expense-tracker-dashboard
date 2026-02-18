from __future__ import annotations

import pandas as pd


COLUMNS = ["id", "amount", "category", "description", "date"]


def load_dataframe(expenses: list[dict]) -> pd.DataFrame:
    if not expenses:
        return pd.DataFrame(columns=COLUMNS)

    df = pd.DataFrame(expenses)

    for col in COLUMNS:
        if col not in df.columns:
            df[col] = None

    df = df[COLUMNS].copy()
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0.0)
    df["category"] = df["category"].fillna("Uncategorized").astype(str).str.strip()
    df["description"] = df["description"].fillna("").astype(str)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")

    return df.dropna(subset=["date"]).sort_values("date")


def total_spent(df: pd.DataFrame) -> float:
    return float(df["amount"].sum()) if not df.empty else 0.0


def category_summary(df: pd.DataFrame) -> pd.Series:
    if df.empty:
        return pd.Series(dtype=float)
    return df.groupby("category")["amount"].sum().sort_values(ascending=False)


def spending_over_time(df: pd.DataFrame, frequency: str = "D") -> pd.Series:
    if df.empty:
        return pd.Series(dtype=float)

    return (
        df.set_index("date")["amount"]
        .resample(frequency)
        .sum()
        .sort_index()
    )


def monthly_total(df: pd.DataFrame) -> float:
    if df.empty:
        return 0.0

    current_period = pd.Timestamp.today().to_period("M")
    month_df = df[df["date"].dt.to_period("M") == current_period]
    return float(month_df["amount"].sum())


def average_transaction(df: pd.DataFrame) -> float:
    if df.empty:
        return 0.0
    return float(df["amount"].mean())


def top_category(df: pd.DataFrame) -> str:
    summary = category_summary(df)
    if summary.empty:
        return "N/A"
    return str(summary.index[0])
