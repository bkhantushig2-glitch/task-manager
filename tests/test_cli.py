import sys
import os
import json
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from click.testing import CliRunner
from src.cli import cli
import src.storage as storage


def setup_temp_storage(tmp_path):
    data_dir = os.path.join(tmp_path, "data")
    os.makedirs(data_dir, exist_ok=True)
    data_file = os.path.join(data_dir, "tasks.json")
    with open(data_file, "w") as f:
        json.dump({"tasks": []}, f)
    storage.DATA_DIR = data_dir
    storage.DATA_FILE = data_file


def seed_tasks(tmp_path):
    setup_temp_storage(tmp_path)
    runner = CliRunner()
    runner.invoke(cli, ["add", "Buy milk", "-d", "From the store", "--priority", "high"])
    runner.invoke(cli, ["add", "Read book", "-d", "Python basics", "--priority", "low"])
    runner.invoke(cli, ["add", "Clean house", "--due", "2026-04-01", "--priority", "medium"])


# --- ADD tests ---

def test_add_basic(tmp_path):
    setup_temp_storage(tmp_path)
    runner = CliRunner()
    result = runner.invoke(cli, ["add", "Buy milk"])
    assert result.exit_code == 0
    assert "Added task #1" in result.output
    assert "Buy milk" in result.output


def test_add_with_options(tmp_path):
    setup_temp_storage(tmp_path)
    runner = CliRunner()
    result = runner.invoke(cli, ["add", "Meeting", "-d", "With team", "--due", "2026-04-01", "-p", "high"])
    assert result.exit_code == 0
    assert "Added task #1" in result.output
    tasks = storage.load_tasks()
    assert len(tasks) == 1
    assert tasks[0].title == "Meeting"
    assert tasks[0].description == "With team"
    assert tasks[0].due_date == "2026-04-01"
    assert tasks[0].priority == "high"


def test_add_multiple(tmp_path):
    setup_temp_storage(tmp_path)
    runner = CliRunner()
    runner.invoke(cli, ["add", "Task 1"])
    result = runner.invoke(cli, ["add", "Task 2"])
    assert "Added task #2" in result.output
    tasks = storage.load_tasks()
    assert len(tasks) == 2


# --- LIST tests ---

def test_list_empty(tmp_path):
    setup_temp_storage(tmp_path)
    runner = CliRunner()
    result = runner.invoke(cli, ["list"])
    assert "No tasks found" in result.output


def test_list_all(tmp_path):
    seed_tasks(tmp_path)
    runner = CliRunner()
    result = runner.invoke(cli, ["list"])
    assert "Buy milk" in result.output
    assert "Read book" in result.output
    assert "Clean house" in result.output


def test_list_filter_priority(tmp_path):
    seed_tasks(tmp_path)
    runner = CliRunner()
    result = runner.invoke(cli, ["list", "-p", "high"])
    assert "Buy milk" in result.output
    assert "Read book" not in result.output


def test_list_filter_status(tmp_path):
    seed_tasks(tmp_path)
    runner = CliRunner()
    runner.invoke(cli, ["done", "1"])
    result = runner.invoke(cli, ["list", "-s", "done"])
    assert "Buy milk" in result.output
    assert "Read book" not in result.output


# --- DONE tests ---

def test_done_existing(tmp_path):
    seed_tasks(tmp_path)
    runner = CliRunner()
    result = runner.invoke(cli, ["done", "1"])
    assert result.exit_code == 0
    assert "marked as done" in result.output
    tasks = storage.load_tasks()
    assert tasks[0].status == "done"


def test_done_not_found(tmp_path):
    setup_temp_storage(tmp_path)
    runner = CliRunner()
    result = runner.invoke(cli, ["done", "99"])
    assert "not found" in result.output


# --- DELETE tests ---

def test_delete_existing(tmp_path):
    seed_tasks(tmp_path)
    runner = CliRunner()
    result = runner.invoke(cli, ["delete", "1"])
    assert result.exit_code == 0
    assert "deleted" in result.output
    tasks = storage.load_tasks()
    assert len(tasks) == 2
    assert all(t.id != 1 for t in tasks)


def test_delete_not_found(tmp_path):
    setup_temp_storage(tmp_path)
    runner = CliRunner()
    result = runner.invoke(cli, ["delete", "99"])
    assert "not found" in result.output


# --- EDIT tests ---

def test_edit_title(tmp_path):
    seed_tasks(tmp_path)
    runner = CliRunner()
    result = runner.invoke(cli, ["edit", "1", "--title", "Buy eggs"])
    assert result.exit_code == 0
    assert "updated" in result.output
    tasks = storage.load_tasks()
    assert tasks[0].title == "Buy eggs"


def test_edit_multiple_fields(tmp_path):
    seed_tasks(tmp_path)
    runner = CliRunner()
    result = runner.invoke(cli, ["edit", "1", "--title", "New title", "-d", "New desc", "-p", "low"])
    assert result.exit_code == 0
    tasks = storage.load_tasks()
    assert tasks[0].title == "New title"
    assert tasks[0].description == "New desc"
    assert tasks[0].priority == "low"


def test_edit_not_found(tmp_path):
    setup_temp_storage(tmp_path)
    runner = CliRunner()
    result = runner.invoke(cli, ["edit", "99", "--title", "Nope"])
    assert "not found" in result.output


# --- SEARCH tests ---

def test_search_by_title(tmp_path):
    seed_tasks(tmp_path)
    runner = CliRunner()
    result = runner.invoke(cli, ["search", "milk"])
    assert "Buy milk" in result.output
    assert "Read book" not in result.output


def test_search_by_description(tmp_path):
    seed_tasks(tmp_path)
    runner = CliRunner()
    result = runner.invoke(cli, ["search", "python"])
    assert "Read book" in result.output


def test_search_no_results(tmp_path):
    seed_tasks(tmp_path)
    runner = CliRunner()
    result = runner.invoke(cli, ["search", "zzzzz"])
    assert "No matching tasks" in result.output


def test_search_case_insensitive(tmp_path):
    seed_tasks(tmp_path)
    runner = CliRunner()
    result = runner.invoke(cli, ["search", "MILK"])
    assert "Buy milk" in result.output
