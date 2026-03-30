from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class MemoryEntry:
    action: str
    reward: float
    escalation_score: float
    defence_score: float


@dataclass(slots=True)
class RollingExperienceMemory:
    """Small continual learning memory with decay-based forgetting."""

    window_size: int = 8
    decay: float = 0.85
    entries: list[MemoryEntry] = field(default_factory=list)

    def remember(
        self,
        action: str,
        reward: float,
        escalation_score: float,
        defence_score: float,
    ) -> None:
        self.entries.append(
            MemoryEntry(
                action=action,
                reward=reward,
                escalation_score=escalation_score,
                defence_score=defence_score,
            )
        )
        if len(self.entries) > self.window_size:
            self.entries = self.entries[-self.window_size :]

    def action_bias(self, actions: list[str]) -> dict[str, float]:
        bias = {action: 0.0 for action in actions}
        for offset, entry in enumerate(reversed(self.entries)):
            weight = self.decay**offset
            bias[entry.action] += weight * entry.reward
        return bias

    def recent_average_reward(self) -> float:
        if not self.entries:
            return 0.0
        return sum(entry.reward for entry in self.entries) / len(self.entries)

    def recent_outcome_signal(self) -> float:
        if not self.entries:
            return 0.0
        weighted = [
            (entry.defence_score - entry.escalation_score) * (self.decay**offset)
            for offset, entry in enumerate(reversed(self.entries))
        ]
        return sum(weighted) / max(1, len(weighted))
