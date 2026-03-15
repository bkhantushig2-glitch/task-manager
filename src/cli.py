import click
from .task import Task
from .storage import load_tasks, save_tasks, get_next_id


@click.group()
def cli():
    """A simple CLI task manager."""
    pass


@cli.command()
@click.argument("title")
@click.option("--description", "-d", default="", help="Task description")
@click.option("--due", default=None, help="Due date (YYYY-MM-DD)")
@click.option("--priority", "-p", type=click.Choice(["high", "medium", "low"]), default="medium", help="Task priority")
def add(title, description, due, priority):
    """Add a new task."""
    task = Task(
        id=get_next_id(),
        title=title,
        description=description,
        due_date=due,
        priority=priority,
    )
    tasks = load_tasks()
    tasks.append(task)
    save_tasks(tasks)
    click.echo(f"Added task #{task.id}: {task.title}")


@cli.command(name="list")
@click.option("--status", "-s", type=click.Choice(["done", "todo"]), default=None, help="Filter by status")
@click.option("--priority", "-p", type=click.Choice(["high", "medium", "low"]), default=None, help="Filter by priority")
def list_tasks(status, priority):
    """List tasks."""
    tasks = load_tasks()
    if status:
        tasks = [t for t in tasks if t.status == status]
    if priority:
        tasks = [t for t in tasks if t.priority == priority]

    if not tasks:
        click.echo("No tasks found.")
        return

    for t in tasks:
        done_marker = "x" if t.status == "done" else " "
        due_str = f" (due: {t.due_date})" if t.due_date else ""
        click.echo(f"[{done_marker}] #{t.id} [{t.priority}] {t.title}{due_str}")


@cli.command()
@click.argument("task_id", type=int)
def done(task_id):
    """Mark a task as done."""
    tasks = load_tasks()
    for t in tasks:
        if t.id == task_id:
            t.mark_done()
            save_tasks(tasks)
            click.echo(f"Task #{task_id} marked as done.")
            return
    click.echo(f"Task #{task_id} not found.", err=True)


@cli.command()
@click.argument("task_id", type=int)
def delete(task_id):
    """Delete a task."""
    tasks = load_tasks()
    original_len = len(tasks)
    tasks = [t for t in tasks if t.id != task_id]
    if len(tasks) == original_len:
        click.echo(f"Task #{task_id} not found.", err=True)
        return
    save_tasks(tasks)
    click.echo(f"Task #{task_id} deleted.")


@cli.command()
@click.argument("task_id", type=int)
@click.option("--title", default=None, help="New title")
@click.option("--description", "-d", default=None, help="New description")
@click.option("--due", default=None, help="New due date (YYYY-MM-DD)")
@click.option("--priority", "-p", type=click.Choice(["high", "medium", "low"]), default=None, help="New priority")
def edit(task_id, title, description, due, priority):
    """Edit a task."""
    tasks = load_tasks()
    for t in tasks:
        if t.id == task_id:
            if title is not None:
                t.title = title
            if description is not None:
                t.description = description
            if due is not None:
                t.due_date = due
            if priority is not None:
                t.priority = priority
            from datetime import datetime
            t.updated_at = datetime.now().isoformat()
            save_tasks(tasks)
            click.echo(f"Task #{task_id} updated.")
            return
    click.echo(f"Task #{task_id} not found.", err=True)


@cli.command()
@click.argument("keyword")
def search(keyword):
    """Search tasks by keyword."""
    tasks = load_tasks()
    keyword_lower = keyword.lower()
    matches = [t for t in tasks if keyword_lower in t.title.lower() or keyword_lower in t.description.lower()]

    if not matches:
        click.echo("No matching tasks found.")
        return

    for t in matches:
        done_marker = "x" if t.status == "done" else " "
        due_str = f" (due: {t.due_date})" if t.due_date else ""
        click.echo(f"[{done_marker}] #{t.id} [{t.priority}] {t.title}{due_str}")


if __name__ == "__main__":
    cli()
