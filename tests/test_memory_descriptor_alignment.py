from adapters.memory_skill_adapter import MemorySkillAdapter


def test_memory_adapter_exposes_governance_descriptor():
    adapter = MemorySkillAdapter()
    descriptor = adapter.get_descriptor()

    assert descriptor.name == 'system_memory'
    assert 'memory' in descriptor.task_nodes
    assert 'memory' in descriptor.tags
    assert descriptor.owner == 'harry-bot'
