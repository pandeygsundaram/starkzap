from __future__ import annotations

from typing import Dict, List, Literal, Optional

from pydantic import BaseModel, Field

ActionType = Literal["attack", "defend", "special"]


class StrategyWeights(BaseModel):
    attack: float = 0.6
    defend: float = 0.3
    special: float = 0.1

    def as_dict(self) -> Dict[ActionType, float]:
        return {
            "attack": self.attack,
            "defend": self.defend,
            "special": self.special,
        }


class AvatarFeatures(BaseModel):
    horn_type: str
    eye_type: str
    armor_style: str
    color: str
    sigil: str
    image: str


class BattleMoveRecord(BaseModel):
    turn: int
    action: ActionType
    damage_dealt: int = 0
    damage_taken: int = 0


class BattleHistoryEntry(BaseModel):
    battle_id: str
    opponent_id: str
    result: Literal["win", "loss"]
    turns_survived: int
    moves_used: List[BattleMoveRecord] = Field(default_factory=list)


class Agent(BaseModel):
    agent_id: str
    owner_wallet: str
    agent_wallet: str
    avatar_url: str
    avatar_features: AvatarFeatures
    strategy_weights: StrategyWeights = Field(default_factory=StrategyWeights)
    experience: int = 0
    wins: int = 0
    losses: int = 0
    battle_history: List[BattleHistoryEntry] = Field(default_factory=list)
    learning_memory: List[str] = Field(default_factory=list)


class BattleActorState(BaseModel):
    agent_id: str
    hp: int
    action: ActionType
    damage_dealt: int
    damage_taken: int
    defending: bool = False
    special_on_cooldown: bool = False


class BattleTurn(BaseModel):
    turn: int
    actor: str
    target: str
    action: ActionType
    damage: int
    hp_after_actor: int
    hp_after_target: int
    animation: Dict[str, float]
    commentary: str


class BattleReplay(BaseModel):
    battle_id: str
    agent_a: str
    agent_b: str
    initial_hp: Dict[str, int]
    turns: List[BattleTurn]
    winner: Optional[str]
    strategy_before: Dict[str, StrategyWeights]
    strategy_after: Dict[str, StrategyWeights]


class CreateAgentRequest(BaseModel):
    owner_wallet: str


class BattleStartRequest(BaseModel):
    agentA: str
    agentB: str
