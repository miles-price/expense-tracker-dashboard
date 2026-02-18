# Personal Expense Tracker (Streamlit)

A portfolio-grade personal finance app built with Python and Streamlit.

This project demonstrates practical SWE skills: data modeling, CRUD flows, input validation, analytics, testing, and clear product UX.

## Features

- Add expenses with `amount`, `category`, `description`, and `date`
- Auto-normalized records with stable `id` fields for safe deletion
- Interactive dashboard metrics:
  - Total spent
  - Current month spend
  - Average transaction value
  - Top spending category
- Filter by category, date range, and amount range
- Visual analytics:
  - Spending by category (bar chart)
  - Daily spend trend (line chart)
- Monthly budget tracking with progress bar and over-budget alert
- CSV export for filtered transactions
- Data management page for deleting individual entries
- Backward compatibility with legacy date formats in stored JSON

## Tech Stack

- Python
- Streamlit
- Pandas
- Matplotlib
- JSON file persistence
- Pytest

## Local Setup

```bash
git clone https://github.com/miles-price/expense-tracker-dashboard.git
cd expense-tracker-dashboard
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Run Tests

```bash
pytest -q
```

## Deploy To Streamlit Community Cloud

1. Push this repository to GitHub.
2. Go to https://share.streamlit.io and sign in with GitHub.
3. Click `New app` and select:
   - Repository: `miles-price/expense-tracker-dashboard`
   - Branch: `main`
   - Main file path: `app.py`
4. Click `Deploy`.

After deploy, add the live app URL to this README and your resume.

## Project Structure

```text
app.py          # Streamlit app (UI + product logic)
expense.py      # Expense domain model
storage.py      # JSON persistence + normalization
analysis.py     # Analytics helpers
tests/          # Unit tests for analytics and storage
```

## Resume Bullet Ideas

- Built and shipped a full-stack-style data app in Python/Streamlit with end-to-end CRUD, analytics, and export workflows.
- Designed a robust persistence layer that normalizes legacy data and prevents malformed records from breaking the app.
- Added automated tests for analytics and storage logic to improve reliability and maintainability.
