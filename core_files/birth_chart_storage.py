import json
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "birth_charts.json"




def save_birth_chart(data: dict):
    if os.path.exists(DB_PATH):
        with open(DB_PATH, "r", encoding="utf-8") as f:
            charts = json.load(f)
    else:
        charts = []

    charts.append(data)

    with open(DB_PATH, "w", encoding="utf-8") as f:
        json.dump(charts, f, ensure_ascii=False, indent=4)



def list_birth_charts():
    if not os.path.exists(DB_PATH):
        print("База натальных карт пуста.")
        return []

    with open(DB_PATH, "r", encoding="utf-8") as f:
        charts = json.load(f)

    if not charts:
        print("База натальных карт пуста.")
        return []

    print("\n=== Сохранённые натальные карты ===")
    for i, chart in enumerate(charts, 1):
        print(f"{i}. {chart['name']} — {chart['date']} {chart['time']} ({chart['city']})")
    return charts

def find_birth_chart_by_name(name: str):
    if not os.path.exists(DB_PATH):
        print("База пуста.")
        return

    with open(DB_PATH, "r", encoding="utf-8") as f:
        charts = json.load(f)

    found = [c for c in charts if c["name"].lower() == name.lower()]
    if not found:
        print(f"Карта с именем '{name}' не найдена.")
    else:
        print(f"\n=== Результаты поиска для '{name}' ===")
        for chart in found:
            for key, value in chart.items():
                print(f"{key.capitalize()}: {value}")
            print("---")
