---
name: memory-master
description: 统一的记忆管理中枢 (Memory Master)。整合了记忆归档(architect)、记忆去重(dedup)、记忆蒸馏(distiller)功能。当用户要求“清理记忆”、“去重记忆”、“蒸馏记忆”时调用。
---

# 🧠 Memory Master (统一记忆管理中枢)

本技能聚合了此前散落的多个记忆相关能力，避免上下文工具槽污染。
请根据用户的具体需求，选择调用对应的子脚本。

## 场景映射与执行指令

### 1. 记忆冷启动归档 (Archive / Architect)
**场景**：用户说“清理记忆”、“归档老旧日志”、“把没用的日志删掉”。
**底层逻辑**：自动扫描 `memory/daily/` 目录下超过 7 天的文件，并将其打包归档至 `memory/archive/YYYY-MM/`，同时审计 Skill 的闲置 ROI。
**执行命令**：
```bash
python3 /root/.openclaw/workspace/skills/memory-master/scripts/memory_manager.py
```

### 2. 核心记忆去重 (Deduplication)
**场景**：用户说“去重记忆”、“合并一下 MEMORY.md”、“看看记忆里有没有冲突”。
**底层逻辑**：通过 Jaccard 相似度扫描 `MEMORY.md` 里的所有条目，合并重复项，清理过时状态，并自动生成备份文件 `MEMORY-backup-*.md`。
**执行命令**：
```bash
node /root/.openclaw/workspace/skills/memory-master/scripts/dedup.mjs
```

### 3. 记忆蒸馏 (Distill)
**场景**：用户说“蒸馏最近的记忆”、“提取一下金线”。
**底层逻辑**：AI 主动读取最近 3 天的 `memory/daily/*.md` 文件，人工提取具有长期价值的“习惯、错误教训、决定”，并用 `write/edit` 工具主动将其追加到 `MEMORY.md` 的合适位置。*(本动作由大模型利用原生读写工具完成，无专属自动化脚本)*。

---
*注：此技能取代了原先独立的 `memory-architect`, `memory-dedup`, `memory-distiller`，调用者需根据意图判断执行哪个命令。*
