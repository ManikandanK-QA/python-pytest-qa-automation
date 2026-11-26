"""Shared, git-ignored paths.

Keeping them in one place stops the same directory name drifting between the
pytest configuration, the fixtures and the documentation.
"""

from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]

ARTIFACTS_DIR = PROJECT_ROOT / "artifacts"
AUTH_DIR = PROJECT_ROOT / ".auth"
RESULTS_DIR = PROJECT_ROOT / "reports"
