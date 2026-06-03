"""Pytest configuration for direct MCP server test execution."""

from __future__ import annotations

import sys
from pathlib import Path

MCP_SERVER_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = MCP_SERVER_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))
