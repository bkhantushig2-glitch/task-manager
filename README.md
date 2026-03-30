# Task Manager CLI

A command-line task manager built with Python and Click. Add, list, complete, edit, search, and delete tasks right from your terminal.

## Setup

**Requirements:** Python 3.9+

```bash
# Install dependencies
pip install click

# Clone the repo
git clone https://github.com/bkhantushig2-glitch/task-manager.git
cd task-manager
```

## Usage

```bash
# Add a task
python3 -m src add "Buy groceries"
python3 -m src add "Finish homework" -p high --due 2026-04-01
python3 -m src add "Read chapter 5" -d "Pages 100-150" -p low

# List all tasks
python3 -m src list

# Filter by status or priority
python3 -m src list -s todo
python3 -m src list -p high

# Mark a task as done
python3 -m src done 1

# Edit a task
python3 -m src edit 1 --title "Buy eggs" -p low

# Search tasks
python3 -m src search "homework"

# Delete a task
python3 -m src delete 1
```

## Features

- **Add tasks** with title, description, priority, and due date
- **List tasks** with filters for status and priority
- **Color-coded priorities** (red = high, yellow = medium, green = low)
- **Due date sorting** with overdue warnings
- **Mark tasks done** with strikethrough display
- **Edit tasks** to update any field
- **Search** by keyword across titles and descriptions
- **JSON persistence** so your tasks survive between sessions

## Dependencies

- [Click](https://click.palletsprojects.com/) - CLI framework
- [pytest](https://docs.pytest.org/) - testing (dev only)

## Running Tests

```bash
python3 -m pytest tests/ -v
```

## Project Structure

```
task-manager/
  src/
    cli.py       # CLI commands (add, list, done, delete, edit, search)
    task.py      # Task data model
    storage.py   # JSON file read/write
  tests/
    test_cli.py      # CLI command tests
    test_task.py     # Task model tests
    test_storage.py  # Storage tests
  data/
    tasks.json   # Where your tasks are saved
```
