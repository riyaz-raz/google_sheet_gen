"""
Utility functions for the commit logger.
"""

import os
from datetime import UTC, datetime, timedelta


def get_current_month() -> str:
    """Get current month name and year."""
    return datetime.now(UTC).strftime("%B %Y")


def get_current_month_start() -> datetime:
    """Get the first day of current month."""
    now = datetime.now(UTC)
    return now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)


def clean_commit_message(message: str) -> str:
    """
    Clean commit message by removing common prefixes.

    Args:
        message: Raw commit message

    Returns:
        Cleaned commit message
    """
    prefixes = [
        "feat:",
        "fix:",
        "chore:",
        "docs:",
        "style:",
        "refactor:",
        "perf:",
        "test:",
        "build:",
        "ci:",
    ]

    cleaned = message
    for prefix in prefixes:
        if cleaned.lower().startswith(prefix):
            cleaned = cleaned[len(prefix) :].strip()
            break

    return cleaned


def format_project_name(repo_path: str) -> str:
    """
    Format repository path to a clean project name.

    Args:
        repo_path: Full repository path

    Returns:
        Formatted project name
    """
    repo_name = os.path.basename(repo_path)

    # Clean up common patterns
    replacements = {
        "_flutter": "",
        "_v2": "",
        "_v3": "",
        "_customer": " Customer",
        "_dealer": " Dealer",
        "_admin": " Admin",
    }

    project_name = repo_name
    for old, new in replacements.items():
        if old in project_name:
            project_name = project_name.replace(old, new)

    return project_name.title()


def format_git_date(date_str: str) -> str:
    """
    Convert git date format to readable format.

    Args:
        date_str: Git date string (e.g., "Fri Jul 25 14:30:00 2026 +0530")

    Returns:
        Formatted date (e.g., "2026-07-25 14:30")
    """
    try:
        date_part = date_str.split("+")[0].strip()
        commit_date = datetime.strptime(date_part, "%a %b %d %H:%M:%S %Y").replace(
            tzinfo=UTC
        )
        return commit_date.strftime("%Y-%m-%d %H:%M")
    except ValueError:
        return date_str


def is_in_current_month(date_str: str) -> bool:
    """
    Check if a git date string is in the current month.

    Args:
        date_str: Git date string

    Returns:
        True if date is in current month
    """
    try:
        date_part = date_str.split("+")[0].strip()
        commit_date = datetime.strptime(date_part, "%a %b %d %H:%M:%S %Y").replace(
            tzinfo=UTC
        )

        now = datetime.now(UTC)
        return commit_date.year == now.year and commit_date.month == now.month
    except ValueError, AttributeError, IndexError:
        return False


def get_month_start_for_git() -> str:
    """
    Get the first day of current month for git log.
    Git's --since excludes the start date, so we subtract 1 day.
    """
    now = datetime.now(UTC)
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    # Subtract 1 day to include the 1st of the month
    return (month_start - timedelta(days=1)).strftime("%Y-%m-%d")
