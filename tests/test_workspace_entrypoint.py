import json
import subprocess


def test_workspace_entrypoint_status_uses_bound_workspace():
    proc = subprocess.run(
        ['python3', 'memory_master_workspace.py', 'status'],
        capture_output=True,
        text=True,
        check=True,
    )
    data = json.loads(proc.stdout)
    assert data['status'] == 'success'
    assert 'directories' in data
