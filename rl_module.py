from __future__ import annotations

from dataclasses import dataclass, field

from memory_module import RollingExperienceMemory


@dataclass(slots=True)
class TabularQLearner:
    """Simple dictionary-based Q-learning."""

    alpha: float = 0.30
    gamma: float = 0.60
    epsilon: float = 0.20
    q_table: dict[tuple[str, str], dict[str, float]] = field(default_factory=dict)

    def get_q_values(self, state: tuple[str, str], actions: list[str]) -> dict[str, float]:
        if state not in self.q_table:
            self.q_table[state] = {action: 0.0 for action in actions}
        else:
            for action in actions:
                self.q_table[state].setdefault(action, 0.0)
        return self.q_table[state]

    def choose_action(
        self,
        state: tuple[str, str],
        actions: list[str],
        rng,
        action_bias: dict[str, float] | None = None,
    ) -> tuple[str, bool]:
        q_values = self.get_q_values(state, actions)
        if rng.random() < self.epsilon:
            return rng.choice(actions), True

        action_bias = action_bias or {action: 0.0 for action in actions}
        combined = {
            action: q_values[action] + action_bias.get(action, 0.0)
            for action in actions
        }
        best_value = max(combined.values())
        best_actions = [action for action, value in combined.items() if value == best_value]
        return rng.choice(best_actions), False

    def update(
        self,
        state: tuple[str, str],
        action: str,
        reward: float,
        next_state: tuple[str, str],
        actions: list[str],
    ) -> None:
        current_q = self.get_q_values(state, actions)
        next_q = self.get_q_values(next_state, actions)
        target = reward + self.gamma * max(next_q.values())
        current_q[action] = current_q[action] + self.alpha * (target - current_q[action])

    def average_q_values(self, actions: list[str]) -> dict[str, float]:
        if not self.q_table:
            return {action: 0.0 for action in actions}
        totals = {action: 0.0 for action in actions}
        for state_values in self.q_table.values():
            for action in actions:
                totals[action] += state_values.get(action, 0.0)
        count = len(self.q_table)
        return {action: totals[action] / count for action in actions}


@dataclass(slots=True)
class LearningProfile:
    """Persistent user-level profile reused across conversations."""

    q_learner: TabularQLearner = field(default_factory=TabularQLearner)
    memory: RollingExperienceMemory = field(default_factory=RollingExperienceMemory)
    interactions_seen: int = 0
