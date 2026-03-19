#!/usr/bin/env python3
"""
Memory Master - 轻量级 AI 记忆管理系统

核心功能：
1. 分层存储: daily → distilled/core → archive
2. 自动整合: 提取关键信息，去重合并
3. 语义搜索: 基于本地可重建索引
4. Skill-ready: 可被外部工作流直接调用
"""

import json
import re
import shutil
import sqlite3
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Set, Optional
import numpy as np


class MemoryMaster:
    """记忆管理核心类"""
    
    def __init__(self, workspace_root: str = "."):
        self.workspace = Path(workspace_root)
        self.memory_root = self.workspace / "memory"
        self.core_dir = self.memory_root / "core"
        self.daily_dir = self.memory_root / "daily"
        self.archive_dir = self.memory_root / "archive"
        self.distilled_dir = self.memory_root / "distilled"
        self.index_dir = self.memory_root / "index"
        
        # 核心文件
        self.core_memory = self.core_dir / "MEMORY.md"
        self.db_path = self.index_dir / "vector_index.db"
        self.processed_record = self.index_dir / "processed_logs.json"
        
        # 确保目录存在
        for d in [self.core_dir, self.daily_dir, self.archive_dir, self.distilled_dir, self.index_dir]:
            d.mkdir(parents=True, exist_ok=True)
    
    def _now(self) -> str:
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def _today_file(self) -> Path:
        """获取今天的日志文件路径"""
        today = datetime.now().strftime("%Y-%m-%d")
        return self.daily_dir / f"{today}.md"
    
    def _extract_date(self, filename: str) -> str:
        """从文件名提取日期"""
        match = re.search(r'(\d{4}-\d{2}-\d{2})', filename)
        return match.group(1) if match else "unknown"
    
    # ==================== 核心 API ====================
    
    def write_daily(self, content: str, metadata: Dict = None) -> Dict:
        """
        写入日常记忆
        
        Args:
            content: 记忆内容
            metadata: 可选元数据 {tags: [], source: ""}
        
        Returns:
            写入结果
        """
        daily_file = self._today_file()
        timestamp = self._now()
        
        # 构建条目
        entry = f"\n## {timestamp}\n\n{content}\n"
        
        if metadata:
            if metadata.get("tags"):
                entry += f"\n**Tags**: {', '.join(metadata['tags'])}\n"
            if metadata.get("source"):
                entry += f"**Source**: {metadata['source']}\n"
        
        # 追加写入
        with open(daily_file, "a", encoding="utf-8") as f:
            f.write(entry)
        
        return {
            "status": "success",
            "action": "write_daily",
            "file": str(daily_file),
            "timestamp": timestamp
        }
    
    def consolidate(self, dry_run: bool = False) -> Dict:
        """
        整合记忆：提取高价值内容，去重，写入核心记忆
        """
        result = {
            "action": "consolidate",
            "timestamp": self._now(),
            "logs_processed": 0,
            "insights_extracted": 0,
            "insights_merged": 0,
            "dry_run": dry_run
        }
        
        # 获取未处理日志
        unprocessed = self._get_unprocessed_logs()
        result["logs_processed"] = len(unprocessed)
        
        if not unprocessed:
            result["status"] = "success"
            result["message"] = "No new logs to process"
            return result
        
        # 提取洞察
        insights = self._extract_insights(unprocessed)
        result["insights_extracted"] = len(insights)
        
        # 合并到核心记忆
        if insights and not dry_run:
            merged = self._merge_to_core(insights)
            result["insights_merged"] = merged
            self._mark_processed(unprocessed)
        
        result["status"] = "success"
        result["message"] = f"Processed {len(unprocessed)} logs, extracted {len(insights)} insights"
        return result
    
    def archive(self, days: int = 7) -> Dict:
        """
        归档过期日志
        
        Args:
            days: 归档阈值天数
        """
        result = {
            "action": "archive",
            "timestamp": self._now(),
            "threshold_days": days,
            "archived_count": 0,
            "archived_files": []
        }
        
        cutoff = datetime.now() - timedelta(days=days)
        
        for f in self.daily_dir.glob("*.md"):
            date_str = self._extract_date(f.name)
            if date_str != "unknown":
                try:
                    file_date = datetime.strptime(date_str, "%Y-%m-%d")
                    if file_date < cutoff:
                        dest = self.archive_dir / f.name
                        shutil.move(str(f), str(dest))
                        result["archived_count"] += 1
                        result["archived_files"].append(f.name)
                except ValueError:
                    pass
        
        result["status"] = "success"
        result["message"] = f"Archived {result['archived_count']} old logs"
        return result
    
    def search(self, query: str, limit: int = 5) -> Dict:
        """
        语义搜索记忆
        
        Args:
            query: 搜索关键词
            limit: 返回结果数量
        """
        result = {
            "action": "search",
            "timestamp": self._now(),
            "query": query,
            "limit": limit,
            "results": []
        }
        
        # 确保索引存在
        if not self.db_path.exists():
            self.build_index()
        
        # 执行搜索
        results = self._semantic_search(query, limit)
        result["results"] = results
        result["status"] = "success"
        result["message"] = f"Found {len(results)} results"
        return result
    
    def build_index(self) -> Dict:
        """构建向量索引"""
        result = {
            "action": "index",
            "timestamp": self._now(),
            "indexed_chunks": 0
        }
        
        conn = self._init_db()
        dirs_to_index = [self.daily_dir, self.archive_dir, self.distilled_dir]
        
        for d in dirs_to_index:
            if not d.exists():
                continue
            for f in d.glob("*.md"):
                added = self._index_file(f, conn)
                result["indexed_chunks"] += added
        
        conn.close()
        
        result["status"] = "success"
        result["message"] = f"Indexed {result['indexed_chunks']} chunks"
        return result
    
    def status(self) -> Dict:
        """获取记忆系统状态"""
        status = {
            "action": "status",
            "timestamp": self._now(),
            "directories": {},
            "files": {},
            "index": {}
        }
        
        # 目录统计
        for name, d in [
            ("daily", self.daily_dir),
            ("archive", self.archive_dir),
            ("distilled", self.distilled_dir),
            ("core", self.core_dir)
        ]:
            if d.exists():
                files = list(d.glob("*.md"))
                status["directories"][name] = len(files)
        
        # 核心记忆文件
        if self.core_memory.exists():
            content = self.core_memory.read_text()
            status["files"]["core_memory_size"] = len(content)
            status["files"]["core_memory_lines"] = len(content.splitlines())
        
        # 索引状态
        if self.db_path.exists():
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute("SELECT COUNT(*) FROM memory_chunks")
            count = c.fetchone()[0]
            conn.close()
            status["index"]["total_chunks"] = count
        
        status["status"] = "success"
        status["message"] = "Memory system status retrieved"
        return status
    
    # ==================== 内部方法 ====================
    
    def _get_unprocessed_logs(self) -> List[Path]:
        """获取未处理的日志文件"""
        if not self.daily_dir.exists():
            return []
        
        processed = self._load_processed_record()
        logs = [f for f in self.daily_dir.glob("*.md") if f.name not in processed]
        return sorted(logs)
    
    def _load_processed_record(self) -> Set[str]:
        """加载已处理记录"""
        if self.processed_record.exists():
            with open(self.processed_record) as f:
                return set(json.load(f))
        return set()
    
    def _extract_insights(self, log_files: List[Path]) -> List[Dict]:
        """从日志中提取高价值经验"""
        insights = []
        
        for log_file in log_files:
            content = log_file.read_text()
            
            # 提取失败模式
            failures = re.findall(r'FAILED.*?[:：]\s*(.+)', content, re.IGNORECASE)
            for f in failures:
                insights.append({
                    "type": "failure_pattern",
                    "content": f.strip(),
                    "source": log_file.name,
                    "date": self._extract_date(log_file.name)
                })
            
            # 提取成功经验
            successes = re.findall(r'SUCCESS.*?[\(\（](.+?)[\)\）]', content, re.IGNORECASE)
            for s in successes:
                insights.append({
                    "type": "success_pattern",
                    "content": s.strip(),
                    "source": log_file.name,
                    "date": self._extract_date(log_file.name)
                })
            
            # 提取决策记录
            decisions = re.findall(r'DECISION.*?[:：]\s*(.+)', content, re.IGNORECASE)
            for d in decisions:
                insights.append({
                    "type": "decision",
                    "content": d.strip(),
                    "source": log_file.name,
                    "date": self._extract_date(log_file.name)
                })
            
            # 提取学习记录
            learnings = re.findall(r'LEARNED.*?[:：]\s*(.+)', content, re.IGNORECASE)
            for l in learnings:
                insights.append({
                    "type": "learning",
                    "content": l.strip(),
                    "source": log_file.name,
                    "date": self._extract_date(log_file.name)
                })
        
        return insights
    
    def _merge_to_core(self, insights: List[Dict]) -> int:
        """合并到核心记忆，返回实际合并数量"""
        existing = ""
        if self.core_memory.exists():
            existing = self.core_memory.read_text()
        
        # 去重
        new_insights = [ins for ins in insights if ins["content"] not in existing]
        
        if not new_insights:
            return 0
        
        # 追加到核心记忆
        with open(self.core_memory, "a", encoding="utf-8") as f:
            f.write(f"\n\n## Auto-Extracted Insights - {self._now()}\n\n")
            for ins in new_insights:
                f.write(f"- **{ins['type']}** ({ins['date']}): {ins['content']}\n")
        
        return len(new_insights)
    
    def _mark_processed(self, log_files: List[Path]):
        """标记日志为已处理"""
        processed = self._load_processed_record()
        for f in log_files:
            processed.add(f.name)
        
        with open(self.processed_record, "w") as f:
            json.dump(list(processed), f, indent=2)
    
    def _init_db(self) -> sqlite3.Connection:
        """初始化向量数据库"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS memory_chunks (
                id TEXT PRIMARY KEY,
                source_file TEXT,
                content TEXT,
                timestamp DATETIME,
                embedding BLOB
            )
        ''')
        conn.commit()
        return conn
    
    def _get_embedding(self, text: str) -> np.ndarray:
        """获取文本嵌入（使用确定性哈希模拟）"""
        np.random.seed(int(hashlib.md5(text.encode()).hexdigest()[:8], 16))
        return np.random.rand(384).astype(np.float32)
    
    def _index_file(self, filepath: Path, conn: sqlite3.Connection) -> int:
        """索引单个文件"""
        content = filepath.read_text()
        chunks = [c.strip() for c in content.split('\n## ') if c.strip()]
        
        c = conn.cursor()
        added = 0
        
        for chunk in chunks:
            if not chunk:
                continue
            chunk_id = hashlib.md5(chunk.encode()).hexdigest()
            
            # 检查是否已存在
            c.execute("SELECT id FROM memory_chunks WHERE id=?", (chunk_id,))
            if c.fetchone():
                continue
            
            emb = self._get_embedding(chunk)
            c.execute(
                "INSERT INTO memory_chunks (id, source_file, content, timestamp, embedding) VALUES (?, ?, ?, ?, ?)",
                (chunk_id, filepath.name, chunk[:1000], datetime.now(), emb.tobytes())
            )
            added += 1
        
        conn.commit()
        return added
    
    def _semantic_search(self, query: str, limit: int) -> List[Dict]:
        """执行语义搜索"""
        query_emb = self._get_embedding(query)
        
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT source_file, content, embedding FROM memory_chunks")
        
        results = []
        for row in c.fetchall():
            source, content, emb_bytes = row
            emb = np.frombuffer(emb_bytes, dtype=np.float32)
            similarity = np.dot(query_emb, emb) / (np.linalg.norm(query_emb) * np.linalg.norm(emb))
            results.append({
                "source": source,
                "content": content[:200] + "..." if len(content) > 200 else content,
                "similarity": float(similarity)
            })
        
        conn.close()
        
        # 排序并返回前N个
        results.sort(key=lambda x: x["similarity"], reverse=True)
        return results[:limit]


# ==================== CLI 入口 ====================

if __name__ == "__main__":
    import sys
    
    mm = MemoryMaster()
    
    if len(sys.argv) < 2:
        print("Usage: python memory_master.py <action> [args...]")
        print("Actions:")
        print("  write <content>     - 写入日常记忆")
        print("  consolidate         - 整合记忆")
        print("  archive [days]      - 归档旧日志")
        print("  search <query> [limit] - 搜索记忆")
        print("  index               - 构建索引")
        print("  status              - 查看状态")
        sys.exit(1)
    
    action = sys.argv[1]
    
    if action == "write":
        content = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else "Empty entry"
        print(json.dumps(mm.write_daily(content), indent=2, ensure_ascii=False))
    elif action == "consolidate":
        dry_run = "--dry-run" in sys.argv
        print(json.dumps(mm.consolidate(dry_run=dry_run), indent=2, ensure_ascii=False))
    elif action == "archive":
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 7
        print(json.dumps(mm.archive(days=days), indent=2, ensure_ascii=False))
    elif action == "search":
        query = sys.argv[2] if len(sys.argv) > 2 else "test"
        limit = int(sys.argv[3]) if len(sys.argv) > 3 else 5
        print(json.dumps(mm.search(query=query, limit=limit), indent=2, ensure_ascii=False))
    elif action == "index":
        print(json.dumps(mm.build_index(), indent=2, ensure_ascii=False))
    elif action == "status":
        print(json.dumps(mm.status(), indent=2, ensure_ascii=False))
    else:
        print(f"Unknown action: {action}")
