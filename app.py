import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd

from expense import Expense
from storage import load_expenses, save_expense, save_all_expenses
from analysis import load_dataframe, total_spent, category_summary, spending_over_time

st.set_page_config(page_title="Expense Tracker Dashboard", layout="wide")
st.title("💰 Personal Expense Tracker Dashboard")

# Sidebar Navigation
menu = st.sidebar.selectbox("Menu", ["Add Expense", "Dashboard", "Data"])

# ---------------------------
# PAGE 1: ADD EXPENSE
# ---------------------------
if menu == "Add Expense":
    st.subheader("Add a New Expense")

    amount = st.number_input("Amount ($)", min_value=0.0, format="%.2f")
    # Build category choices from existing data
    existing = load_expenses()
    existing_categories = sorted({e.get("category", "").strip() for e in existing if e.get("category")})
    category_choice = st.selectbox("Category", existing_categories + ["➕ Add new category" ] if existing_categories else ["➕ Add new category"])

    if category_choice == "➕ Add new category":
        category = st.text_input("New category name").strip()
    else:
        category = category_choice

    description = st.text_input("Description (optional)").strip()
    expense_date = st.date_input("Date", value=pd.Timestamp.today().date())

    if st.button("Save Expense"):
        if amount <= 0:
            st.error("Amount must be greater than 0.")
        elif not category:
            st.error("Category is required.")
        else:
            expense = Expense(amount, category, description, expense_date)
            save_expense(expense.to_dict())
            st.success("✅ Expense saved!")

    st.caption("Tip: Use consistent category names (e.g., Food vs food) for cleaner charts.")

# ---------------------------
# PAGE 2: DASHBOARD (CHARTS)
# ---------------------------
elif menu == "Dashboard":
    st.subheader("Spending Overview")

    expenses = load_expenses()
    df = load_dataframe(expenses)

    if df.empty:
        st.info("No expenses recorded yet. Add one from the 'Add Expense' page.")
    else:
        # Metrics
        st.metric("Total Spent", f"${total_spent(df):.2f}")

        # Filters
        st.markdown("### Filters")
        all_categories = sorted(df["category"].dropna().unique().tolist())
        selected_categories = st.multiselect("Category", all_categories, default=all_categories)

        # Date range filter
        df = df.copy()
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        min_date = df["date"].min().date() if df["date"].notna().any() else pd.Timestamp.today().date()
        max_date = df["date"].max().date() if df["date"].notna().any() else pd.Timestamp.today().date()

        start_date, end_date = st.date_input(
            "Date range",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date,
        )

        filtered_df = df[df["category"].isin(selected_categories)].copy()
        filtered_df = filtered_df[(filtered_df["date"].dt.date >= start_date) & (filtered_df["date"].dt.date <= end_date)].copy()

        if filtered_df.empty:
            st.info("No expenses match the selected filters. Adjust your category selection to see charts and data.")
            st.stop()

        col1, col2 = st.columns(2)

        # Chart 1: Bar chart by category
        with col1:
            st.markdown("### Spending by Category")
            cat_data = category_summary(filtered_df)

            fig1, ax1 = plt.subplots()
            cat_data.plot(kind="bar", ax=ax1)
            ax1.set_xlabel("Category")
            ax1.set_ylabel("Amount ($)")
            ax1.tick_params(axis="x", rotation=30)
            st.pyplot(fig1)

        # Chart 2: Spending over time
        with col2:
            st.markdown("### Spending Over Time")
            time_data = spending_over_time(filtered_df)

            fig2, ax2 = plt.subplots()
            time_data.plot(kind="line", marker="o", ax=ax2)
            ax2.set_xlabel("Date")
            ax2.set_ylabel("Amount ($)")
            ax2.tick_params(axis="x", rotation=30)
            st.pyplot(fig2)

        # Table view
        st.markdown("### Expenses Table")
        filtered_df["amount"] = filtered_df["amount"].astype(float)
        st.dataframe(filtered_df.sort_values("date", ascending=False), use_container_width=True)

        st.markdown("### Delete an Expense")

        filtered_df_display = filtered_df.sort_values("date", ascending=False).reset_index(drop=True)
        options = [
            f"{i}: ${row['amount']:.2f} | {row['category']} | {row['description']} | {row['date']}"
            for i, row in filtered_df_display.iterrows()
        ]

        to_delete = st.selectbox("Select an expense to delete", options)

        if st.button("Delete Selected Expense"):
            delete_index = int(to_delete.split(":")[0])

            all_expenses = load_expenses()
            all_df = load_dataframe(all_expenses).sort_values("date", ascending=False).reset_index(drop=True)

            row = filtered_df_display.iloc[delete_index]
            match = (
                (all_df["amount"].astype(float) == float(row["amount"])) &
                (all_df["category"] == row["category"]) &
                (all_df["description"] == row["description"]) &
                (all_df["date"] == row["date"])
            )

            match_indices = all_df[match].index.tolist()
            if match_indices:
                all_df = all_df.drop(match_indices[0]).reset_index(drop=True)
                save_all_expenses(all_df.to_dict(orient="records"))
                st.success("Deleted! Refreshing dashboard...")
                st.rerun()
            else:
                st.error("Could not find that expense in the saved data.")

# ---------------------------
# PAGE 3: RAW DATA VIEW
# ---------------------------
elif menu == "Data":
    st.subheader("Raw Expense Data (data.json)")

    expenses = load_expenses()
    df = load_dataframe(expenses)

    if df.empty:
        st.info("No data yet.")
    else:
        st.write(df)
        st.caption("This table is generated from your saved JSON file.")
