from __future__ import annotations

from typing import Dict, List, Optional

from app.models import Agent, BattleReplay


class InMemoryStore:
    def __init__(self) -> None:
        self.agents: Dict[str, Agent] = {}
        self.battles: Dict[str, BattleReplay] = {}

    def save_agent(self, agent: Agent) -> Agent:
        self.agents[agent.agent_id] = agent
        return agent

    def get_agent(self, agent_id: str) -> Optional[Agent]:
        return self.agents.get(agent_id)

    def list_agents(self) -> List[Agent]:
        return list(self.agents.values())

    def save_battle(self, battle: BattleReplay) -> BattleReplay:
        self.battles[battle.battle_id] = battle
        return battle

    def get_battle(self, battle_id: str) -> Optional[BattleReplay]:
        return self.battles.get(battle_id)


store = InMemoryStore()
