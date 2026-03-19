"""Simple action registry for memory-master workflows."""

from __future__ import annotations

from typing import Any, Callable, Dict

ActionHandler = Callable[..., Dict[str, Any]]


class ActionRegistry:
    def __init__(self):
        self._actions: Dict[str, ActionHandler] = {}

    def register(self, name: str, handler: ActionHandler) -> None:
        self._actions[name] = handler

    def register_many(self, actions: Dict[str, ActionHandler]) -> None:
        self._actions.update(actions)

    def get(self, name: str) -> ActionHandler:
        if name not in self._actions:
            raise KeyError(f"Unknown action: {name}")
        return self._actions[name]

    def as_dict(self) -> Dict[str, ActionHandler]:
        return dict(self._actions)

    def names(self):
        return sorted(self._actions.keys())
