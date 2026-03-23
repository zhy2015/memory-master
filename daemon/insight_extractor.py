"""Insight extraction helpers for Memory Master daemon."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, List


class InsightExtractor:
    def extract(self, log_file: Path) -> List[Dict]:
        content = log_file.read_text(encoding='utf-8')
        insights: List[Dict] = []
        failures = re.findall(r'FAILED.*?:\s*(.+)', content)
        for failure in failures:
            insights.append({
                'type': 'failure_pattern',
                'content': failure.strip(),
                'source': log_file.name,
                'date': self._extract_date(log_file.name),
            })

        successes = re.findall(r'SUCCESS.*?\((.+?)\)', content)
        for success in successes:
            insights.append({
                'type': 'success_pattern',
                'content': success.strip(),
                'source': log_file.name,
                'date': self._extract_date(log_file.name),
            })

        skill_usage = re.findall(r'Skills registered:\s*(\d+)', content)
        if skill_usage:
            insights.append({
                'type': 'metric',
                'content': f'Total skills: {skill_usage[0]}',
                'source': log_file.name,
                'date': self._extract_date(log_file.name),
            })
        return insights

    def _extract_date(self, filename: str) -> str:
        match = re.search(r'(\d{4}-\d{2}-\d{2})', filename)
        return match.group(1) if match else 'unknown'
