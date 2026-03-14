from __future__ import annotations

import random
import uuid
from copy import deepcopy
from dataclasses import dataclass, field
from typing import Dict, List

from app.learning import update_strategy
from app.models import (
    ActionType,
    Agent,
    BattleHistoryEntry,
    BattleMoveRecord,
    BattleReplay,
    BattleTurn,
)


@dataclass
class Combatant:
    agent: Agent
    hp: int = 100
    defending: bool = False
    special_cooldown: int = 0
    actions_used: List[ActionType] = field(default_factory=list)
    move_records: List[BattleMoveRecord] = field(default_factory=list)


class BattleEngine:
    def __init__(self, seed: int | None = None) -> None:
        self.rng = random.Random(seed)

    def choose_action(self, combatant: Combatant, opponent: Combatant) -> ActionType:
        weights = combatant.agent.strategy_weights.as_dict().copy()

        if combatant.hp < 30:
            weights["defend"] += 0.2
        if opponent.hp < 25:
            weights["special"] += 0.15
        if combatant.special_cooldown > 0:
            weights["special"] = 0.0

        actions = list(weights.keys())
        total = sum(weights.values())
        normalized = [value / total for value in weights.values()]
        return self.rng.choices(actions, weights=normalized, k=1)[0]  # type: ignore[return-value]

    def _roll_damage(self, action: ActionType) -> int:
        if action == "attack":
            return self.rng.randint(10, 15)
        if action == "special":
            return self.rng.randint(20, 25)
        return self.rng.randint(2, 4)

    def _resolve_action(self, actor: Combatant, target: Combatant, action: ActionType, turn_number: int) -> BattleTurn:
        actor.defending = action == "defend"
        if action == "defend":
            damage = 0
            commentary = f"{actor.agent.agent_id} braces for impact."
        else:
            damage = self._roll_damage(action)
            if target.defending:
                damage = max(1, damage // 2)
            target.hp = max(0, target.hp - damage)
            commentary = f"{actor.agent.agent_id} uses {action} for {damage} damage."

        if actor.special_cooldown > 0:
            actor.special_cooldown -= 1
        if action == "special":
            actor.special_cooldown = 2

        actor.actions_used.append(action)
        actor.move_records.append(
            BattleMoveRecord(
                turn=turn_number,
                action=action,
                damage_dealt=damage,
                damage_taken=0,
            )
        )

        if target.move_records:
            target.move_records[-1].damage_taken += damage

        return BattleTurn(
            turn=turn_number,
            actor=actor.agent.agent_id,
            target=target.agent.agent_id,
            action=action,
            damage=damage,
            hp_after_actor=actor.hp,
            hp_after_target=target.hp,
            animation={
                "lunge_at": 0.0,
                "impact_at": 0.3,
                "damage_popup_at": 0.5,
                "hp_update_at": 0.7,
                "reset_at": 1.2,
                "next_turn_at": 2.0,
            },
            commentary=commentary,
        )

    def simulate(self, agent_a: Agent, agent_b: Agent) -> BattleReplay:
        battle_id = f"battle_{uuid.uuid4().hex[:10]}"
        combatants = {
            agent_a.agent_id: Combatant(agent=agent_a),
            agent_b.agent_id: Combatant(agent=agent_b),
        }
        actor_order = [combatants[agent_a.agent_id], combatants[agent_b.agent_id]]
        strategy_before = {
            agent_a.agent_id: deepcopy(agent_a.strategy_weights),
            agent_b.agent_id: deepcopy(agent_b.strategy_weights),
        }
        turns: List[BattleTurn] = []
        turn_number = 1

        while all(combatant.hp > 0 for combatant in actor_order) and turn_number <= 40:
            for actor, target in ((actor_order[0], actor_order[1]), (actor_order[1], actor_order[0])):
                if actor.hp <= 0 or target.hp <= 0:
                    break
                action = self.choose_action(actor, target)
                turns.append(self._resolve_action(actor, target, action, turn_number))
                turn_number += 1
                if target.hp <= 0:
                    break
            for combatant in actor_order:
                if combatant.defending:
                    combatant.defending = False

        winner = None
        if actor_order[0].hp != actor_order[1].hp:
            winner = max(actor_order, key=lambda combatant: combatant.hp).agent.agent_id

        for combatant in actor_order:
            did_win = combatant.agent.agent_id == winner
            update_strategy(combatant.agent, combatant.actions_used, did_win)
            combatant.agent.experience += 25 if did_win else 10
            combatant.agent.wins += 1 if did_win else 0
            combatant.agent.losses += 0 if did_win else 1
            opponent = actor_order[1] if combatant is actor_order[0] else actor_order[0]
            combatant.agent.battle_history.append(
                BattleHistoryEntry(
                    battle_id=battle_id,
                    opponent_id=opponent.agent.agent_id,
                    result="win" if did_win else "loss",
                    turns_survived=len(turns),
                    moves_used=combatant.move_records,
                )
            )
            combatant.agent.battle_history = combatant.agent.battle_history[-10:]

        return BattleReplay(
            battle_id=battle_id,
            agent_a=agent_a.agent_id,
            agent_b=agent_b.agent_id,
            initial_hp={agent_a.agent_id: 100, agent_b.agent_id: 100},
            turns=turns,
            winner=winner,
            strategy_before=strategy_before,
            strategy_after={
                agent_a.agent_id: agent_a.strategy_weights,
                agent_b.agent_id: agent_b.strategy_weights,
            },
        )
