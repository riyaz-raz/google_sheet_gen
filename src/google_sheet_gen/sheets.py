"""
Google Sheets integration for sending commit data.
"""

import json
import time
from typing import Any

import requests


class SheetSender:
    """Sends commit data to Google Sheets via web app."""

    def __init__(self, sheet_url: str, retries: int = 3, timeout: int = 60):
        """
        Initialize sheet sender.

        Args:
            sheet_url: Google Sheets web app URL
            retries: Number of retry attempts
            timeout: Request timeout in seconds
        """
        self.sheet_url = sheet_url
        self.retries = retries
        self.timeout = timeout

    def send_commits(self, commits: list[dict[str, Any]]) -> tuple[int, int]:
        """
        Send commits to Google Sheets.

        Args:
            commits: List of commit dictionaries

        Returns:
            tuple: (success_count, total_count)
        """
        if not commits:
            print("📊 No commits to send. Sending empty update to clear sheet...")
            return self._send_empty_update()

        print(f"📤 Sending {len(commits)} commits to Google Sheets...")
        print(f"   🔄 Retries: {self.retries}, Timeout: {self.timeout}s")

        # Prepare data
        commit_data = []
        for commit in commits:
            commit_data.append(
                {
                    "repo": commit["repo"],
                    "hash": commit["hash"],
                    "author": commit["author"],
                    "email": commit["email"],
                    "message": commit["message"],
                    "date": commit["date"],
                }
            )

        payload = {"action": "update_commits", "commits": commit_data}

        return self._send_request(payload)

    def _send_empty_update(self) -> tuple[int, int]:
        """Send empty update to clear the sheet."""
        payload = {"action": "update_commits", "commits": []}
        return self._send_request(payload)

    def _send_request(self, payload: dict[str, Any]) -> tuple[int, int]:
        """
        Send HTTP request with retry logic.

        Returns:
            tuple: (success_count, total_count)
        """
        for attempt in range(self.retries):
            try:
                response = requests.post(
                    self.sheet_url,
                    json=payload,
                    timeout=self.timeout,
                    headers={"Content-Type": "application/json"},
                )

                response.raise_for_status()

                # Parse response
                result = response.json()
                status = result.get("status", "unknown")
                message = result.get("message", "")

                if status == "success":
                    print(f"   ✅ Success: {message}")
                    # Return counts based on response
                    total = len(payload.get("commits", []))
                    return (total, total)
                else:
                    print(f"   ❌ Server error: {status} - {message}")
                    if attempt < self.retries - 1:
                        print(f"      🔄 Retrying in {2**attempt}s...")
                        time.sleep(2**attempt)
                    continue

            except requests.exceptions.Timeout:
                print(f"   ⏰ Timeout (attempt {attempt + 1}/{self.retries})")
                if attempt < self.retries - 1:
                    print(f"      🔄 Retrying in {2**attempt}s...")
                    time.sleep(2**attempt)
            except requests.exceptions.RequestException as e:
                print(f"   ❌ Request failed: {e}")
                if attempt < self.retries - 1:
                    print(f"      🔄 Retrying in {2**attempt}s...")
                    time.sleep(2**attempt)
            except json.JSONDecodeError as e:
                print(f"   ❌ Invalid response: {e}")
                break

        print(f"   ❌ Failed after {self.retries} attempts")
        total = len(payload.get("commits", []))
        return (0, total)
