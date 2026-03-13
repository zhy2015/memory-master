# Skill 任务节点化注册与收敛工作流 (Task-Node Skill Registry Workflow)

> **设计目标**: 终结 `<available_skills>` 列表的无序膨胀，通过“按场景分类、按软链接挂载、相同归并”的机制，保持 Agent 启动上下文的极简与高效。

## 核心原则
1. **全局 Facade 化**: 主 Agent 的 `<available_skills>` 只暴露核心的“任务入口”（Task Facade），如 `repo-manager`, `social-agent`, `infra-ops`。
2. **底层脚本共享**: 具体的原子工具（如 `read_file.py`, `send_request.js`）存放在统一的公共库（`~/scripts/common/`）中。
3. **软链接挂载**: 通过创建 Symlink（软链接），将需要的原子工具挂载到对应 Task Facade 的执行目录下，供子节点使用。
4. **收敛优先**: 遇到新需求时，先找**已有的**公共原子工具组合；若必须引入新 Skill，必须经过查重与融合评估。

---

## 标准工作流 (Standard Operating Procedure)

当用户提出“帮我安装/编写一个新的 Skill”时，必须严格执行以下四步：

### Phase 1: 意图与分类 (Classification)
- 明确新 Skill 的核心动作（如：发邮件、抓网页、查数据库）。
- 确定该动作属于哪个**任务节点 (Task Node)**？
  - *例如：* 属于“个人生活助理”？属于“代码项目运维”？属于“服务器监控”？
- **动作约束**：如果是某任务的从属功能，绝不应该注册为一个全新的全局 Skill。

### Phase 2: 查重与复用 (Deduplication & Reuse)
- 使用 `find` 或 `grep` 扫描现有 `workspace/skills/` 与核心库。
- **判断**：是否已有同类工具（比如已有 `web_fetch`，就不需要再安装 `web_scraper`）？
- **融合规则**：
  - 如果重叠度 > 70%，**拒绝安装新 Skill**。
  - 直接修改原有 Skill，增加新的参数（如增加 `--format=pdf` 支持），实现功能融合。

### Phase 3: 原子化落盘与软链接 (Atomic Storage & Symlinking)
- 如果确需引入新脚本：
  1. 将源码存入统一的公共库：`mkdir -p ~/.openclaw/shared_scripts/`，并赋予执行权限 (`chmod +x`)。
  2. 根据 Phase 1 的分类，找到对应的 **Task Facade 目录**（例如 `workspace/skills/code-ops/`）。
  3. **创建软链接**：`ln -s ~/.openclaw/shared_scripts/new_tool.py workspace/skills/code-ops/new_tool.py`
  4. 只在 `code-ops` 的局部 `SKILL.md` 中增加说明，**不**将其注入全局 Agent 的 System Prompt。

### Phase 4: 上下文收敛 (Context Consolidation)
- 每月或每达到 5 个新工具时触发。
- 检查各个 Facade 下的软链接，是否有可以被组合的命令。
- 删除超 30 天未被调用的原子脚本，并移除所有对应的软链接。
