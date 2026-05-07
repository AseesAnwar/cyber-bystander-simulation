"""Mesa learning helpers for the cyber-bystander simulation.

This module keeps the learning logic readable and lightweight:
- role-based action preferences provide a simple behavioural starting point
- reward updates let agents adjust from outcomes during a run
- persistent memory lets some of that learning carry into later runs

The goal is not to predict people exactly. The goal is to make the agents
behave in a more adaptive, explainable way inside the simulation.
"""

from __future__ import annotations

from dataclasses import dataclass, field


ACTIONS = ["support_bully", "support_victim", "stay_silent", "step_aside"]
ROLE_ORDER = ["instigator", "defender", "neutral", "other"]

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


@dataclass(slots=True)
class RunLearningSummary:
    """Simple history record shown in the dashboard after repeated runs."""

    run_number: int
    defender_tendency: float
    bully_support_tendency: float
    silent_tendency: float
    defender_action_share: float
    bully_support_action_share: float
    silent_action_share: float
    outcome: str


@dataclass(slots=True)
class MesaLearningState:
    """Persistent learning memory that can carry across dashboard runs."""

    role_action_values: dict[str, dict[str, float]] = field(
        default_factory=lambda: {
            role: default_action_values().copy() for role in ROLE_ORDER
        }
    )
    run_history: list[RunLearningSummary] = field(default_factory=list)
    run_counter: int = 0


def default_action_values() -> dict[str, float]:
    return {action: 0.0 for action in ACTIONS}


def reset_learning_state() -> MesaLearningState:
    return MesaLearningState()


def make_working_values(
    persistent_state: MesaLearningState,
    carry_learning: bool,
) -> dict[str, dict[str, float]]:
    if not carry_learning:
        return {role: default_action_values() for role in ROLE_ORDER}
    return {
        role: persistent_state.role_action_values.get(role, default_action_values()).copy()
        for role in ROLE_ORDER
    }


def choose_weighted_action(
    base_preferences: dict[str, float],
    learned_values: dict[str, float],
    tom_adjustments: dict[str, float],
    rng,
) -> str:
    """Choose an action from role tendency, learned preference, and social context."""

    weights: dict[str, float] = {}
    for action in ACTIONS:
        weights[action] = max(
            0.01,
            base_preferences.get(action, 0.0)
            + learned_values.get(action, 0.0)
            + tom_adjustments.get(action, 0.0),
        )

    total = sum(weights.values())
    normalized = [weights[action] / total for action in ACTIONS]
    return rng.choices(ACTIONS, weights=normalized, k=1)[0]


def update_action_value(
    current_value: float,
    reward: float,
    learning_rate: float,
    reward_strength: float,
) -> float:
    """Simple reward update used inside the simulation run."""

    return current_value + learning_rate * reward_strength * reward


def reward_for_action(role: str, action: str, bullying_change: float) -> float:
    """Reward logic stays simple enough to explain in a meeting."""

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


def average_tendency(state: MesaLearningState, action_name: str) -> float:
    total = 0.0
    for role in ROLE_ORDER:
        total += state.role_action_values[role].get(action_name, 0.0)
    return total / len(ROLE_ORDER)


def blend_persistent_learning(
    persistent_state: MesaLearningState,
    working_values: dict[str, dict[str, float]],
    memory_retention_strength: float,
    adaptation_speed: float,
    action_shares: dict[str, float],
    outcome: str,
    carry_learning: bool,
) -> MesaLearningState:
    """Blend old experience with the latest run instead of hard-resetting memory."""

    retention = max(0.0, min(1.0, memory_retention_strength))
    adaptation = max(0.0, min(1.0, adaptation_speed))

    if carry_learning:
        for role, action_values in working_values.items():
            stored = persistent_state.role_action_values.setdefault(role, default_action_values())
            for action in ACTIONS:
                stored[action] = retention * stored.get(action, 0.0) + adaptation * action_values.get(action, 0.0)

    persistent_state.run_counter += 1
    persistent_state.run_history.append(
        RunLearningSummary(
            run_number=persistent_state.run_counter,
            defender_tendency=average_tendency(persistent_state, "support_victim"),
            bully_support_tendency=average_tendency(persistent_state, "support_bully"),
            silent_tendency=average_tendency(persistent_state, "stay_silent"),
            defender_action_share=action_shares.get("support_victim", 0.0),
            bully_support_action_share=action_shares.get("support_bully", 0.0),
            silent_action_share=action_shares.get("stay_silent", 0.0),
            outcome=outcome,
        )
    )
    return persistent_state
