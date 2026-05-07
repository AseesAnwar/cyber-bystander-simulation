from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class SocialContext:
    """Plain-English Theory of Mind summary of what agents think others may do."""

    expected_bully_support: float
    expected_defence: float
    expected_silence: float


def infer_social_context(
    previous_action_counts: dict[str, int],
    total_agents: int,
    tom_influence_strength: float,
) -> SocialContext:
    """Estimate the social direction of the environment from visible behaviour."""

    total = max(1, total_agents)
    raw_support = previous_action_counts.get("support_bully", 0) / total
    raw_defence = previous_action_counts.get("support_victim", 0) / total
    raw_silence = previous_action_counts.get("stay_silent", 0) / total

    strength = max(0.0, min(1.0, tom_influence_strength))
    return SocialContext(
        expected_bully_support=raw_support * strength,
        expected_defence=raw_defence * strength,
        expected_silence=raw_silence * strength,
    )
