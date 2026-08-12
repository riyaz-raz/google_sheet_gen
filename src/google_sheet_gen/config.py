"""
Configuration loading and validation.
"""

import json
import sys
from pathlib import Path
from typing import Any


class ConfigLoader:
    """Handles loading and validating configuration."""

    def __init__(self, config_path: str = "config.json"):
        self.REQUIRED_FIELDS = ["google_sheet_url", "repositories"]

        """
        Initialize config loader.

        Args:
            config_path: Path to config file
        """
        self.config_path = Path(config_path)
        self.config: dict[str, Any] | None = None

    def load(self) -> dict[str, Any]:
        """
        Load and validate configuration.

        Returns:
            Configuration dictionary

        Raises:
            SystemExit: If config is invalid
        """
        try:
            with open(self.config_path, "r") as f:
                self.config = json.load(f)

            self._validate()
            # Assert to narrow the type from dict|None to dict
            assert self.config is not None
            return self.config

        except FileNotFoundError:
            print(f"❌ Config file '{self.config_path}' not found!")
            print("📋 Please create config.json based on config.example.json")
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"❌ Error parsing config file: {e}")
            sys.exit(1)

    def _validate(self) -> None:
        """Validate required fields in config."""
        if not self.config:
            raise ValueError("Configuration not loaded")

        for field in self.REQUIRED_FIELDS:
            if field not in self.config:
                print(f"❌ Missing required field: '{field}' in config")
                sys.exit(1)

        if not self.config["google_sheet_url"]:
            print("❌ Google Sheet URL is empty in config")
            sys.exit(1)

        if not self.config["repositories"]:
            print("❌ No repositories specified in config")
            sys.exit(1)

    def get_repositories(self) -> list[str]:
        """Get list of repositories from config."""
        return self.config.get("repositories", []) if self.config else []

    def get_sheet_url(self) -> str:
        """Get Google Sheets web app URL."""
        return self.config.get("google_sheet_url", "") if self.config else ""

    def get_settings(self) -> dict[str, Any]:
        """Get settings from config."""
        return self.config.get("settings", {}) if self.config else {}

    def print_summary(self) -> None:
        """Print configuration summary."""
        if not self.config:
            return

        print("📋 Configuration:")
        print(f"   Sheet URL: {self.config['google_sheet_url'][:50]}...")
        print(f"   Repositories: {len(self.config['repositories'])}")

        settings = self.config.get("settings", {})
        if settings:
            print("   Settings:")
            for key, value in settings.items():
                print(f"      {key}: {value}")
