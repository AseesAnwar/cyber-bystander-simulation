"""Behavioural simulation engine for the cyberbystander dashboard.

This engine keeps the project focused on behavioural dynamics rather than
prediction. It combines:
1. Theory of Mind: agents react to what they think others may do
2. Reinforcement Learning: agents update action tendencies from outcomes
3. Continual Learning: those tendencies can be carried into later runs
"""

from __future__ import annotations

from dataclasses import dataclass
import math
import random

from abm_continual_learning import (
    ContinualLearningState,
    ROLE_ORDER,
    blend_persistent_learning,
    make_working_values,
)
from abm_explanations import build_end_of_run_explanation
from abm_rl import ACTIONS, choose_action, update_action_value
from abm_tom import infer_social_context


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
class SimulationResult:
    composition: RoleComposition
    agents: list[AgentProfile]
    bullying_history: list[float]
    snapshots: list[SimulationSnapshot]
    final_outcome: str
    explanation: str
    simple_takeaway: str
    updated_learning_state: ContinualLearningState


BASE_ROLE_PREFERENCES = {
    "instigator": {
        "support_bully": 0.62,
        "support_victim": 0.08,
        "stay_silent": 0.22,
        "step_aside": 0.08,
    },
    "defender": {
        "support_bully": 0.08,
        "support_victim": 0.62,
        "stay_silent": 0.22,
        "step_aside": 0.08,
    },
    "neutral": {
        "support_bully": 0.12,
        "support_victim": 0.15,
        "stay_silent": 0.60,
        "step_aside": 0.13,
    },
    "other": {
        "support_bully": 0.08,
        "support_victim": 0.10,
        "stay_silent": 0.20,
        "step_aside": 0.62,
    },
}


def composition_from_percentages(config: SimulationConfig) -> RoleComposition:
    raw = {
        "instigator": max(config.instigator_pct, 0.0),
        "defender": max(config.defender_pct, 0.0),
        "neutral": max(config.neutral_pct, 0.0),
        "other": max(config.other_pct, 0.0),
    }
    total_pct = sum(raw.values())
    if total_pct <= 0:
        raw = {role: 25.0 for role in ROLE_ORDER}
        total_pct = 100.0

    normalized = {role: raw[role] / total_pct for role in ROLE_ORDER}
    raw_counts = {role: normalized[role] * config.total_bystanders for role in ROLE_ORDER}
    counts = {role: int(raw_counts[role]) for role in ROLE_ORDER}
    remainder = config.total_bystanders - sum(counts.values())

    for role in sorted(ROLE_ORDER, key=lambda item: raw_counts[item] - counts[item], reverse=True):
        if remainder <= 0:
            break
        counts[role] += 1
        remainder -= 1

    return RoleComposition(
        instigator=counts["instigator"],
        defender=counts["defender"],
        neutral=counts["neutral"],
        other=counts["other"],
    )


def build_agents(composition: RoleComposition) -> list[AgentProfile]:
    agents: list[AgentProfile] = []
    role_stream: list[str] = []
    for role in ROLE_ORDER:
        role_stream.extend([role] * composition.as_dict()[role])

    for index, role in enumerate(role_stream):
        angle = (2 * math.pi * index) / max(1, len(role_stream))
        radius = 1.9 + 0.18 * (index % 3)
        agents.append(
            AgentProfile(
                agent_id=f"{role}_{index}",
                role=role,
                x=radius * math.cos(angle),
                y=radius * math.sin(angle),
            )
        )
    return agents


def simulate_scenario(
    config: SimulationConfig,
    persistent_learning_state: ContinualLearningState,
) -> SimulationResult:
    rng = random.Random(config.random_seed)
    composition = composition_from_percentages(config)
    agents = build_agents(composition)
    bullying_level = max(0.0, min(100.0, config.initial_aggression))
    bullying_history = [bullying_level]
    snapshots: list[SimulationSnapshot] = []
    working_values = make_working_values(persistent_learning_state, config.carry_learning)

    previous_action_counts = {action: 0 for action in ACTIONS}
    total_action_counts = {action: 0 for action in ACTIONS}

    for step in range(1, config.max_steps + 1):
        snapshot = simulate_step(
            config=config,
            agents=agents,
            bullying_level=bullying_level,
            step=step,
            rng=rng,
            working_values=working_values,
            previous_action_counts=previous_action_counts,
        )
        bullying_level = max(0.0, min(100.0, snapshot.bullying_level))
        bullying_history.append(bullying_level)
        snapshots.append(snapshot)
        previous_action_counts = snapshot.action_counts.copy()
        for action in ACTIONS:
            total_action_counts[action] += snapshot.action_counts.get(action, 0)

        if bullying_level >= config.escalation_threshold:
            return finalize_run(
                config,
                composition,
                agents,
                bullying_history,
                snapshots,
                "Got worse",
                persistent_learning_state,
                working_values,
                total_action_counts,
            )
        if bullying_level <= config.calming_threshold:
            return finalize_run(
                config,
                composition,
                agents,
                bullying_history,
                snapshots,
                "Calmed down",
                persistent_learning_state,
                working_values,
                total_action_counts,
            )

    return finalize_run(
        config,
        composition,
        agents,
        bullying_history,
        snapshots,
        "Stayed unresolved",
        persistent_learning_state,
        working_values,
        total_action_counts,
    )


def simulate_step(
    config: SimulationConfig,
    agents: list[AgentProfile],
    bullying_level: float,
    step: int,
    rng: random.Random,
    working_values: dict[str, dict[str, float]],
    previous_action_counts: dict[str, int],
) -> SimulationSnapshot:
    bullying_ratio = bullying_level / 100.0
    toxicity_ratio = config.toxicity_level / 100.0
    identity_ratio = config.identity_attack_level / 100.0

    social_context = infer_social_context(
        previous_action_counts=previous_action_counts,
        total_agents=len(agents),
        tom_influence_strength=config.tom_influence_strength,
    )

    participation_probabilities = {
        "instigator": min(0.92, 0.30 + 0.24 * bullying_ratio + 0.20 * toxicity_ratio),
        "defender": min(0.88, 0.20 + 0.25 * bullying_ratio + 0.12 * identity_ratio),
        "neutral": min(0.80, 0.18 + 0.16 * bullying_ratio),
        "other": 0.12,
    }

    active_agent_ids: list[str] = []
    action_counts = {action: 0 for action in ACTIONS}
    role_action_pairs: list[tuple[str, str]] = []

    for agent in agents:
        if rng.random() >= participation_probabilities[agent.role]:
            continue

        active_agent_ids.append(agent.agent_id)
        tom_adjustments = {
            "support_bully": 0.35 * social_context.expected_bully_support,
            "support_victim": 0.35 * social_context.expected_defence,
            "stay_silent": 0.35 * social_context.expected_silence,
            "step_aside": 0.08,
        }
        action = choose_action(
            base_preferences=BASE_ROLE_PREFERENCES[agent.role],
            learned_values=working_values[agent.role],
            tom_adjustments=tom_adjustments,
            rng=rng,
        )
        action_counts[action] += 1
        role_action_pairs.append((agent.role, action))

    change = bullying_change_from_actions(config, action_counts, len(agents), bullying_level, rng)
    next_bullying_level = bullying_level + change

    # Agents learn immediately from how their action moved the situation.
    for role, action in role_action_pairs:
        reward = role_reward(role, action, change)
        working_values[role][action] = update_action_value(
            current_value=working_values[role][action],
            reward=reward,
            learning_rate=config.learning_rate,
            reward_strength=config.reward_strength,
        )

    return SimulationSnapshot(
        step=step,
        bullying_level=next_bullying_level,
        active_agent_ids=active_agent_ids,
        action_counts=action_counts,
        bullying_change=change,
        story_line=build_story_line(action_counts, change, social_context.expected_defence, social_context.expected_silence),
    )


def bullying_change_from_actions(
    config: SimulationConfig,
    action_counts: dict[str, int],
    total_agents: int,
    bullying_level: float,
    rng,
) -> float:
    bullying_ratio = bullying_level / 100.0
    toxicity_ratio = config.toxicity_level / 100.0
    profanity_ratio = config.profanity_level / 100.0
    identity_ratio = config.identity_attack_level / 100.0
    engagement_ratio = ((config.like_influence + config.retweet_influence) / 2.0) / 100.0

    content_pressure = (
        5.2 * toxicity_ratio
        + 3.0 * profanity_ratio
        + 4.1 * identity_ratio
        + 2.2 * engagement_ratio
    )
    support_pressure = (action_counts["support_bully"] / max(1, total_agents)) * (16 + 6 * toxicity_ratio)
    defence_pressure = (action_counts["support_victim"] / max(1, total_agents)) * (16 + 5 * identity_ratio)
    silence_pressure = (action_counts["stay_silent"] / max(1, total_agents)) * (5 + 4 * bullying_ratio)
    unrelated_pressure = (action_counts["step_aside"] / max(1, total_agents)) * 1.2
    randomness = rng.uniform(-1.0, 1.0)

    return content_pressure + support_pressure + silence_pressure + 0.4 * unrelated_pressure - defence_pressure + randomness


def role_reward(role: str, action: str, bullying_change: float) -> float:
    if role == "instigator":
        if action == "support_bully":
            return 1.0 if bullying_change > 0 else -0.8
        return 0.2 if bullying_change > 0 else -0.3
    if role == "defender":
        if action == "support_victim":
            return 1.0 if bullying_change < 0 else -0.8
        return 0.2 if bullying_change < 0 else -0.3
    if role == "neutral":
        if action == "stay_silent":
            return -0.7 if bullying_change > 0 else 0.1
        if action == "support_victim":
            return 0.6 if bullying_change < 0 else -0.2
        return 0.0
    if action == "step_aside":
        return 0.1 if abs(bullying_change) < 2 else -0.1
    return 0.0


def build_story_line(
    action_counts: dict[str, int],
    bullying_change: float,
    expected_defence: float,
    expected_silence: float,
) -> str:
    supporters = action_counts["support_bully"]
    defenders = action_counts["support_victim"]
    silent = action_counts["stay_silent"]

    if defenders > supporters:
        sentence = "More people stepped in to support the victim than to support the bully, so the pressure began to ease."
    elif supporters > defenders:
        sentence = "More people sided with the bully than defended the victim, so the bullying gained momentum."
    else:
        sentence = "Neither side clearly took control in this step, so the situation stayed mixed."

    if expected_defence > 0.15:
        sentence += " Several agents were influenced by the feeling that others might also defend."
    if silent > 0 and expected_silence > 0.10:
        sentence += " Silence also spread because some agents expected others to stay silent."

    sentence += f" Change this step: {bullying_change:+.1f}."
    return sentence


def finalize_run(
    config: SimulationConfig,
    composition: RoleComposition,
    agents: list[AgentProfile],
    bullying_history: list[float],
    snapshots: list[SimulationSnapshot],
    final_outcome: str,
    persistent_learning_state: ContinualLearningState,
    working_values: dict[str, dict[str, float]],
    total_action_counts: dict[str, int],
) -> SimulationResult:
    total_actions = max(1, sum(total_action_counts.values()))
    action_shares = {
        action: total_action_counts[action] / total_actions
        for action in ACTIONS
    }
    updated_state = blend_persistent_learning(
        persistent_state=persistent_learning_state,
        working_values=working_values,
        memory_retention_strength=config.memory_retention_strength,
        adaptation_speed=config.adaptation_speed,
        action_shares=action_shares,
        outcome=final_outcome,
        carry_learning=config.carry_learning,
    )

    dominant_role = max(composition.as_dict(), key=composition.as_dict().get)
    explanation, simple_takeaway = build_end_of_run_explanation(
        final_outcome=final_outcome,
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
        final_outcome=final_outcome,
        explanation=explanation,
        simple_takeaway=simple_takeaway,
        updated_learning_state=updated_state,
    )
