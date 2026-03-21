"""Memory domain core.

Business/domain logic only. No dependency on global skill governance.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from daemon.memory_master_daemon import MemoryMasterDaemon


class MemoryCore:
    def __init__(self, workspace_root="."):
        self.workspace_root = Path(workspace_root).resolve()
        self.daemon = MemoryMasterDaemon(self.workspace_root)

    def status(self) -> Dict[str, Any]:
        return {
            "workspace": str(self.workspace_root),
            "core_exists": (self.workspace_root / "memory" / "core" / "MEMORY.md").exists(),
            "daily_dir": str(self.workspace_root / "memory" / "daily"),
            "archive_dir": str(self.workspace_root / "memory" / "archive"),
        }

    def consolidate(self) -> Dict[str, Any]:
        result = self.daemon.run_daily_maintenance()
        return {"processed": result}

    def search(self, query: str) -> Dict[str, Any]:
        # Placeholder: keep domain API boundary now; real search backend can plug in later.
        return {"query": query, "results": [], "note": "Search backend not yet bound in MemoryCore."}
