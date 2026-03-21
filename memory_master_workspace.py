#!/usr/bin/env python3
"""Workspace-bound production entrypoint for Memory Master."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

from memory_master import MemoryMaster

DEFAULT_WORKSPACE = Path(os.environ.get("MEMORY_MASTER_WORKSPACE", "/Users/hidream/.openclaw/workspace")).resolve()


def get_memory_master(workspace: str | None = None) -> MemoryMaster:
    return MemoryMaster(str(Path(workspace).resolve() if workspace else DEFAULT_WORKSPACE))


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    mm = get_memory_master()

    if not argv:
        print(json.dumps({
            "status": "success",
            "workspace": str(DEFAULT_WORKSPACE),
            "message": "memory-master workspace-bound entrypoint ready",
        }, indent=2, ensure_ascii=False))
        return 0

    action = argv[0]
    if action == "write":
        content = " ".join(argv[1:]) if len(argv) > 1 else "Empty entry"
        print(json.dumps(mm.write_daily(content), indent=2, ensure_ascii=False))
        return 0
    if action == "consolidate":
        dry_run = "--dry-run" in argv
        print(json.dumps(mm.consolidate(dry_run=dry_run), indent=2, ensure_ascii=False))
        return 0
    if action == "archive":
        days = int(argv[1]) if len(argv) > 1 else 7
        print(json.dumps(mm.archive(days=days), indent=2, ensure_ascii=False))
        return 0
    if action == "search":
        query = argv[1] if len(argv) > 1 else "test"
        limit = int(argv[2]) if len(argv) > 2 else 5
        print(json.dumps(mm.search(query=query, limit=limit), indent=2, ensure_ascii=False))
        return 0
    if action == "recall":
        query = argv[1] if len(argv) > 1 else "test"
        limit = int(argv[2]) if len(argv) > 2 else 5
        print(json.dumps(mm.recall(query=query, limit=limit), indent=2, ensure_ascii=False))
        return 0
    if action == "index":
        print(json.dumps(mm.build_index(), indent=2, ensure_ascii=False))
        return 0
    if action == "status":
        print(json.dumps(mm.status(), indent=2, ensure_ascii=False))
        return 0

    print(json.dumps({"status": "error", "error": f"Unknown action: {action}"}, ensure_ascii=False))
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
