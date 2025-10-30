#!/usr/bin/env python3
"""
Task Management Helper Script

This script helps create, update, and manage tasks in the project tracking system.

Usage:
    python scripts/task_helper.py create --name "task name" --priority P1 --type feature
    python scripts/task_helper.py list [--status todo|in_progress|blocked|completed]
    python scripts/task_helper.py update --id 001 --status in_progress
    python scripts/task_helper.py show --id 001
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path

# Add src to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class TaskHelper:
    """Helper class for managing project tasks."""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.current_sprint_dir = self.project_root / "project_tracking" / "sprints" / "current"
        self.templates_dir = self.project_root / "project_tracking" / "templates"
        self.current_sprint_dir.mkdir(parents=True, exist_ok=True)

    def get_next_task_number(self) -> int:
        """Get the next available task number."""
        task_files = list(self.current_sprint_dir.glob("task-*.md"))
        if not task_files:
            return 1

        numbers = []
        for f in task_files:
            try:
                num = int(f.stem.split("-")[1])
                numbers.append(num)
            except (IndexError, ValueError):
                continue

        return max(numbers) + 1 if numbers else 1

    def create_task(
        self,
        name: str,
        priority: str = "P1",
        task_type: str = "feature",
        effort: str = "M",
        description: str = "",
    ) -> Path:
        """Create a new task file from template."""
        task_num = self.get_next_task_number()
        task_id = f"{task_num:03d}"

        # Create filename
        safe_name = name.lower().replace(" ", "-")[:50]
        filename = f"task-{task_id}-{safe_name}.md"
        task_file = self.current_sprint_dir / filename

        # Read template
        template_file = self.templates_dir / "task-template.md"
        if not template_file.exists():
            print(f"Error: Template not found at {template_file}")
            sys.exit(1)

        with open(template_file, encoding="utf-8") as f:
            template = f.read()

        # Replace placeholders
        content = template.replace("[Task Title]", name)
        content = content.replace("`todo` | `in_progress` | `blocked` | `completed`", "`todo`")
        content = content.replace(
            "`P0 (Critical)` | `P1 (High)` | `P2 (Medium)` | `P3 (Low)`", f"`{priority}`"
        )
        content = content.replace(
            "`XS (1-2h)` | `S (2-4h)` | `M (4-8h)` | `L (1-2d)` | `XL (2-5d)`", f"`{effort}`"
        )
        content = content.replace(
            "`feature` | `bugfix` | `refactor` | `test` | `docs` | `research`", f"`{task_type}`"
        )
        content = content.replace("YYYY-MM-DD", datetime.now().strftime("%Y-%m-%d"))
        content = content.replace(
            "[Clear description of what needs to be done and why]",
            description or "[Add task description here]",
        )

        # Write task file
        with open(task_file, "w", encoding="utf-8") as f:
            f.write(content)

        print(f"✅ Created task: {filename}")
        print(f"   Location: {task_file}")
        print(f"   Priority: {priority}")
        print(f"   Type: {task_type}")
        print(f"   Effort: {effort}")

        return task_file

    def list_tasks(self, status_filter: str | None = None) -> list[dict]:
        """List all tasks in current sprint."""
        task_files = sorted(self.current_sprint_dir.glob("task-*.md"))

        tasks = []
        for task_file in task_files:
            task_info = self._parse_task_file(task_file)
            if status_filter and task_info.get("status") != status_filter:
                continue
            tasks.append(task_info)

        return tasks

    def _parse_task_file(self, task_file: Path) -> dict:
        """Parse task file to extract metadata."""
        with open(task_file, encoding="utf-8") as f:
            content = f.read()

        lines = content.split("\n")
        task_info = {
            "file": task_file.name,
            "path": str(task_file),
            "title": "Unknown",
            "status": "unknown",
            "priority": "unknown",
            "effort": "unknown",
            "type": "unknown",
        }

        for line in lines:
            if line.startswith("# Task:"):
                task_info["title"] = line.replace("# Task:", "").strip()
            elif line.startswith("**Status**:"):
                # Extract status from: **Status**: `todo`
                status = line.split("`")[1] if "`" in line else "unknown"
                task_info["status"] = status
            elif line.startswith("**Priority**:"):
                priority = line.split("`")[1] if "`" in line else "unknown"
                task_info["priority"] = priority
            elif line.startswith("**Estimated Effort**:"):
                effort = line.split("`")[1] if "`" in line else "unknown"
                task_info["effort"] = effort
            elif line.startswith("**Task Type**:"):
                task_type = line.split("`")[1] if "`" in line else "unknown"
                task_info["type"] = task_type

        return task_info

    def update_task_status(self, task_id: str, new_status: str) -> bool:
        """Update the status of a task."""
        task_file = self._find_task_file(task_id)
        if not task_file:
            print(f"❌ Task {task_id} not found")
            return False

        with open(task_file, encoding="utf-8") as f:
            content = f.read()

        # Update status line
        lines = content.split("\n")
        for i, line in enumerate(lines):
            if line.startswith("**Status**:"):
                # Replace the status
                lines[i] = f"**Status**: `{new_status}`"
                break

        # Write back
        with open(task_file, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

        print(f"✅ Updated task {task_id} status to: {new_status}")
        return True

    def _find_task_file(self, task_id: str) -> Path | None:
        """Find task file by ID."""
        pattern = f"task-{task_id}-*.md"
        matches = list(self.current_sprint_dir.glob(pattern))
        return matches[0] if matches else None

    def show_task(self, task_id: str):
        """Show task details."""
        task_file = self._find_task_file(task_id)
        if not task_file:
            print(f"❌ Task {task_id} not found")
            return

        task_info = self._parse_task_file(task_file)
        print(f"\n📋 Task {task_id}: {task_info['title']}")
        print(f"   Status: {task_info['status']}")
        print(f"   Priority: {task_info['priority']}")
        print(f"   Effort: {task_info['effort']}")
        print(f"   Type: {task_info['type']}")
        print(f"   File: {task_info['file']}\n")


def main():
    parser = argparse.ArgumentParser(description="Task Management Helper")
    subparsers = parser.add_parsers(dest="command", help="Command to execute")

    # Create task
    create_parser = subparsers.add_parser("create", help="Create a new task")
    create_parser.add_argument("--name", required=True, help="Task name")
    create_parser.add_argument(
        "--priority", choices=["P0", "P1", "P2", "P3"], default="P1", help="Task priority"
    )
    create_parser.add_argument(
        "--type",
        choices=["feature", "bugfix", "refactor", "test", "docs", "research"],
        default="feature",
        help="Task type",
    )
    create_parser.add_argument(
        "--effort", choices=["XS", "S", "M", "L", "XL"], default="M", help="Effort estimate"
    )
    create_parser.add_argument("--description", default="", help="Task description")

    # List tasks
    list_parser = subparsers.add_parser("list", help="List tasks")
    list_parser.add_argument(
        "--status",
        choices=["todo", "in_progress", "blocked", "completed"],
        help="Filter by status",
    )

    # Update task
    update_parser = subparsers.add_parser("update", help="Update task status")
    update_parser.add_argument("--id", required=True, help="Task ID (e.g., 001)")
    update_parser.add_argument(
        "--status",
        required=True,
        choices=["todo", "in_progress", "blocked", "completed"],
        help="New status",
    )

    # Show task
    show_parser = subparsers.add_parser("show", help="Show task details")
    show_parser.add_argument("--id", required=True, help="Task ID (e.g., 001)")

    args = parser.parse_args()
    helper = TaskHelper()

    if args.command == "create":
        helper.create_task(
            name=args.name,
            priority=args.priority,
            task_type=args.type,
            effort=args.effort,
            description=args.description,
        )
    elif args.command == "list":
        tasks = helper.list_tasks(status_filter=args.status)
        if not tasks:
            print("No tasks found")
        else:
            print(f"\n📋 Tasks ({len(tasks)}):\n")
            for task in tasks:
                status_emoji = {
                    "todo": "⚪",
                    "in_progress": "🔵",
                    "blocked": "🔴",
                    "completed": "✅",
                }.get(task["status"], "❓")
                print(
                    f"{status_emoji} [{task['priority']}] {task['title']} ({task['effort']}) - {task['status']}"
                )
            print()
    elif args.command == "update":
        helper.update_task_status(args.id, args.status)
    elif args.command == "show":
        helper.show_task(args.id)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
