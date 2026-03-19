# Memory Master

轻量级 AI 记忆管理系统。支持记忆分层存储、自动整合、语义搜索。

## 快速开始

```python
from memory_master import MemoryMaster

# 初始化
mm = MemoryMaster("/path/to/workspace")

# 写入日常记忆
mm.write_daily("学习了新的部署流程...")

# 整合记忆（提取高价值内容到核心记忆）
mm.consolidate()

# 搜索记忆
results = mm.search("部署")
```

## 目录结构

```
memory/
├── daily/          # 每日原始日志
├── core/           # 核心记忆（整合后）
├── archive/        # 归档（>7天）
└── index/          # 向量索引
```

## 功能

- **write_daily**: 写入日常记忆
- **consolidate**: 整合记忆，提取关键信息
- **archive**: 归档过期日志
- **search**: 语义搜索
- **status**: 查看系统状态

## 依赖

```
python >= 3.8
numpy
```

## License

MIT
