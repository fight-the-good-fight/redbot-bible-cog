"""File-backed store for Bible memories (notes).

Memories live in a dedicated ``memories.json`` file inside the cog's data
directory, separate from the cog's ``settings.json``. This keeps the cog
settings clean and makes memories easy to back up, migrate, and share.
"""

import json
from pathlib import Path
from typing import List, Optional

from redbot.core import data_manager

MEMORIES_FILENAME = "memories.json"
COG_NAME = "Bible"


def memories_path() -> Path:
    """Return the path to the memories file for this cog."""
    return data_manager.cog_data_path(raw_name=COG_NAME) / MEMORIES_FILENAME


def _resolve(path: Optional[Path]) -> Path:
    return path if path is not None else memories_path()


def load_memories(path: Optional[Path] = None) -> List[dict]:
    """Load memories from disk.

    Returns an empty list if the file is missing, unreadable, or does not
    contain a JSON list.
    """
    p = _resolve(path)
    if not p.exists():
        return []
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []
    return data if isinstance(data, list) else []


def save_memories(memories: List[dict], path: Optional[Path] = None) -> None:
    """Write memories to disk, creating parent directories as needed."""
    p = _resolve(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(memories, indent=2), encoding="utf-8")