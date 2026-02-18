import json
import os

FILE_NAME = "data.json"

def load_expenses():
    if not os.path.exists(FILE_NAME):
        return []

    with open(FILE_NAME, "r") as file:
        try:
            return json.load(file)
        except json.JSONDecodeError:
            return []

def save_expense(expense):
    expenses = load_expenses()
    expenses.append(expense)

    with open(FILE_NAME, "w") as file:
        json.dump(expenses, file, indent=4)

def save_all_expenses(expenses):
    with open(FILE_NAME, "w") as file:
        json.dump(expenses, file, indent=4)