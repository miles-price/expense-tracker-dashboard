from __future__ import annotations

from datetime import date

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from analysis import (
    average_transaction,
    category_summary,
    load_dataframe,
    monthly_total,
    spending_over_time,
    top_category,
    total_spent,
)
from expense import Expense
from storage import delete_expense, load_expenses, save_expense

st.set_page_config(page_title="Personal Expense Tracker", layout="wide")
st.title("Personal Expense Tracker")
st.caption("Track spending, monitor your monthly budget, and export clean data for analysis.")


# Sidebar controls
st.sidebar.header("Controls")
menu = st.sidebar.radio("Navigation", ["Add Expense", "Dashboard", "Manage Data"])
monthly_budget = st.sidebar.number_input(
    "Monthly budget ($)",
    min_value=0.0,
    value=float(st.session_state.get("monthly_budget", 2000.0)),
    step=50.0,
)
st.session_state["monthly_budget"] = monthly_budget


def _load_df() -> pd.DataFrame:
    return load_dataframe(load_expenses())


def _usd(value: float) -> str:
    return f"${value:,.2f}"


if menu == "Add Expense":
    st.subheader("Add a New Expense")

    existing_categories = sorted(
        {
            item.get("category", "").strip()
            for item in load_expenses()
            if item.get("category")
        }
    )

    with st.form("add_expense_form", clear_on_submit=True):
        amount = st.number_input("Amount ($)", min_value=0.01, format="%.2f")
        category_choice = st.selectbox(
            "Category",
            existing_categories + ["Add new category"] if existing_categories else ["Add new category"],
        )

        category = (
            st.text_input("New category").strip()
            if category_choice == "Add new category"
            else category_choice
        )

        description = st.text_input("Description (optional)").strip()
        expense_date = st.date_input("Date", value=date.today())
        submitted = st.form_submit_button("Save Expense")

        if submitted:
            if not category:
                st.error("Category is required.")
            else:
                expense = Expense(
                    amount=amount,
                    category=category,
                    description=description,
                    expense_date=expense_date,
                )
                save_expense(expense.to_dict())
                st.success("Expense saved.")

    st.info("Tip: keep category names consistent (e.g., use either 'Food' or 'Groceries', not both).")

elif menu == "Dashboard":
    st.subheader("Dashboard")

    df = _load_df()
    if df.empty:
        st.info("No expenses yet. Add your first expense from the Add Expense page.")
        st.stop()

    min_date = df["date"].min().date()
    max_date = df["date"].max().date()

    filter_col1, filter_col2, filter_col3 = st.columns([2, 2, 1])

    with filter_col1:
        selected_categories = st.multiselect(
            "Filter by category",
            options=sorted(df["category"].unique().tolist()),
            default=sorted(df["category"].unique().tolist()),
        )

    with filter_col2:
        start_date, end_date = st.date_input(
            "Date range",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date,
        )

    with filter_col3:
        min_amount, max_amount = st.slider(
            "Amount range",
            min_value=float(df["amount"].min()),
            max_value=float(df["amount"].max()),
            value=(float(df["amount"].min()), float(df["amount"].max())),
        )

    filtered_df = df[
        (df["category"].isin(selected_categories))
        & (df["date"].dt.date >= start_date)
        & (df["date"].dt.date <= end_date)
        & (df["amount"] >= min_amount)
        & (df["amount"] <= max_amount)
    ].copy()

    if filtered_df.empty:
        st.warning("No expenses match your current filters.")
        st.stop()

    total = total_spent(filtered_df)
    monthly_spend = monthly_total(filtered_df)
    avg_txn = average_transaction(filtered_df)
    top = top_category(filtered_df)

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Spent", _usd(total))
    m2.metric("This Month", _usd(monthly_spend))
    m3.metric("Avg Transaction", _usd(avg_txn))
    m4.metric("Top Category", top)

    if monthly_budget > 0:
        utilization = min(monthly_spend / monthly_budget, 1.0)
        st.progress(utilization, text=f"Budget used: {_usd(monthly_spend)} / {_usd(monthly_budget)}")
        if monthly_spend > monthly_budget:
            st.error(f"Over budget by {_usd(monthly_spend - monthly_budget)} this month.")

    c1, c2 = st.columns(2)

    with c1:
        st.markdown("### Spending by Category")
        cat_data = category_summary(filtered_df)
        fig1, ax1 = plt.subplots()
        cat_data.plot(kind="bar", ax=ax1, color="#ff8c42")
        ax1.set_xlabel("Category")
        ax1.set_ylabel("Amount ($)")
        ax1.tick_params(axis="x", rotation=30)
        st.pyplot(fig1)

    with c2:
        st.markdown("### Spending Trend")
        trend = spending_over_time(filtered_df, frequency="D")
        fig2, ax2 = plt.subplots()
        trend.plot(kind="line", ax=ax2, marker="o", color="#2a9d8f")
        ax2.set_xlabel("Date")
        ax2.set_ylabel("Amount ($)")
        ax2.tick_params(axis="x", rotation=30)
        st.pyplot(fig2)

    st.markdown("### Recent Transactions")
    display_df = filtered_df.sort_values("date", ascending=False).copy()
    display_df["date"] = display_df["date"].dt.strftime("%Y-%m-%d")
    st.dataframe(display_df[["date", "category", "description", "amount"]], use_container_width=True)

    csv_data = display_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Download filtered data as CSV",
        data=csv_data,
        file_name="filtered_expenses.csv",
        mime="text/csv",
    )

elif menu == "Manage Data":
    st.subheader("Manage Saved Expenses")
    df = _load_df()

    if df.empty:
        st.info("No data to manage yet.")
        st.stop()

    manage_df = df.sort_values("date", ascending=False).copy()
    manage_df["date"] = manage_df["date"].dt.strftime("%Y-%m-%d")

    st.dataframe(
        manage_df[["id", "date", "category", "description", "amount"]],
        use_container_width=True,
    )

    options = [
        f"{row['id']} | {row['date']} | ${row['amount']:.2f} | {row['category']} | {row['description']}"
        for _, row in manage_df.iterrows()
    ]
    selected = st.selectbox("Select one expense to delete", options)

    if st.button("Delete selected expense", type="secondary"):
        selected_id = selected.split(" | ")[0].strip()
        was_deleted = delete_expense(selected_id)
        if was_deleted:
            st.success("Expense deleted.")
            st.rerun()
        else:
            st.error("Could not delete this entry. Please refresh and try again.")
