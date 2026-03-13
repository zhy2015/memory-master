# Heartbeat 驱动的自洁净机制 (Heartbeat-Driven Auto-Consolidation)

> 本机制定义了 Agent 如何利用 OpenClaw 的 Heartbeat (心跳) 轮询机制，实现自我环境的被动巡检与无感自清洁。

## 机制背景
Agent 在长期运行中，会因为用户的随机需求产生大量的“碎片化记忆”和“平铺的冗余工具”。如果纯靠主流程 prompt 的 `<available_skills>` 列表，会导致上下文膨胀与执行瘫痪。
为此，将 `memory-master` 的审计动作挂载到系统的潜意识轮询（`HEARTBEAT.md`）中，是实现“长久清爽”的最佳路径。

## 执行策略

### 1. 触发条件 (Trigger)
- **调度源**：系统底层的 cron 或 Gateway daemon 触发的心跳轮询（匹配 Heartbeat prompt）。
- **执行频次**：由系统的 Heartbeat 周期决定。建议在逻辑层面设定每 24-48 小时实际执行一次深层扫描。

### 2. 巡检动作 (Routines)

**动作 A: Skill 软链接与重叠度审计 (Context Consolidation)**
- **输入**：`workspace/skills/` 目录下的清单。
- **逻辑**：扫描最近 3 天新增的、功能平铺的 Skill。如果发现多个 Skill 功能重叠度高（例如多个处理文件的脚本），则在后台静默触发**重构**。
- **输出**：将其转化为“任务节点入口 + 底层软链接”的结构，清理冗余注册表。完成后向宿主发送异步简报（如：“已将 3 个抓取类 Skill 融合为 1 个软链接入口”）。

**动作 B: 记忆碎片下放 (Project Context Delegate)**
- **输入**：`MEMORY.md` 以及最近的 `memory/daily/` 日志。
- **逻辑**：正则扫描或语义识别其中是否混入了“大量代码排障、报错日志、特定项目部署步骤”等不属于抽象经验的内容。
- **输出**：主动将这些内容从主记忆区剪切，并追加或覆盖到对应代码项目的 `DEPLOY_MANUAL.md` 或 `PROJECT_MEMORY.md` 中。随后执行 `git commit` 与 `git push` 使其随代码持久化。

### 3. 反馈循环 (Feedback Loop)
- **发现并处理了问题**：向绑定的 IM 渠道（如 QQBot/Telegram）推送极简总结。
- **未发现问题 / 状态良好**：返回标准心跳应答（如 `HEARTBEAT_OK`），保持绝对静默，不占用任何多余的交互注意力。
