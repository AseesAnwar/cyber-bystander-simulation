from __future__ import annotations

from dataclasses import dataclass


ACTIONS = ["support_bully", "support_victim", "stay_silent", "step_aside"]


@dataclass(slots=True)
class ActionValues:
    values: dict[str, float]

    def copy(self) -> "ActionValues":
        return ActionValues(values=self.values.copy())


def default_action_values() -> ActionValues:
    return ActionValues(values={action: 0.0 for action in ACTIONS})


def choose_action(
    base_preferences: dict[str, float],
    learned_values: dict[str, float],
    tom_adjustments: dict[str, float],
    rng,
) -> str:
    """Pick one action using base role tendency, learning, and ToM influence."""

    weights = {}
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
    """Simple reward-based update. Higher reward makes the action more attractive next time."""

    return current_value + learning_rate * reward_strength * reward
