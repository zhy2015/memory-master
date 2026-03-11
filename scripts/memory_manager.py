import os
import shutil
import time
from datetime import datetime, timedelta
import csv

WORKSPACE_DIR = "/root/.openclaw/workspace"
MEMORY_DIR = os.path.join(WORKSPACE_DIR, "memory")
DAILY_DIR = os.path.join(MEMORY_DIR, "daily")
ARCHIVE_DIR = os.path.join(MEMORY_DIR, "archive")
METRICS_FILE = os.path.join(MEMORY_DIR, "metrics", "skill_usage.csv")

def archive_old_daily_logs(days=7):
    print(f"🔍 正在扫描超过 {days} 天的日常记忆...")
    if not os.path.exists(DAILY_DIR):
        print("   [跳过] daily 目录不存在")
        return

    now = time.time()
    moved_count = 0
    
    for filename in os.listdir(DAILY_DIR):
        if not filename.endswith(".md"):
            continue
            
        filepath = os.path.join(DAILY_DIR, filename)
        file_mtime = os.path.getmtime(filepath)
        
        if (now - file_mtime) > (days * 86400):
            # 确定归档月份目录
            file_date = datetime.fromtimestamp(file_mtime)
            month_folder = file_date.strftime("%Y-%m")
            target_dir = os.path.join(ARCHIVE_DIR, month_folder)
            os.makedirs(target_dir, exist_ok=True)
            
            target_path = os.path.join(target_dir, filename)
            shutil.move(filepath, target_path)
            print(f"   📦 归档: {filename} -> archive/{month_folder}/")
            moved_count += 1
            
    print(f"✅ 完成归档，共移动 {moved_count} 个文件。\n")

def check_skill_roi(days=30):
    print(f"🔍 正在审查超过 {days} 天未使用的冷门技能...")
    if not os.path.exists(METRICS_FILE):
        print("   [跳过] 找不到 skill_usage.csv")
        return

    skill_last_used = {}
    
    try:
        with open(METRICS_FILE, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                skill = row.get('Skill')
                date_str = row.get('Date')
                if skill and date_str:
                    try:
                        # 假设格式如 2026-03-11
                        date_obj = datetime.strptime(date_str.split(' ')[0], "%Y-%m-%d")
                        if skill not in skill_last_used or date_obj > skill_last_used[skill]:
                            skill_last_used[skill] = date_obj
                    except Exception:
                        pass
    except Exception as e:
        print(f"   [错误] 读取 metrics 失败: {e}")
        return

    now = datetime.now()
    cold_skills = []
    
    for skill, last_date in skill_last_used.items():
        if (now - last_date).days > days:
            cold_skills.append((skill, (now - last_date).days))
            
    if cold_skills:
        print("   ⚠️ 发现以下高闲置技能（建议评估是否剔除）：")
        for skill, idle_days in cold_skills:
            print(f"      - {skill} (已闲置 {idle_days} 天)")
    else:
        print("   ✨ 所有已记录技能均在活跃期。")

if __name__ == "__main__":
    print("🧠 Memory Architect 自动化工具 🧠")
    print("="*40)
    archive_old_daily_logs(days=7)
    check_skill_roi(days=30)
    print("="*40)
    print("💡 提示：记忆蒸馏(提取金线至 MEMORY.md)建议由大模型通过阅读近期 daily 日志后直接操作，本脚本不盲目篡改核心记忆。")
