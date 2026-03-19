---
name: memory-master
description: 记忆管理 skill：自动整理、归档、检索记忆日志，支持上下文整合、提炼与去重
version: 1.1.0
category: knowledge
---

# Memory Master Skill

把本仓库的记忆管理能力以 Skill 形式暴露出来，便于被工作流、Agent 或脚本直接调用。

## 能力

| Action | 描述 |
|---|---|
| `write` | 写入当日日志 |
| `consolidate` | 从 daily 提取高价值内容，去重后合并进 core |
| `archive` | 归档超过阈值的 daily 日志 |
| `index` | 建立 / 重建本地索引 |
| `search` | 搜索 daily / archive / distilled 内容 |
| `status` | 查看记忆系统状态 |

## 建议目录结构

```text
memory/
├── core/MEMORY.md
├── daily/
├── archive/
├── distilled/
└── index/
    ├── vector_index.db
    ├── memory_index.json
    └── processed_logs.json
```

## CLI 用法

```bash
python memory_master.py write "今天解决了部署问题"
python memory_master.py consolidate --dry-run
python memory_master.py consolidate
python memory_master.py archive 7
python memory_master.py index
python memory_master.py search "部署问题" 5
python memory_master.py status
```

## 设计取向

- 保持仓库本身轻量，不强绑定 OpenClaw runtime
- 但保留 skill 化接口与目录约定，方便后续接进更大的工作流引擎
- 优先本地可运行、可维护，而不是过度框架化
