# Memory Master (zhy2015/memory-master)

A unified memory management skill for OpenClaw agents. This skill consolidates the functionalities of memory archiving, deduplication, and distillation into a single, efficient tool.

## Features

- **Memory Archiving (architect)**: Compresses raw, daily conversation logs into the `memory/archive/` directory to prevent context bloating.
- **Memory Deduplication (dedup)**: Periodically scans `MEMORY.md` to remove redundant, conflicting, or overly detailed entries, maintaining a high-density, high-value core memory.
- **Memory Distillation (distiller)**: Extracts long-term patterns, facts, and essential rules from short-term daily logs (`memory/daily/`) and synthesizes them into `MEMORY.md` and `USER.md`.

## Usage

This skill is primarily designed to be invoked autonomously by the agent during scheduled maintenance cycles or when the user explicitly requests memory cleanup.

**Triggers:**
- "清理记忆" (Clean up memory)
- "去重记忆" (Deduplicate memory)
- "蒸馏记忆" (Distill memory)

## Design Philosophy

This tool is a core component of the "Three-Tier Memory Dam" (三级记忆水坝) architecture:
1. **Short-term**: `memory/daily/` (Raw logs)
2. **Long-term**: `MEMORY.md` / `USER.md` (Distilled rules and facts)
3. **Archive**: `memory/archive/` (Compressed history)

By managing these tiers, `memory-master` ensures the agent remains responsive and avoids the "hallucination and decision paralysis" often caused by an overgrown context window.
