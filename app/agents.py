from __future__ import annotations

import hashlib
import random

from app.avatar import generate_avatar
from app.learning import _normalize
from app.models import Agent, CreateAgentRequest, StrategyWeights

ADJECTIVES = ["iron", "null", "ember", "void", "storm", "hex", "lunar", "grim"]
CREATURES = ["maw", "wraith", "fang", "hydra", "drake", "tiger", "wyrm", "golem"]


def _wallet_rng(owner_wallet: str) -> random.Random:
    digest = hashlib.sha256(owner_wallet.encode("utf-8")).hexdigest()
    return random.Random(int(digest[:16], 16))


def create_agent(payload: CreateAgentRequest, existing_count: int) -> Agent:
    rng = _wallet_rng(f"{payload.owner_wallet}:{existing_count}")
    agent_id = f"{rng.choice(ADJECTIVES)}_{rng.choice(CREATURES)}_{existing_count + 1}"
    agent_wallet = "0xAGENT" + hashlib.sha256(agent_id.encode("utf-8")).hexdigest()[:12].upper()
    avatar = generate_avatar(agent_id)
    raw_weights = StrategyWeights(
        attack=round(rng.uniform(0.45, 0.7), 2),
        defend=round(rng.uniform(0.15, 0.35), 2),
        special=round(rng.uniform(0.05, 0.2), 2),
    )

    return Agent(
        agent_id=agent_id,
        owner_wallet=payload.owner_wallet,
        agent_wallet=agent_wallet,
        avatar_url=avatar.image,
        avatar_features=avatar,
        strategy_weights=_normalize(raw_weights.as_dict()),
    )
