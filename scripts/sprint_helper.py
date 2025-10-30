#!/usr/bin/env python3
"""
Sprint Management Helper Script

This script helps create, update, and manage sprints in the project tracking system.

Usage:
    python scripts/sprint_helper.py start --number 2 --goal "Sprint goal"
    python scripts/sprint_helper.py status
    python scripts/sprint_helper.py complete
    python scripts/sprint_helper.py archive
"""

import argparse
import os
import shutil
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add src to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class SprintHelper:
    """Helper class for managing project sprints."""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.sprints_dir = self.project_root / "project_tracking" / "sprints"
        self.current_dir = self.sprints_dir / "current"
        self.completed_dir = self.sprints_dir / "completed"
        self.templates_dir = self.project_root / "project_tracking" / "templates"

        # Ensure directories exist
        self.current_dir.mkdir(parents=True, exist_ok=True)
        self.completed_dir.mkdir(parents=True, exist_ok=True)

    def get_current_sprint_file(self) -> Path | None:
        """Get the current sprint file."""
        sprint_files = list(self.current_dir.glob("sprint-*.md"))
        if not sprint_files:
            return None
        # Return the newest file (in case multiple exist)
        return max(sprint_files, key=lambda f: f.stat().st_mtime)

    def start_sprint(
        self,
        number: int,
        goal: str,
        duration_weeks: int = 2,
        theme: str = "",
    ) -> Path:
        """Start a new sprint."""
        # Check if sprint already exists
        current_sprint = self.get_current_sprint_file()
        if current_sprint:
            print(f"⚠️  Active sprint already exists: {current_sprint.name}")
            response = input("Archive current sprint and start new one? (y/N): ")
            if response.lower() != "y":
                print("❌ Cancelled")
                sys.exit(0)
            self.archive_sprint()

        # Calculate dates
        start_date = datetime.now()
        end_date = start_date + timedelta(weeks=duration_weeks)

        # Create sprint file
        sprint_name = f"sprint-{number:02d}"
        if theme:
            sprint_name += f"-{theme.lower().replace(' ', '-')[:30]}"
        sprint_file = self.current_dir / f"{sprint_name}.md"

        # Read template
        template_file = self.templates_dir / "sprint-template.md"
        if not template_file.exists():
            print(f"❌ Template not found at {template_file}")
            sys.exit(1)

        with open(template_file, encoding="utf-8") as f:
            template = f.read()

        # Replace placeholders
        content = template.replace("Sprint X", f"Sprint {number}")
        content = content.replace("[Sprint Name/Theme]", theme or "TBD")
        content = content.replace("**Sprint Number**: X", f"**Sprint Number**: {number}")
        content = content.replace("**Duration**: 2 weeks", f"**Duration**: {duration_weeks} weeks")
        content = content.replace(
            "**Start Date**: YYYY-MM-DD", f"**Start Date**: {start_date.strftime('%Y-%m-%d')}"
        )
        content = content.replace(
            "**End Date**: YYYY-MM-DD", f"**End Date**: {end_date.strftime('%Y-%m-%d')}"
        )
        content = content.replace(
            "**Sprint Goal**: [One sentence describing the main objective]",
            f"**Sprint Goal**: {goal}",
        )
        content = content.replace(
            "YYYY-MM-DD by Claude",
            f"{datetime.now().strftime('%Y-%m-%d')} by {os.getenv('USER', 'Developer')}",
        )

        # Write sprint file
        with open(sprint_file, "w", encoding="utf-8") as f:
            f.write(content)

        print(f"✅ Started Sprint {number}")
        print(f"   File: {sprint_file.name}")
        print(f"   Goal: {goal}")
        print(f"   Duration: {duration_weeks} weeks")
        print(f"   Start: {start_date.strftime('%Y-%m-%d')}")
        print(f"   End: {end_date.strftime('%Y-%m-%d')}")

        return sprint_file

    def show_status(self):
        """Show current sprint status."""
        sprint_file = self.get_current_sprint_file()
        if not sprint_file:
            print("❌ No active sprint found")
            return

        with open(sprint_file, encoding="utf-8") as f:
            content = f.read()

        # Extract key information
        lines = content.split("\n")
        sprint_info = {}

        for line in lines:
            if line.startswith("# Sprint"):
                sprint_info["title"] = line.replace("# ", "")
            elif line.startswith("**Sprint Number**:"):
                sprint_info["number"] = line.split(":")[1].strip()
            elif line.startswith("**Start Date**:"):
                sprint_info["start"] = line.split(":")[1].strip()
            elif line.startswith("**End Date**:"):
                sprint_info["end"] = line.split(":")[1].strip()
            elif line.startswith("**Sprint Goal**:"):
                sprint_info["goal"] = line.split(":", 1)[1].strip()
            elif "**Sprint Status**:" in line:
                sprint_info["status"] = line.split(":")[1].strip()

        # Display
        print(f"\n📊 {sprint_info.get('title', 'Current Sprint')}")
        print(f"   Sprint Number: {sprint_info.get('number', 'Unknown')}")
        print(f"   Goal: {sprint_info.get('goal', 'Not set')}")
        print(f"   Start: {sprint_info.get('start', 'Unknown')}")
        print(f"   End: {sprint_info.get('end', 'Unknown')}")
        print(f"   Status: {sprint_info.get('status', 'Unknown')}")

        # Calculate progress
        try:
            start = datetime.strptime(sprint_info.get("start", ""), "%Y-%m-%d")
            end = datetime.strptime(sprint_info.get("end", ""), "%Y-%m-%d")
            now = datetime.now()

            if now < start:
                print("   Progress: Not started")
            elif now > end:
                print(f"   Progress: Completed (ended {(now - end).days} days ago)")
            else:
                total_days = (end - start).days
                elapsed_days = (now - start).days
                progress = (elapsed_days / total_days) * 100
                remaining_days = (end - now).days
                print(f"   Progress: {progress:.0f}% ({elapsed_days}/{total_days} days)")
                print(f"   Remaining: {remaining_days} days")
        except ValueError:
            print("   Progress: Unknown")

        print(f"\n   File: {sprint_file.name}\n")

    def archive_sprint(self):
        """Archive the current sprint to completed folder."""
        sprint_file = self.get_current_sprint_file()
        if not sprint_file:
            print("❌ No active sprint to archive")
            return

        # Move to completed
        dest = self.completed_dir / sprint_file.name
        shutil.move(str(sprint_file), str(dest))

        # Also move associated task files
        task_files = list(self.current_dir.glob("task-*.md"))
        if task_files:
            print(f"📁 Archiving {len(task_files)} task files...")
            for task_file in task_files:
                task_dest = self.completed_dir / task_file.name
                shutil.move(str(task_file), str(task_dest))

        print(f"✅ Archived sprint to: {dest}")
        print(f"   Tasks archived: {len(task_files)}")

    def complete_sprint(self):
        """Mark sprint as completed and update status."""
        sprint_file = self.get_current_sprint_file()
        if not sprint_file:
            print("❌ No active sprint found")
            return

        with open(sprint_file, encoding="utf-8") as f:
            content = f.read()

        # Update status
        content = content.replace(
            "**Sprint Status**: 🟢 On Track", "**Sprint Status**: ✅ Completed"
        )
        content = content.replace(
            "**Sprint Status**: 🟡 At Risk", "**Sprint Status**: ✅ Completed"
        )
        content = content.replace(
            "**Sprint Status**: 🔴 Blocked", "**Sprint Status**: ✅ Completed"
        )

        # Add completion date
        completion_note = f"\n\n**Completed**: {datetime.now().strftime('%Y-%m-%d')}\n"
        if "**Last Updated**:" in content:
            content = content.replace("**Last Updated**:", completion_note + "**Last Updated**:")

        with open(sprint_file, "w", encoding="utf-8") as f:
            f.write(content)

        print("✅ Marked sprint as completed")
        print("   Next: Run 'python scripts/sprint_helper.py archive' to archive")
        print("   Then: Start new sprint with 'python scripts/sprint_helper.py start'")


def main():
    parser = argparse.ArgumentParser(description="Sprint Management Helper")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Start sprint
    start_parser = subparsers.add_parser("start", help="Start a new sprint")
    start_parser.add_argument("--number", type=int, required=True, help="Sprint number")
    start_parser.add_argument("--goal", required=True, help="Sprint goal")
    start_parser.add_argument("--theme", default="", help="Sprint theme/name")
    start_parser.add_argument(
        "--duration", type=int, default=2, help="Duration in weeks (default: 2)"
    )

    # Show status
    status_parser = subparsers.add_parser("status", help="Show current sprint status")

    # Complete sprint
    complete_parser = subparsers.add_parser("complete", help="Mark sprint as completed")

    # Archive sprint
    archive_parser = subparsers.add_parser("archive", help="Archive completed sprint")

    args = parser.parse_args()
    helper = SprintHelper()

    if args.command == "start":
        helper.start_sprint(
            number=args.number,
            goal=args.goal,
            theme=args.theme,
            duration_weeks=args.duration,
        )
    elif args.command == "status":
        helper.show_status()
    elif args.command == "complete":
        helper.complete_sprint()
    elif args.command == "archive":
        helper.archive_sprint()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
