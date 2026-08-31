"""cPanel/Passenger WSGI entry point for LTMD Analytics.

Configure the cPanel Python application to use this file as its startup entry point.
Private data paths must be supplied through environment variables and must not live under
public_html or inside the Git repository.
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from analytics_api.app import application  # noqa: E402,F401
