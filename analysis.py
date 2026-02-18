import pandas as pd

def load_dataframe(expenses):
    """
    Convert list of expense dictionaries into a pandas DataFrame.
    Ensures expected columns exist even if list is empty.
    """
    if not expenses:
        return pd.DataFrame(columns=["amount", "category", "description", "date"])
    return pd.DataFrame(expenses)

def total_spent(df):
    return df["amount"].sum()

def category_summary(df):
    return df.groupby("category")["amount"].sum().sort_values(ascending=False)

def spending_over_time(df):
    df = df.copy()
    df["date"] = pd.to_datetime(df["date"])
    # Group by calendar day
    return df.groupby(df["date"].dt.date)["amount"].sum()