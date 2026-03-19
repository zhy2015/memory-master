# Memory Master

轻量级 AI 记忆管理系统，同时提供一套可被工作流 / Agent 调用的 **memory-master skill**。

## 当前能力

- 记忆写入：`write_daily`
- 记忆整合：`consolidate`
- 日志归档：`archive`
- 本地索引：`build_index`
- 相似搜索：`search`
- 最小工作流引擎：`workflow_engine/`
- Action Registry：把 memory actions 注册进 pipeline
- 测试与示例：`tests/`、`examples/`

## 这次从 openclaw-core 抽了什么

只抽真正适合独立仓库维护的部分：

- skill 描述与 manifest
- 最小 workflow engine 思路
- async context
- 动作编排骨架
- 不强绑定 OpenClaw runtime 的 action registry 方式

没硬搬整个大引擎，避免仓库过胖。

## 快速开始

```python
from memory_master import MemoryMaster

mm = MemoryMaster("/path/to/workspace")
mm.write_daily("学习了新的部署流程...", metadata={"tags": ["ops"]})
mm.consolidate()
results = mm.search("部署")
print(results)
```

## CLI

```bash
python memory_master.py write "学习了新的部署流程"
python memory_master.py consolidate --dry-run
python memory_master.py consolidate
python memory_master.py archive 7
python memory_master.py index
python memory_master.py search "部署问题" 5
python memory_master.py status
memory-master-runner --help
```

`memory-master-runner` 是打包后的 console script，可直接执行 JSON pipeline。

## Demo Pipeline

直接运行：

```bash
python examples/pipeline_demo.py
```

它会执行：

```text
write -> consolidate -> index -> search -> status
```

## Registry 用法

```python
from memory_master import MemoryMaster
from workflow_engine import ActionRegistry, WorkflowEngine, WorkflowNode, WorkflowPipeline

mm = MemoryMaster("/tmp/demo-memory")
registry = ActionRegistry()
registry.register("write", lambda content: mm.write_daily(content))
registry.register("consolidate", lambda: mm.consolidate())
registry.register("index", lambda: mm.build_index())
registry.register("search", lambda query: mm.search(query=query, limit=3))

pipeline = (
    WorkflowPipeline("demo", "demo")
    .add_node(WorkflowNode("write", "write", inputs={"content": "LEARNED: registry keeps wiring clean"}))
    .add_node(WorkflowNode("index", "index"))
    .add_edge("write", "index")
)

# asyncio.run(WorkflowEngine(registry.as_dict()).execute(pipeline))
```

## 目录结构

```text
memory/
├── daily/
├── distilled/
├── core/
├── archive/
└── index/

examples/
workflow_engine/
skill-memory-master/
tests/
```

## 提取规则

自动提取以下内容到核心记忆：

- `FAILED: xxx` → `failure_pattern`
- `SUCCESS(xxx)` → `success_pattern`
- `DECISION: xxx` → `decision`
- `LEARNED: xxx` → `learning`

## 测试

```bash
python -m unittest discover -s tests -v
```

当前测试覆盖：
- memory API 基础能力
- workflow registry / resume / validation / history
- CLI runner
- 独立节点并行执行
- 包构建可用性

完整安装与验收见 `INSTALL.md`。

## 依赖

```text
python >= 3.8
numpy
```

## License

MIT
