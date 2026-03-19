# 使用示例

```python
from memory_master import MemoryMaster

# 初始化
mm = MemoryMaster("./my_workspace")

# 写入记忆
mm.write_daily("今天学会了使用新的 API", metadata={"tags": ["learning", "api"]})

# 整合记忆（提取关键信息）
result = mm.consolidate()
print(f"整合了 {result['insights_extracted']} 条洞察")

# 搜索记忆
results = mm.search("API 学习", limit=3)
for r in results["results"]:
    print(f"[{r['similarity']:.2f}] {r['content']}")

# 查看状态
print(mm.status())
```

## 标记格式

在写入记忆时，使用特定标记可以自动提取到核心记忆：

- `FAILED: xxx` - 失败模式
- `SUCCESS(xxx)` - 成功经验
- `DECISION: xxx` - 决策记录
- `LEARNED: xxx` - 学习记录

示例：
```python
mm.write_daily("""
今天部署遇到了问题。
FAILED: 忘记设置环境变量导致连接失败
LEARNED: 部署前必须检查 .env 文件
SUCCESS(修复了部署脚本)
""")
```
