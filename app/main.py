from __future__ import annotations

from fastapi import FastAPI, HTTPException

from app.agents import create_agent
from app.battle import BattleEngine
from app.models import Agent, BattleStartRequest, CreateAgentRequest
from app.storage import store

app = FastAPI(
    title="ClawQuest AI Agent Battle System",
    description="Hackathon-ready hybrid AI battle backend with lightweight learning and replay timelines.",
    version="0.1.0",
)


@app.get("/health")
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/agent/create", response_model=Agent)
def create_agent_endpoint(payload: CreateAgentRequest) -> Agent:
    agent = create_agent(payload, existing_count=len(store.agents))
    store.save_agent(agent)
    return agent


@app.get("/agents", response_model=list[Agent])
def list_agents() -> list[Agent]:
    return store.list_agents()


@app.get("/agent/{agent_id}", response_model=Agent)
def get_agent(agent_id: str) -> Agent:
    agent = store.get_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent


@app.post("/battle/start")
def start_battle(payload: BattleStartRequest) -> dict:
    agent_a = store.get_agent(payload.agentA)
    agent_b = store.get_agent(payload.agentB)
    if not agent_a or not agent_b:
        raise HTTPException(status_code=404, detail="One or both agents not found")
    if agent_a.agent_id == agent_b.agent_id:
        raise HTTPException(status_code=400, detail="Agents must be different")

    replay = BattleEngine().simulate(agent_a, agent_b)
    store.save_battle(replay)
    store.save_agent(agent_a)
    store.save_agent(agent_b)
    return replay.model_dump()


@app.get("/battle/{battle_id}")
def get_battle(battle_id: str) -> dict:
    battle = store.get_battle(battle_id)
    if not battle:
        raise HTTPException(status_code=404, detail="Battle not found")
    return battle.model_dump()


@app.get("/battle/{battle_id}/timeline")
def get_battle_timeline(battle_id: str) -> dict:
    battle = store.get_battle(battle_id)
    if not battle:
        raise HTTPException(status_code=404, detail="Battle not found")

    return {
        "battle_id": battle.battle_id,
        "agents": [battle.agent_a, battle.agent_b],
        "initial_hp": battle.initial_hp,
        "turns": [turn.model_dump() for turn in battle.turns],
        "winner": battle.winner,
    }
