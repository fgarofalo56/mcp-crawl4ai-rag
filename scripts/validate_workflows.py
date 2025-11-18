#!/usr/bin/env python3
"""
Validate GitHub Actions workflows and related YAML configuration files.

This script checks:
- YAML syntax validity
- Workflow structure (on, jobs, steps)
- Dependabot configuration
- Pre-commit configuration
"""

import sys
from pathlib import Path

import yaml


class Colors:
    """ANSI color codes."""

    RED = "\033[0;31m"
    GREEN = "\033[0;32m"
    YELLOW = "\033[1;33m"
    BLUE = "\033[0;34m"
    NC = "\033[0m"  # No Color


def validate_workflow(file_path: Path) -> tuple[bool, list[str]]:
    """
    Validate a GitHub Actions workflow file.

    Args:
        file_path: Path to the workflow YAML file

    Returns:
        Tuple of (is_valid, list_of_issues)
    """
    try:
        with open(file_path) as f:
            data = yaml.safe_load(f)

        issues = []

        # Check for workflow essentials
        # 'on' might be parsed as True (boolean) in YAML
        if "on" not in data and True not in data:
            issues.append("Missing 'on' trigger definition")

        if "jobs" not in data:
            issues.append("Missing 'jobs' definition")
            return False, issues

        # Check each job
        for job_name, job_config in data["jobs"].items():
            if not isinstance(job_config, dict):
                issues.append(f"Job '{job_name}' is not properly configured")
                continue

            if "runs-on" not in job_config:
                issues.append(f"Job '{job_name}' missing 'runs-on'")

            if "steps" not in job_config:
                issues.append(f"Job '{job_name}' missing 'steps'")

        return len(issues) == 0, issues

    except yaml.YAMLError as e:
        return False, [f"YAML syntax error: {e}"]
    except Exception as e:
        return False, [f"Error: {e}"]


def validate_yaml_file(file_path: Path) -> tuple[bool, list[str]]:
    """
    Validate a generic YAML file.

    Args:
        file_path: Path to the YAML file

    Returns:
        Tuple of (is_valid, list_of_issues)
    """
    try:
        with open(file_path) as f:
            yaml.safe_load(f)
        return True, []
    except yaml.YAMLError as e:
        return False, [f"YAML syntax error: {e}"]
    except Exception as e:
        return False, [f"Error: {e}"]


def main():
    """Main validation function."""
    print(f"{Colors.BLUE}🔍 Validating GitHub Actions Workflows...{Colors.NC}\n")

    repo_root = Path.cwd()
    workflow_dir = repo_root / ".github" / "workflows"
    all_valid = True

    # Validate workflow files
    if not workflow_dir.exists():
        print(f"{Colors.RED}❌ Workflow directory not found: {workflow_dir}{Colors.NC}")
        sys.exit(1)

    print(f"📁 Checking workflow files in {workflow_dir.relative_to(repo_root)}\n")

    workflow_files = sorted(workflow_dir.glob("*.yml"))
    if not workflow_files:
        print(f"{Colors.YELLOW}⚠️  No workflow files found{Colors.NC}\n")
    else:
        for workflow in workflow_files:
            filename = workflow.name
            print(f"  Validating {filename}... ", end="")

            valid, issues = validate_workflow(workflow)

            if valid:
                print(f"{Colors.GREEN}✅ Valid{Colors.NC}")
            else:
                print(f"{Colors.RED}❌ Invalid{Colors.NC}")
                for issue in issues:
                    print(f"    {Colors.RED}Error: {issue}{Colors.NC}")
                all_valid = False

    print()

    # Validate dependabot.yml
    print("📁 Checking Dependabot configuration\n")
    dependabot_file = repo_root / ".github" / "dependabot.yml"

    if dependabot_file.exists():
        print("  Validating dependabot.yml... ", end="")
        valid, issues = validate_yaml_file(dependabot_file)

        if valid:
            print(f"{Colors.GREEN}✅ Valid{Colors.NC}")
        else:
            print(f"{Colors.RED}❌ Invalid{Colors.NC}")
            for issue in issues:
                print(f"    {Colors.RED}Error: {issue}{Colors.NC}")
            all_valid = False
    else:
        print(f"  {Colors.YELLOW}⚠️  dependabot.yml not found{Colors.NC}")

    print()

    # Validate pre-commit config
    print("📁 Checking Pre-commit configuration\n")
    precommit_file = repo_root / ".pre-commit-config.yaml"

    if precommit_file.exists():
        print("  Validating .pre-commit-config.yaml... ", end="")
        valid, issues = validate_yaml_file(precommit_file)

        if valid:
            print(f"{Colors.GREEN}✅ Valid{Colors.NC}")
        else:
            print(f"{Colors.RED}❌ Invalid{Colors.NC}")
            for issue in issues:
                print(f"    {Colors.RED}Error: {issue}{Colors.NC}")
            all_valid = False
    else:
        print(f"  {Colors.YELLOW}⚠️  .pre-commit-config.yaml not found{Colors.NC}")

    print()

    # Summary
    print("━" * 50)
    if all_valid:
        print(f"{Colors.GREEN}✅ All workflows are valid!{Colors.NC}\n")
        print("Next steps:")
        print("  1. Commit the workflow files")
        print("  2. Push to GitHub")
        print("  3. Check Actions tab for workflow runs")
        print("  4. Set up branch protection rules")
        sys.exit(0)
    else:
        print(f"{Colors.RED}❌ Some workflows have errors{Colors.NC}\n")
        print("Please fix the errors above before committing.")
        sys.exit(1)


if __name__ == "__main__":
    main()
