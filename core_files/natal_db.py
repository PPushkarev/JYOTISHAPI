# natal_db.py

import json
import os

DB_FILE = "natal_database.json"

def load_db():
    if not os.path.exists(DB_FILE):
        return {}
    with open(DB_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_db(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def add_natal_chart(name, birth_info):
    data = load_db()
    if name in data:
        print(f"Запись для '{name}' уже существует.")
        return False
    data[name] = birth_info
    save_db(data)
    print(f"Натальная карта для '{name}' сохранена.")
    return True

def get_natal_chart(name):
    data = load_db()
    return data.get(name)

def list_all_names():
    data = load_db()
    return list(data.keys())
