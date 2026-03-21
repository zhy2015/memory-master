#!/usr/bin/env python3
"""
Memory Master Daemon
后台守护进程：自动整理记忆，由 Heartbeat 驱动

输入: memory/daily/ 中的 WAL 日志和执行结果
处理: 提炼规律，去重，归档
输出: 写入 memory/core/MEMORY.md，过期日志移至 memory/archive/
"""

import json
import re
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Set


class MemoryMasterDaemon:
    """
    记忆大师守护进程
    
    职责:
    1. 扫描 daily/ 目录，读取未处理的日志
    2. 提取高价值经验（规律、踩坑、配置）
    3. 去重：与 core/MEMORY.md 对比，避免重复
    4. 归档：将过期日志移至 archive/
    """
    
    def __init__(self, workspace_root: str | Path = "/root/.openclaw/workspace"):
        workspace_root = Path(workspace_root)
        self.memory_root = workspace_root / "memory"
        self.core_dir = self.memory_root / "core"
        self.daily_dir = self.memory_root / "daily"
        self.archive_dir = self.memory_root / "archive"
        self.index_dir = self.memory_root / "index"
        
        # Ensure directories exist
        for d in [self.core_dir, self.daily_dir, self.archive_dir, self.index_dir]:
            d.mkdir(parents=True, exist_ok=True)
        
        self.core_memory = self.core_dir / "MEMORY.md"
        self.index_file = self.index_dir / "memory_index.json"
    
    def run_daily_maintenance(self):
        """每日维护任务"""
        print(f"[{self._now()}] 🧠 Memory Master: Starting daily maintenance...")
        
        # 1. 读取未处理的 daily logs
        unprocessed = self._get_unprocessed_logs()
        print(f"  Found {len(unprocessed)} unprocessed log(s)")
        
        if not unprocessed:
            print("  Nothing to process")
            return
        
        # 2. 提取高价值内容
        insights = self._extract_insights(unprocessed)
        print(f"  Extracted {len(insights)} insight(s)")
        
        # 3. 去重并合并到核心记忆
        if insights:
            self._merge_to_core(insights)
            print(f"  Merged to core memory")
        
        # 4. 标记已处理
        self._mark_processed(unprocessed)
        
        # 5. 归档过期日志（>7天）
        archived = self._archive_old_logs()
        print(f"  Archived {archived} old log(s)")
        
        # 6. 更新索引
        self._update_index()
        
        print(f"[{self._now()}] ✅ Memory Master: Daily maintenance completed")
    
    def _now(self):
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def _get_unprocessed_logs(self) -> List[Path]:
        """获取未处理的日志文件"""
        if not self.daily_dir.exists():
            return []
        
        # 读取处理记录
        processed = self._load_processed_record()
        
        # 获取所有日志文件
        logs = []
        for f in self.daily_dir.glob("*.md"):
            if f.name not in processed:
                logs.append(f)
        
        return sorted(logs)
    
    def _load_processed_record(self) -> Set[str]:
        """加载已处理记录"""
        record_file = self.index_dir / "processed_logs.json"
        if record_file.exists():
            with open(record_file) as f:
                return set(json.load(f))
        return set()
    
    def _extract_insights(self, log_files: List[Path]) -> List[Dict]:
        """从日志中提取高价值经验"""
        insights = []
        
        for log_file in log_files:
            with open(log_file) as f:
                content = f.read()
            
            # 提取关键模式
            # 1. 失败模式
            failures = re.findall(r'FAILED.*?:\s*(.+)', content)
            for f in failures:
                insights.append({
                    "type": "failure_pattern",
                    "content": f.strip(),
                    "source": log_file.name,
                    "date": self._extract_date(log_file.name)
                })
            
            # 2. 成功经验
            successes = re.findall(r'SUCCESS.*?\((.+?)\)', content)
            for s in successes:
                insights.append({
                    "type": "success_pattern",
                    "content": s.strip(),
                    "source": log_file.name,
                    "date": self._extract_date(log_file.name)
                })
            
            # 3. 技能使用统计
            skill_usage = re.findall(r'Skills registered:\s*(\d+)', content)
            if skill_usage:
                insights.append({
                    "type": "metric",
                    "content": f"Total skills: {skill_usage[0]}",
                    "source": log_file.name,
                    "date": self._extract_date(log_file.name)
                })
        
        return insights
    
    def _extract_date(self, filename: str) -> str:
        """从文件名提取日期"""
        match = re.search(r'(\d{4}-\d{2}-\d{2})', filename)
        return match.group(1) if match else "unknown"
    
    def _merge_to_core(self, insights: List[Dict]):
        """合并到核心记忆"""
        # 读取现有核心记忆
        existing = ""
        if self.core_memory.exists():
            with open(self.core_memory) as f:
                existing = f.read()
        
        # 去重：检查是否已存在
        new_insights = []
        for ins in insights:
            if ins["content"] not in existing:
                new_insights.append(ins)
        
        if not new_insights:
            return
        
        # 追加到核心记忆
        with open(self.core_memory, "a") as f:
            f.write(f"\n\n## Auto-Extracted Insights - {self._now()}\n\n")
            for ins in new_insights:
                f.write(f"- **{ins['type']}** ({ins['date']}): {ins['content']}\n")
    
    def _mark_processed(self, log_files: List[Path]):
        """标记日志为已处理"""
        record_file = self.index_dir / "processed_logs.json"
        processed = self._load_processed_record()
        
        for f in log_files:
            processed.add(f.name)
        
        with open(record_file, "w") as f:
            json.dump(list(processed), f, indent=2)
    
    def _archive_old_logs(self) -> int:
        """归档过期日志（>7天）"""
        if not self.daily_dir.exists():
            return 0
        
        cutoff = datetime.now() - timedelta(days=7)
        archived = 0
        
        for f in self.daily_dir.glob("*.md"):
            # 提取日期
            date_str = self._extract_date(f.name)
            if date_str != "unknown":
                try:
                    file_date = datetime.strptime(date_str, "%Y-%m-%d")
                    if file_date < cutoff:
                        # 归档
                        shutil.move(str(f), str(self.archive_dir / f.name))
                        archived += 1
                except ValueError:
                    pass
        
        return archived
    
    def _update_index(self):
        """更新记忆索引"""
        index = {
            "last_updated": self._now(),
            "core_memory": str(self.core_memory),
            "total_daily_logs": len(list(self.daily_dir.glob("*.md"))),
            "total_archived": len(list(self.archive_dir.glob("*.md"))),
            "insights_count": self._count_insights()
        }
        
        with open(self.index_file, "w") as f:
            json.dump(index, f, indent=2)
    
    def _count_insights(self) -> int:
        """统计核心记忆中的经验条目数"""
        if not self.core_memory.exists():
            return 0
        
        with open(self.core_memory) as f:
            content = f.read()
        
        # 简单统计 "- **" 开头的行
        return len(re.findall(r'^- \*\*', content, re.MULTILINE))


def main():
    """CLI entry"""
    daemon = MemoryMasterDaemon()
    daemon.run_daily_maintenance()


if __name__ == "__main__":
    main()
