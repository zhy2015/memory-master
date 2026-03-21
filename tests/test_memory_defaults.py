from pathlib import Path

from core.memory_core import MemoryCore
from daemon.memory_master_daemon import MemoryMasterDaemon


def test_memory_core_defaults_to_current_working_directory_workspace(monkeypatch, tmp_path: Path):
    monkeypatch.chdir(tmp_path)
    core = MemoryCore()
    assert core.workspace_root == tmp_path.resolve()


def test_memory_daemon_defaults_to_current_working_directory_workspace(monkeypatch, tmp_path: Path):
    monkeypatch.chdir(tmp_path)
    daemon = MemoryMasterDaemon()
    assert daemon.memory_root == tmp_path.resolve() / "memory"
