"""Bridge between the Mesa backend and the plain-English Streamlit dashboard.

The dashboard should not need to know Mesa internals. This module translates a
Mesa run into small, readable data objects that the UI can render directly.
"""

from __future__ import annotations

from dataclasses import dataclass

from abm_explanations import build_end_of_run_explanation
from mesa_learning import MesaLearningState
from mesa_model import CyberBystanderMesaModel


ROLE_ORDER = ["instigator", "defender", "neutral", "other"]


@dataclass(slots=True)
class AgentProfile:
    agent_id: str
    role: str
    x: float
    y: float


@dataclass(slots=True)
class RoleComposition:
    instigator: int
    defender: int
    neutral: int
    other: int

    @property
    def total(self) -> int:
        return self.instigator + self.defender + self.neutral + self.other

    def as_dict(self) -> dict[str, int]:
        return {
            "instigator": self.instigator,
            "defender": self.defender,
            "neutral": self.neutral,
            "other": self.other,
        }


@dataclass(slots=True)
class SimulationConfig:
    total_bystanders: int
    instigator_pct: float
    defender_pct: float
    neutral_pct: float
    other_pct: float
    initial_aggression: float
    toxicity_level: float
    profanity_level: float
    identity_attack_level: float
    like_influence: float
    retweet_influence: float
    simulation_speed: float
    random_seed: int
    tom_influence_strength: float
    learning_rate: float
    reward_strength: float
    memory_retention_strength: float
    adaptation_speed: float
    carry_learning: bool
    max_steps: int = 18
    escalation_threshold: float = 80.0
    calming_threshold: float = 20.0


@dataclass(slots=True)
class SimulationSnapshot:
    step: int
    bullying_level: float
    active_agent_ids: list[str]
    action_counts: dict[str, int]
    bullying_change: float
    story_line: str


@dataclass(slots=True)
class SimulationPreview:
    composition: RoleComposition
    agents: list[AgentProfile]
    bullying_history: list[float]


@dataclass(slots=True)
class SimulationResult:
    composition: RoleComposition
    agents: list[AgentProfile]
    bullying_history: list[float]
    snapshots: list[SimulationSnapshot]
    final_outcome: str
    explanation: str
    simple_takeaway: str
    updated_learning_state: MesaLearningState


def _create_model(
    config: SimulationConfig,
    persistent_learning_state: MesaLearningState | None,
) -> CyberBystanderMesaModel:
    return CyberBystanderMesaModel(
        total_bystanders=config.total_bystanders,
        instigator_pct=config.instigator_pct,
        defender_pct=config.defender_pct,
        neutral_pct=config.neutral_pct,
        other_pct=config.other_pct,
        initial_aggression=config.initial_aggression,
        toxicity_level=config.toxicity_level,
        profanity_level=config.profanity_level,
        identity_attack_level=config.identity_attack_level,
        like_influence=config.like_influence,
        retweet_influence=config.retweet_influence,
        random_seed=config.random_seed,
        tom_influence_strength=config.tom_influence_strength,
        learning_rate=config.learning_rate,
        reward_strength=config.reward_strength,
        memory_retention_strength=config.memory_retention_strength,
        adaptation_speed=config.adaptation_speed,
        carry_learning=config.carry_learning,
        persistent_learning_state=persistent_learning_state,
        max_steps=config.max_steps,
        escalation_threshold=config.escalation_threshold,
        calming_threshold=config.calming_threshold,
    )


def build_preview_state(config: SimulationConfig) -> SimulationPreview:
    model = _create_model(config, persistent_learning_state=MesaLearningState())
    composition = RoleComposition(**model.role_counts)
    agents = [
        AgentProfile(
            agent_id=agent.visual_id,
            role=agent.role,
            x=agent.display_x,
            y=agent.display_y,
        )
        for agent in model.agents
    ]
    return SimulationPreview(
        composition=composition,
        agents=agents,
        bullying_history=[model.bullying_intensity],
    )


def simulate_scenario(
    config: SimulationConfig,
    persistent_learning_state: MesaLearningState,
) -> SimulationResult:
    model = _create_model(config, persistent_learning_state=persistent_learning_state)
    model.run_to_completion()

    composition = RoleComposition(**model.role_counts)
    agents = [
        AgentProfile(
            agent_id=agent.visual_id,
            role=agent.role,
            x=agent.display_x,
            y=agent.display_y,
        )
        for agent in model.agents
    ]
    snapshots = [
        SimulationSnapshot(
            step=record.step,
            bullying_level=record.bullying_level,
            active_agent_ids=record.active_agent_ids,
            action_counts=record.action_counts,
            bullying_change=record.bullying_change,
            story_line=record.story_line,
        )
        for record in model.story_records
    ]

    history_df = model.datacollector.get_model_vars_dataframe()
    bullying_history = history_df["bullying_level"].tolist()

    dominant_role = max(composition.as_dict(), key=composition.as_dict().get)
    explanation, simple_takeaway = build_end_of_run_explanation(
        final_outcome=model.final_outcome,
        dominant_role=dominant_role,
        tom_strength=config.tom_influence_strength,
        learning_rate=config.learning_rate,
        carry_learning=config.carry_learning,
        final_bullying_level=bullying_history[-1],
    )

    return SimulationResult(
        composition=composition,
        agents=agents,
        bullying_history=bullying_history,
        snapshots=snapshots,
        final_outcome=model.final_outcome,
        explanation=explanation,
        simple_takeaway=simple_takeaway,
        updated_learning_state=model.updated_learning_state,
    )
