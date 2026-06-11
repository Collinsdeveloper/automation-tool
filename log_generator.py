import argparse
import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import List

try:
    from rich.console import Console
    from rich.table import Table
except ImportError:
    Console = None
    Table = None

console = Console() if Console is not None else None


@dataclass
class Task:
    description: str
    completed: bool = False
    id: int = field(default=0)

    def mark_complete(self):
        self.completed = True


class TaskManager:
    def __init__(self):
        self.task_file = Path("tasks.json")
        self.tasks: List[Task] = []
        self._next_id = 1
        self._load_tasks()

    def add_task(self, description: str) -> Task:
        task = Task(description=description, id=self._next_id)
        self.tasks.append(task)
        self._next_id += 1
        self._save_tasks()
        return task

    def complete_task(self, task_id: int) -> Task:
        for task in self.tasks:
            if task.id == task_id:
                task.mark_complete()
                self._save_tasks()
                return task
        raise ValueError(f"Task with id {task_id} not found")

    def list_tasks(self) -> List[Task]:
        return list(self.tasks)

    def _load_tasks(self) -> None:
        if not self.task_file.exists():
            return
        try:
            data = json.loads(self.task_file.read_text(encoding="utf-8"))
            for item in data:
                task = Task(
                    description=item["description"],
                    completed=item.get("completed", False),
                    id=item["id"],
                )
                self.tasks.append(task)
                self._next_id = max(self._next_id, task.id + 1)
        except (json.JSONDecodeError, KeyError, TypeError):
            console.print("[red]Warning:[/red] Failed to load existing tasks. Starting fresh.")

    def _save_tasks(self) -> None:
        data = [
            {"id": task.id, "description": task.description, "completed": task.completed}
            for task in self.tasks
        ]
        self.task_file.write_text(json.dumps(data, indent=2), encoding="utf-8")


def generate_log(log_entries):
    if not isinstance(log_entries, list):
        raise ValueError("Input must be a list")

    filename = f"log_{datetime.now().strftime('%Y%m%d')}.txt"

    with open(filename, "w", encoding="utf-8") as file:
        for entry in log_entries:
            file.write(f"{entry}\n")

    if console is not None:
        console.print(f"[green]Log file created:[/green] {filename}")
    else:
        print(f"Log file created: {filename}")
    return filename


def main():
    parser = argparse.ArgumentParser(
        description="Automation tool for task management and log generation"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    add_parser = subparsers.add_parser("add-task", help="Add a new task")
    add_parser.add_argument("description", help="Task description")

    complete_parser = subparsers.add_parser("complete-task", help="Mark a task as complete")
    complete_parser.add_argument("task_id", type=int, help="ID of the task to complete")

    list_parser = subparsers.add_parser("list-tasks", help="List all tasks")

    log_parser = subparsers.add_parser("generate-log", help="Create a timestamped log file")
    log_parser.add_argument(
        "entries",
        nargs="*",
        help="Log entries to write to the file",
        default=[],
    )

    args = parser.parse_args()
    manager = TaskManager()

    if args.command == "add-task":
        task = manager.add_task(args.description)
        if console is not None:
            console.print(f"[blue]Task added:[/blue] {task.id} - {task.description}")
        else:
            print(f"Task added: {task.id} - {task.description}")

    elif args.command == "complete-task":
        try:
            task = manager.complete_task(args.task_id)
            if console is not None:
                console.print(f"[blue]Task completed:[/blue] {task.id} - {task.description}")
            else:
                print(f"Task completed: {task.id} - {task.description}")
        except ValueError as exc:
            if console is not None:
                console.print(f"[red]Error:[/red] {exc}")
            else:
                print(f"Error: {exc}")
            raise

    elif args.command == "list-tasks":
        tasks = manager.list_tasks()
        if console is not None and Table is not None:
            table = Table(title="Tasks")
            table.add_column("ID", justify="right")
            table.add_column("Description")
            table.add_column("Completed")
            for task in tasks:
                table.add_row(str(task.id), task.description, "Yes" if task.completed else "No")
            console.print(table)
        else:
            for task in tasks:
                print(f"{task.id}: {task.description} - {'Completed' if task.completed else 'Pending'}")

    elif args.command == "generate-log":
        generate_log(args.entries)


if __name__ == "__main__":
    main()
