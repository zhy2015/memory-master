# STARTUP_MEMORY_ROUTING

## Goal
Avoid loading long-term memory as startup ballast.

## Startup default
- Read only `STARTUP_MEMORY_CARD.md` and `memory/todos/active.md`
- Do not read full `memory/core/MEMORY.md` by default
- Do not read daily logs unless the task depends on very recent execution context

## When to search/read memory
Search memory first when the request is about:
- prior work
- decisions / reasons / why
- people / preferences
- dates / timelines
- todos / commitments

## Read order
1. `memory_search`
2. `memory_get` for small snippets
3. Full file read only if snippets are insufficient

## Anti-bloat rules
- Keep execution logs out of long-term memory
- Keep startup on routing, not full recall
- Project-specific details belong in project memory/manuals, not startup path
- Memory routing is a domain concern; cross-skill governance belongs to `skill-governance`, not to memory startup rules.
