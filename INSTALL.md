# Install & Verify

## Install from source

```bash
git clone git@github.com:zhy2015/memory-master.git
cd memory-master
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -e .
```

## Verify CLI entrypoint

```bash
memory-master-runner --help
```

## Verify package build

```bash
python3 -m build
ls -la dist/
```

## Verify test suite

```bash
python3 -m unittest discover -s tests -v
```

## Minimal workflow run

```bash
cat > /tmp/mm-pipeline.json <<'JSON'
{
  "pipeline_id": "quick-demo",
  "name": "quick demo",
  "nodes": [
    {
      "node_id": "write",
      "action": "skill://memory-master/write",
      "inputs": {"content": "LEARNED: install verification keeps releases honest"},
      "outputs": ["file"]
    },
    {
      "node_id": "index",
      "action": "memory://index",
      "outputs": ["indexed_chunks"]
    }
  ],
  "edges": [["write", "index"]]
}
JSON

memory-master-runner /tmp/mm-pipeline.json --workspace /tmp/mm-workspace
```

## Notes

- Parallel execution is supported with `--parallel` for independent DAG nodes.
- Default local proxy on this machine is `127.0.0.1:7897`; export it only when your environment requires outbound proxying.
