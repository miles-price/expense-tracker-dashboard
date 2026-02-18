import json

import storage


def test_save_and_delete_expense(tmp_path, monkeypatch):
    data_file = tmp_path / "test_data.json"
    monkeypatch.setattr(storage, "FILE_NAME", data_file)

    saved = storage.save_expense(
        {"amount": 20.5, "category": "Food", "description": "Lunch", "date": "2026-02-01"}
    )

    all_expenses = storage.load_expenses()
    assert len(all_expenses) == 1
    assert all_expenses[0]["id"] == saved["id"]

    removed = storage.delete_expense(saved["id"])
    assert removed is True
    assert storage.load_expenses() == []


def test_load_expenses_handles_invalid_json(tmp_path, monkeypatch):
    data_file = tmp_path / "bad.json"
    data_file.write_text("not-json", encoding="utf-8")
    monkeypatch.setattr(storage, "FILE_NAME", data_file)

    assert storage.load_expenses() == []


def test_load_expenses_normalizes_old_records(tmp_path, monkeypatch):
    data_file = tmp_path / "legacy.json"
    legacy = [{"amount": 12, "category": "Food", "description": "", "date": "2026-02-17 18:24:10"}]
    data_file.write_text(json.dumps(legacy), encoding="utf-8")
    monkeypatch.setattr(storage, "FILE_NAME", data_file)

    normalized = storage.load_expenses()

    assert len(normalized) == 1
    assert "id" in normalized[0]
    assert normalized[0]["date"] == "2026-02-17"
