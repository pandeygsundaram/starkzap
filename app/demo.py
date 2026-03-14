from __future__ import annotations

import json

from app.agents import create_agent
from app.battle import BattleEngine
from app.models import CreateAgentRequest


def run_demo() -> None:
    agent_a = create_agent(CreateAgentRequest(owner_wallet="0xUSER_A"), existing_count=0)
    agent_b = create_agent(CreateAgentRequest(owner_wallet="0xUSER_B"), existing_count=1)
    replay = BattleEngine(seed=42).simulate(agent_a, agent_b)
    print(json.dumps(replay.model_dump(), indent=2))


if __name__ == "__main__":
    run_demo()
