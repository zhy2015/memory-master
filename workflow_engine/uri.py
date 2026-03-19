"""Skill URI helpers for memory-master workflow actions."""

from __future__ import annotations

from typing import Dict, Callable, Any


class SkillURIRegistry:
    def __init__(self, actions: Dict[str, Callable[..., Dict[str, Any]]], *, skill_name: str = "memory-master"):
        self.skill_name = skill_name
        self.actions = actions

    def resolve(self, action_or_uri: str):
        if action_or_uri.startswith("skill://"):
            prefix = f"skill://{self.skill_name}/"
            if not action_or_uri.startswith(prefix):
                raise KeyError(f"Unsupported skill URI: {action_or_uri}")
            action = action_or_uri[len(prefix):]
        elif action_or_uri.startswith("memory://"):
            action = action_or_uri[len("memory://"):]
        else:
            action = action_or_uri
        if action not in self.actions:
            raise KeyError(f"Unknown action: {action}")
        return self.actions[action]
