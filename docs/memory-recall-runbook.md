# Memory Recall Runbook

## 目标
在不改动聊天模型链路的前提下，保持 OpenClaw 的 recall/memory 独立可用。

## 当前稳定方案
- 聊天模型 provider：`models.providers.openai`
- 聊天模型 baseUrl：`https://ai.td.ee/v1`
- memory backend：`qmd`
- memory search provider：`local`
- local embeddings model：`hf:ggml-org/embeddinggemma-300m-qat-q8_0-GGUF/embeddinggemma-300m-qat-Q8_0.gguf`
- workspace：`/root/.openclaw/workspace`

## 解耦原则
1. 不把 recall 绑定到聊天 provider。
2. 不让 memory backend 回退到 `builtin + openai embeddings`。
3. recall 出问题时，先修 `memory` 和 `agents.defaults.memorySearch`，不要先动 `models.providers.openai`。

## 配置基线
`/root/.openclaw/openclaw.json`

关键字段：
```json
{
  "models": {
    "providers": {
      "openai": {
        "baseUrl": "https://ai.td.ee/v1"
      }
    }
  },
  "agents": {
    "defaults": {
      "workspace": "/root/.openclaw/workspace",
      "memorySearch": {
        "enabled": true,
        "provider": "local",
        "fallback": "none",
        "local": {
          "modelPath": "hf:ggml-org/embeddinggemma-300m-qat-q8_0-GGUF/embeddinggemma-300m-qat-Q8_0.gguf"
        }
      }
    }
  },
  "memory": {
    "backend": "qmd"
  }
}
```

## 验收命令
```bash
openclaw memory status --deep --json
python3 /root/.openclaw/workspace/scripts/check_memory_config.py
```

## 通过标准
- `workspaceDir == /root/.openclaw/workspace`
- `backend == qmd`
- `provider == qmd`
- `embeddingProbe.ok == true`
- `scan.totalFiles > 0`
- 聊天 provider baseUrl 仍为 `https://ai.td.ee/v1`

## fallback 策略
### 一级：只修 recall，不碰 chat
优先检查并恢复：
- `agents.defaults.workspace`
- `agents.defaults.memorySearch.provider=local`
- `agents.defaults.memorySearch.fallback=none`
- `memory.backend=qmd`

### 二级：本地 embeddings 模型异常
如果 `embeddingProbe.ok=false`：
1. 保持 chat provider 不动
2. 先检查本地模型路径是否仍是当前 GGUF
3. 再检查 qmd 是否可执行
4. 然后重新跑 `openclaw memory status --deep --json`

### 三级：qmd 链路异常
如果 qmd 本身不可用：
1. 记录异常
2. 保持聊天模型链路不改
3. 再单独评估备用 recall provider
4. 未确认前，不允许把 memory 直接切回依赖 openai embeddings 的 builtin

## 快速诊断
```bash
python3 /root/.openclaw/workspace/scripts/check_memory_config.py
openclaw memory status --deep --json
openclaw status
```

## 启动期建议
- 新会话先跑 workspace sanity check，再读启动文件。
- 如果运行时声称 workspace 是 `/`，但 `/root/.openclaw/workspace/AGENTS.md` 存在，直接以 `/root/.openclaw/workspace` 为准。
- 发现漂移时，先跑 `python3 /root/.openclaw/workspace/scripts/check_memory_config.py`，不要等 recall 挂掉再排查。
