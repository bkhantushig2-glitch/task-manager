import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.task import Task


def test_task_creation():
    task = Task(id=1, title="Buy milk")
    assert task.id == 1
    assert task.title == "Buy milk"
    assert task.status == "todo"
    assert task.priority == "medium"
    assert task.description == ""


def test_task_with_all_fields():
    task = Task(
        id=2,
        title="Study",
        description="Chapter 5",
        due_date="2026-03-20",
        priority="high",
    )
    assert task.priority == "high"
    assert task.due_date == "2026-03-20"
    assert task.description == "Chapter 5"


def test_task_mark_done():
    task = Task(id=1, title="Test")
    assert task.status == "todo"
    task.mark_done()
    assert task.status == "done"


def test_task_mark_todo():
    task = Task(id=1, title="Test", status="done")
    task.mark_todo()
    assert task.status == "todo"


def test_task_to_dict():
    task = Task(id=1, title="Test")
    d = task.to_dict()
    assert d["id"] == 1
    assert d["title"] == "Test"
    assert "created_at" in d
    assert "updated_at" in d


def test_task_from_dict():
    data = {
        "id": 3,
        "title": "From dict",
        "description": "",
        "due_date": None,
        "priority": "low",
        "status": "todo",
        "created_at": "2026-01-01T00:00:00",
        "updated_at": "2026-01-01T00:00:00",
    }
    task = Task.from_dict(data)
    assert task.id == 3
    assert task.title == "From dict"
    assert task.priority == "low"
