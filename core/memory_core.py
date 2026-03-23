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

    def search(self, query: str, limit: int = 10) -> Dict[str, Any]:
        query = query.strip()
        if not query:
            return {"query": query, "results": [], "note": "Empty query."}

        candidates = [
            self.workspace_root / "memory" / "core" / "MEMORY.md",
            *sorted((self.workspace_root / "memory" / "daily").glob("*.md")),
        ]
        query_terms = [term.lower() for term in query.split() if term.strip()]
        scored: List[Dict[str, Any]] = []
        for path in candidates:
            if not path.exists():
                continue
            content = path.read_text(encoding="utf-8")
            lowered = content.lower()
            score = sum(lowered.count(term) for term in query_terms)
            if score <= 0:
                continue
            snippet = self._build_snippet(content, query_terms)
            scored.append({"path": str(path), "score": score, "snippet": snippet})

        scored.sort(key=lambda item: (-item["score"], item["path"]))
        return {"query": query, "results": scored[:limit], "backend": "simple_text_search"}

    def _build_snippet(self, content: str, query_terms: List[str], max_chars: int = 240) -> str:
        lowered = content.lower()
        index = min((lowered.find(term) for term in query_terms if term in lowered), default=0)
        start = max(index - 60, 0)
        end = min(start + max_chars, len(content))
        return content[start:end].replace("\n", " ").strip()
