import json
import os
from typing import List
from .task import Task

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
DATA_FILE = os.path.join(DATA_DIR, "tasks.json")


def ensure_data_file():
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w") as f:
            json.dump({"tasks": []}, f)


def load_tasks() -> List[Task]:
    ensure_data_file()
    with open(DATA_FILE, "r") as f:
        data = json.load(f)
    return [Task.from_dict(t) for t in data.get("tasks", [])]


def save_tasks(tasks: List[Task]):
    ensure_data_file()
    with open(DATA_FILE, "w") as f:
        json.dump({"tasks": [t.to_dict() for t in tasks]}, f, indent=2)


def get_next_id() -> int:
    tasks = load_tasks()
    if not tasks:
        return 1
    return max(t.id for t in tasks) + 1
