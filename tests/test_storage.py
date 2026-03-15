import sys
import os
import json
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import src.storage as storage
from src.task import Task


def setup_temp_storage(tmp_path):
    """Point storage to a temp directory for testing."""
    storage.DATA_DIR = str(tmp_path)
    storage.DATA_FILE = os.path.join(str(tmp_path), "tasks.json")


def test_ensure_data_file(tmp_path):
    setup_temp_storage(tmp_path)
    storage.ensure_data_file()
    assert os.path.exists(storage.DATA_FILE)


def test_load_empty(tmp_path):
    setup_temp_storage(tmp_path)
    tasks = storage.load_tasks()
    assert tasks == []


def test_save_and_load(tmp_path):
    setup_temp_storage(tmp_path)
    tasks = [
        Task(id=1, title="First"),
        Task(id=2, title="Second", priority="high"),
    ]
    storage.save_tasks(tasks)
    loaded = storage.load_tasks()
    assert len(loaded) == 2
    assert loaded[0].title == "First"
    assert loaded[1].priority == "high"


def test_get_next_id_empty(tmp_path):
    setup_temp_storage(tmp_path)
    assert storage.get_next_id() == 1


def test_get_next_id_with_tasks(tmp_path):
    setup_temp_storage(tmp_path)
    storage.save_tasks([Task(id=5, title="Test")])
    assert storage.get_next_id() == 6
