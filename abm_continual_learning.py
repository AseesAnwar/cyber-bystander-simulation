from __future__ import annotations

from dataclasses import dataclass, field

from abm_rl import ACTIONS, default_action_values


ROLE_ORDER = ["instigator", "defender", "neutral", "other"]


@dataclass(slots=True)
class RunLearningSummary:
    run_number: int
    defender_tendency: float
    bully_support_tendency: float
    silent_tendency: float
    defender_action_share: float
    bully_support_action_share: float
    silent_action_share: float
    outcome: str


@dataclass(slots=True)
class ContinualLearningState:
    """Learning memory that can carry across repeated dashboard runs."""

    role_action_values: dict[str, dict[str, float]] = field(
        default_factory=lambda: {
            role: default_action_values().values.copy() for role in ROLE_ORDER
        }
    )
    run_history: list[RunLearningSummary] = field(default_factory=list)
    run_counter: int = 0


def reset_learning_state() -> ContinualLearningState:
    return ContinualLearningState()


def blend_persistent_learning(
    persistent_state: ContinualLearningState,
    working_values: dict[str, dict[str, float]],
    memory_retention_strength: float,
    adaptation_speed: float,
    action_shares: dict[str, float],
    outcome: str,
    carry_learning: bool,
) -> ContinualLearningState:
    """Keep part of old experience while also absorbing new behaviour changes."""

    retention = max(0.0, min(1.0, memory_retention_strength))
    adaptation = max(0.0, min(1.0, adaptation_speed))

    if carry_learning:
        for role, action_values in working_values.items():
            stored = persistent_state.role_action_values.setdefault(role, default_action_values().values.copy())
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


def average_tendency(state: ContinualLearningState, action_name: str) -> float:
    total = 0.0
    for role in ROLE_ORDER:
        total += state.role_action_values[role].get(action_name, 0.0)
    return total / len(ROLE_ORDER)


def make_working_values(
    persistent_state: ContinualLearningState,
    carry_learning: bool,
) -> dict[str, dict[str, float]]:
    if not carry_learning:
        return {role: default_action_values().values.copy() for role in ROLE_ORDER}
    return {
        role: persistent_state.role_action_values[role].copy()
        for role in ROLE_ORDER
    }
