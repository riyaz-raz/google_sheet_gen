"""
Report Generator - Git commit logger for Google Sheets.

This package fetches git commits from multiple repositories and logs them
to a Google Sheet via a web app.
"""

from google_sheet_gen.main import main
from google_sheet_gen.config import ConfigLoader
from google_sheet_gen.git import GitCommitFetcher
from google_sheet_gen.sheets import SheetSender

__version__ = "0.1.0"
__all__ = [
    "main",
    "ConfigLoader",
    "GitCommitFetcher",
    "SheetSender",
]
