"""
Git operations for fetching commit data - Fixed date filtering.
"""

import os
import subprocess
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

from google_sheet_gen.utils import (
    clean_commit_message,
    format_git_date,
    format_project_name,
)


class GitCommitFetcher:
    """Fetches commits from git repositories - Fixed date handling."""

    def __init__(self, max_commits: int | None = None):
        """
        Initialize git commit fetcher.

        Args:
            max_commits: Maximum commits per repo. None for all.
        """
        self.max_commits = max_commits

    def is_git_repo(self, path: str) -> bool:
        """Check if a path is a valid git repository."""
        git_dir = Path(path) / ".git"
        return git_dir.exists() and git_dir.is_dir()

    def get_month_start(self) -> str:
        """
        Get the first day of current month for git log.
        Git's --since excludes the start date, so we subtract 1 day.
        """
        now = datetime.now(UTC)
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        # Subtract 1 day to include the 1st of the month
        include_start = month_start - timedelta(days=1)
        return include_start.strftime("%Y-%m-%d")

    def get_commits_for_month(self, repo_path: str) -> list[dict[str, Any]]:
        """
        Get all commits from current month for a repository.
        FIXED: Includes the 1st day of the month.
        """
        if not self.is_git_repo(repo_path):
            print(f"⚠️ Skipping: {repo_path} is not a valid git repository")
            return []

        try:
            month_start = self.get_month_start()

            # Get only commit hashes first (faster)
            hash_command = [
                "git",
                "-C",
                repo_path,
                "log",
                "--since",
                month_start,
                "--format=%H",
            ]

            if self.max_commits:
                hash_command.insert(4, f"-{self.max_commits}")

            hash_result = subprocess.run(
                hash_command, capture_output=True, text=True, check=True
            )

            hashes = hash_result.stdout.strip().split("\n")
            if not hashes or not hashes[0]:
                return []

            # Then get full details for each commit
            command = [
                "git",
                "-C",
                repo_path,
                "log",
                "--since",
                month_start,
                "--pretty=format:%H|%an|%ae|%s|%ad",
                "--no-patch",
            ]

            if self.max_commits:
                command.insert(4, f"-{self.max_commits}")

            result = subprocess.run(command, capture_output=True, text=True, check=True)

            output = result.stdout.strip()
            if not output:
                return []

            # Parse commits
            commits = []
            project_name = format_project_name(repo_path)

            for line in output.split("\n"):
                commit = self._parse_commit_line(line, project_name, repo_path)
                if commit:
                    commits.append(commit)

            return commits

        except subprocess.CalledProcessError as e:
            print(f"⚠️ Error reading git log in {repo_path}: {e}")
            return []
        except (OSError, subprocess.SubprocessError, ValueError) as e:
            print(f"⚠️ Error in {repo_path}: {e}")
            return []

    def _parse_commit_line(
        self, line: str, project_name: str, repo_path: str
    ) -> dict[str, Any] | None:
        """Parse a single git log line."""
        try:
            hash_val, author, email, message, date = line.split("|", 4)

            return {
                "repo": project_name,
                "repo_raw": os.path.basename(repo_path),
                "hash": hash_val[:8],
                "full_hash": hash_val,
                "author": author,
                "email": email,
                "message": clean_commit_message(message),
                "raw_message": message,
                "date": format_git_date(date),
            }

        except ValueError:
            return None

    def fetch_all_repos(self, repos: list[str]) -> list[dict[str, Any]]:
        """
        Fetch commits from all repositories.
        """
        all_commits = []

        # Filter valid repos first
        valid_repos = []
        for repo_path in repos:
            repo_path = os.path.expanduser(repo_path)

            if not os.path.exists(repo_path):
                print(f"⚠️ Skipping: {repo_path} does not exist")
                continue

            if not self.is_git_repo(repo_path):
                print(f"⚠️ Skipping: {repo_path} is not a valid git repository")
                continue

            valid_repos.append(repo_path)

        if not valid_repos:
            return []

        print(f"📂 Processing {len(valid_repos)} repositories...")
        print(f"   📅 Including commits from: {self.get_month_start()} to today")

        # Process each repo
        for repo_path in valid_repos:
            print(f"   🔍 Scanning: {os.path.basename(repo_path)}")
            commits = self.get_commits_for_month(repo_path)

            if commits:
                all_commits.extend(commits)
                print(f"      ✅ Found {len(commits)} commit(s)")
            else:
                print("      ℹ️ No commits found")

        return all_commits
