#!/usr/bin/env python3
"""Local ops check for this deployment's memory configuration.

This script is intentionally environment-specific and should not be treated as a
repository-generic health check.
"""

import json
import os
import subprocess
import sys
from pathlib import Path

CONFIG = Path(os.environ.get('OPENCLAW_CONFIG', '/root/.openclaw/openclaw.json'))
EXPECTED_WORKSPACE = os.environ.get('OPENCLAW_WORKSPACE', '/root/.openclaw/workspace')


def fail(msg, code=1):
    print(f'FAIL: {msg}')
    sys.exit(code)


def ok(msg):
    print(f'OK: {msg}')


if not CONFIG.exists():
    fail(f'missing config: {CONFIG}')

obj = json.loads(CONFIG.read_text())

workspace = obj.get('agents', {}).get('defaults', {}).get('workspace')
backend = obj.get('memory', {}).get('backend')
mem_search = obj.get('agents', {}).get('defaults', {}).get('memorySearch', {})
provider = mem_search.get('provider')
fallback = mem_search.get('fallback')
chat_base = obj.get('models', {}).get('providers', {}).get('openai', {}).get('baseUrl')
expected_chat_base = os.environ.get('OPENCLAW_EXPECTED_BASEURL', 'https://ai.td.ee/v1')

if workspace != EXPECTED_WORKSPACE:
    fail(f'workspace drift: {workspace!r} != {EXPECTED_WORKSPACE!r}')
ok(f'workspace={workspace}')

if backend != 'qmd':
    fail(f'memory backend drift: {backend!r} != \'qmd\'')
ok(f'memory.backend={backend}')

if provider != 'local':
    fail(f'memorySearch.provider drift: {provider!r} != \'local\'')
ok(f'memorySearch.provider={provider}')

if fallback != 'none':
    fail(f'memorySearch.fallback drift: {fallback!r} != \'none\'')
ok(f'memorySearch.fallback={fallback}')

if chat_base != expected_chat_base:
    fail(f'chat provider baseUrl drift: {chat_base!r} != {expected_chat_base!r}')
ok(f'chat provider baseUrl preserved: {chat_base}')

cmd = ['openclaw', 'memory', 'status', '--deep', '--json']
proc = subprocess.run(cmd, capture_output=True, text=True)
if proc.returncode != 0:
    fail(f'status command failed: {proc.stderr.strip() or proc.stdout.strip()}')

try:
    payload = json.loads(proc.stdout)
except json.JSONDecodeError as e:
    fail(f'invalid status json: {e}')

if not payload or 'status' not in payload[0]:
    fail('unexpected status payload shape')

status = payload[0]['status']
probe = payload[0].get('embeddingProbe', {})
scan = payload[0].get('scan', {})

if status.get('workspaceDir') != EXPECTED_WORKSPACE:
    fail(f"runtime workspaceDir drift: {status.get('workspaceDir')!r}")
ok(f"runtime workspaceDir={status.get('workspaceDir')}")

if status.get('backend') != 'qmd':
    fail(f"runtime backend drift: {status.get('backend')!r}")
ok(f"runtime backend={status.get('backend')}")

if status.get('provider') != 'qmd':
    fail(f"runtime provider drift: {status.get('provider')!r}")
ok(f"runtime provider={status.get('provider')}")

if not probe.get('ok'):
    fail('embedding probe not ok')
ok('embedding probe ok')

if scan.get('totalFiles', 0) <= 0:
    fail('memory scan found zero files')
ok(f"memory files={scan.get('totalFiles')}")

print('PASS: memory config and runtime status healthy')
