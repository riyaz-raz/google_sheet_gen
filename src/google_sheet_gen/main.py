"""
Git Commit Logger - Logs git commits to Google Sheets

Usage:
    python -m report_gen.main
"""

import sys

from google_sheet_gen.config import ConfigLoader
from google_sheet_gen.git import GitCommitFetcher
from google_sheet_gen.sheets import SheetSender
from google_sheet_gen.utils import get_current_month


def print_header():
    """Print application header."""
    print("🚀 Git Commit Logger")
    print("=" * 50)
    print(f"📅 Logging commits for: {get_current_month()}")
    print("🔄 Mode: Clear sheet and replace with fresh data")
    print("=" * 50)


def main():
    """Main entry point."""
    # Print header
    print_header()

    # Load configuration
    config = ConfigLoader("config.json")
    config.load()
    config.print_summary()
    print()

    # Get settings
    repositories = config.get_repositories()
    sheet_url = config.get_sheet_url()
    settings = config.get_settings()

    # Get settings with defaults
    max_commits = settings.get("max_commits_per_run", None)
    timeout = settings.get("timeout", 120)  # Increased default timeout
    retries = settings.get("retries", 3)

    # Fetch commits
    print("📂 Fetching commits from repositories...")
    print("-" * 50)

    fetcher = GitCommitFetcher(max_commits)
    all_commits = fetcher.fetch_all_repos(repositories)

    if not all_commits:
        print("\nℹ️ No commits found for this month")
        print("   Sheet will be cleared (no data to add)")

        # Still clear the sheet
        sender = SheetSender(sheet_url, retries=retries, timeout=timeout)
        sender.send_commits([])
        print("\n📊 Sheet cleared successfully")
        print("=" * 50)
        print("🏁 Done!")
        return

    # Sort commits by date (newest first)
    all_commits.sort(key=lambda x: x["date"], reverse=True)

    # Send to Google Sheets in a single request
    print("-" * 50)
    sender = SheetSender(sheet_url, retries=retries, timeout=timeout)

    success_count, total_count = sender.send_commits(all_commits)

    # Print summary
    print("\n" + "=" * 50)
    if success_count == total_count and success_count > 0:
        print(
            f"📊 Successfully logged all {success_count} commits for {get_current_month()}"
        )
    elif success_count > 0:
        print(
            f"📊 Partially logged {success_count}/{total_count} commits for {get_current_month()}"
        )
        print("💡 Run the script again to retry failed commits")
    elif success_count == 0 and total_count > 0:
        print("❌ Failed to log commits. Check your configuration and network.")
        print(f"💡 Try increasing 'timeout' in config (currently {timeout}s)")
        sys.exit(1)
    else:
        print("📊 Sheet cleared successfully")
    print("🏁 Done!")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Interrupted by user")
        print("ℹ️ Sheet may be partially updated. Run again to complete.")
        sys.exit(0)
    except (ValueError, OSError, KeyError, TypeError) as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
