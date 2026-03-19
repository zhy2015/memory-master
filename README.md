# Memory Master

轻量级 AI 记忆管理系统，同时提供一套可被工作流/Agent 调用的 **memory-master skill**。

## 这次改造做了什么

从 `zhy2015/openclaw-core` 抽离了真正有价值、且适合独立仓库维护的部分：

- skill 化描述（`skill-memory-master/SKILL.md`）
- manifest 动作定义（`skill-memory-master/manifest.json`）
- 更完整的本地索引 / 搜索能力
- 更清晰的目录约定：`daily / distilled / core / archive / index`
- 保持仓库轻量，不把整个 OpenClaw 工作流引擎硬搬进来

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
```

## 目录结构

```text
memory/
├── daily/          # 每日原始日志
├── distilled/      # 中间蒸馏层（可选）
├── core/           # 核心记忆（整合后）
├── archive/        # 归档（>7天）
└── index/          # 本地索引
```

## 功能

- **write_daily**: 写入日常记忆
- **consolidate**: 整合记忆，提取关键信息
- **archive**: 归档过期日志
- **search**: 基于本地可重建索引的相似搜索
- **build_index**: 构建索引
- **status**: 查看系统状态

## 提取规则

自动提取以下内容到核心记忆：

- `FAILED: xxx` → failure_pattern
- `SUCCESS(xxx)` → success_pattern
- `DECISION: xxx` → decision
- `LEARNED: xxx` → learning

## 依赖

```text
python >= 3.8
numpy
```

## License

MIT
