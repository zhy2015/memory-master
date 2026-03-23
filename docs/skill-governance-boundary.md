# Skill Governance Boundary

## Target split

- Control plane: `core/infra/skill_manager.py`, `core/infra/skill_contracts.py`
- Domain core: e.g. `memory/core/memory_core.py`
- Adapter layer: e.g. `memory/adapters/memory_skill_adapter.py`

## Rules

1. Governance depends only on `ISkill`.
2. Domain core must not import governance/runtime registry concerns.
3. Adapters are the only place allowed to translate domain APIs into tool schemas.
4. `GlobalContext` stays capability-scoped and minimal.

## Migration note

Existing manifest/registry paths can keep running during transition.
The new `SkillManager` path is a cleaner control-plane abstraction for future refactors.
