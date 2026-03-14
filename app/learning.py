from __future__ import annotations

from collections import Counter
from typing import Iterable, List

from app.models import ActionType, Agent, StrategyWeights

LEARNING_RATE = 0.04


def _normalize(weights: dict[ActionType, float]) -> StrategyWeights:
    total = sum(max(value, 0.01) for value in weights.values())
    return StrategyWeights(
        attack=max(weights["attack"], 0.01) / total,
        defend=max(weights["defend"], 0.01) / total,
        special=max(weights["special"], 0.01) / total,
    )


def update_strategy(agent: Agent, actions_used: Iterable[ActionType], did_win: bool) -> StrategyWeights:
    weights = agent.strategy_weights.as_dict()
    usage = Counter(actions_used)

    for action, count in usage.items():
        adjustment = LEARNING_RATE * count
        if did_win:
            weights[action] += adjustment
        else:
            weights[action] -= adjustment * 0.5
            other_actions = [key for key in weights.keys() if key != action]
            for other_action in other_actions:
                weights[other_action] += adjustment * 0.25

    updated = _normalize(weights)
    agent.strategy_weights = updated
    outcome = "win" if did_win else "loss"
    agent.learning_memory.append(
        f"After a {outcome}, adjusted strategy toward {dict(usage)} and normalized weights."
    )
    agent.learning_memory = agent.learning_memory[-10:]
    return updated
