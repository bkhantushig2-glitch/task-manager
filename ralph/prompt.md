# Ralph Instructions - Task Manager

## Big Picture
Build a Python CLI task manager in small verified steps. Each loop iteration starts with a fresh context window, so your memory is in files and git history.

## Loop Algorithm
Each iteration:
1. Read `ralph/goals.json`.
2. Pick the first goal where `status != "passed"` and all dependencies are passed.
3. If verification specifies tests and they do not exist, write tests first.
4. Run that goal's verification command.
5. If verification fails, implement/fix and rerun.
6. If verification passes, mark goal as `"passed"`, commit, and update `ralph/progress.txt`.

## Rules
- One goal per iteration.
- Do not mark a goal passed until its verification command passes.
- Keep code simple and readable for beginner students.
- If blocked by missing prerequisite, add a new goal (e.g., `1a`) with `added_by: "ralph"` and a short reason.

## Regression Protocol
If you notice broken behavior in a previously passed goal:
1. Mark that goal as `"regression"`.
2. Add a repair goal with suffix `r` (for example `1r`).
3. Continue current goal unless the regression blocks progress.

## Important Files
- `src/task.py` - Task dataclass
- `src/storage.py` - JSON persistence
- `src/cli.py` - CLI entry point (Click)
- `data/tasks.json` - persistence file
- `ralph/goals.json` - source of truth for goal status
- `ralph/progress.txt` - short loop notes

## Commands
```bash
pytest tests/ -v
python -m src.cli add "test task"
python -m src.cli list
git log --oneline -8
```

## Commit Message Format
`goal [id]: [short summary]`
