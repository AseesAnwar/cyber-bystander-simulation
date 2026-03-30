from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class MentalStateEstimate:
    """Simple Theory of Mind estimate derived from visible conversation cues."""

    perceived_aggression: float
    perceived_victim_vulnerability: float
    perceived_social_norm: float
    toxicity_bucket: str
    social_norm_bucket: str


def infer_mental_states(
    source_toxicity: float,
    source_threat: float,
    source_insult: float,
    source_identity_attack: float,
    source_severe_toxicity: float,
    source_sentiment: str,
    reinforce_share: float,
    defend_share: float,
    neutral_share: float,
    empathy_score: float,
) -> MentalStateEstimate:
    """Infer interpretable beliefs from toxicity, sentiment, and reply trends."""

    negative_sentiment_bonus = 0.10 if source_sentiment == "negative" else 0.0
    aggression = _bounded(
        0.40 * source_toxicity
        + 0.20 * source_threat
        + 0.20 * source_insult
        + 0.15 * source_identity_attack
        + 0.05 * source_severe_toxicity
        + negative_sentiment_bonus
    )
    victim_vulnerability = _bounded(
        0.45 * aggression
        + 0.20 * source_identity_attack
        + 0.15 * source_threat
        + 0.10 * source_severe_toxicity
        + 0.10 * empathy_score
    )
    social_norm = _bounded(
        0.50 + 0.50 * reinforce_share - 0.40 * defend_share - 0.10 * neutral_share
    )

    return MentalStateEstimate(
        perceived_aggression=aggression,
        perceived_victim_vulnerability=victim_vulnerability,
        perceived_social_norm=social_norm,
        toxicity_bucket=bucketize_level(aggression),
        social_norm_bucket=bucketize_social_norm(social_norm),
    )


def bucketize_level(value: float) -> str:
    if value < 0.33:
        return "low"
    if value < 0.66:
        return "medium"
    return "high"


def bucketize_social_norm(value: float) -> str:
    if value < 0.40:
        return "defend"
    if value > 0.60:
        return "reinforce"
    return "mixed"


def _bounded(value: float) -> float:
    return max(0.0, min(1.0, value))
