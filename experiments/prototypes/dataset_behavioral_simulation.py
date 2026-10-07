from __future__ import annotations

from dataclasses import dataclass
import random

from preprocess_cyby23 import ThreadRecord


ROLE_MAP = {
    "reinforce": "instigator",
    "defend": "defender",
    "neutral": "neutral",
    "unrelated": "other",
}

ROLE_ORDER = ["instigator", "defender", "neutral", "other"]


@dataclass(slots=True)
class DatasetScenario:
    thread_id: str
    source_text: str
    source_user: str
    risk_level: str
    source_toxicity: float
    source_profanity: float
    source_identity_attack: float
    source_threat: float
    source_retweet_count: float
    source_favorite_count: float
    bystander_counts: dict[str, int]
    observed_reply_count: int


@dataclass(slots=True)
class SimulationStep:
    step: int
    aggression: float
    active_instigators: int
    active_defenders: int
    active_neutrals: int
    active_others: int
    change: float
    summary: str


@dataclass(slots=True)
class DatasetSimulationResult:
    scenario: DatasetScenario
    aggression_history: list[float]
    steps: list[SimulationStep]
    final_outcome: str
    explanation: str


def thread_to_dataset_scenario(thread_record: ThreadRecord) -> DatasetScenario:
    bystander_counts = {role: 0 for role in ROLE_ORDER}
    for reply_role, count in thread_record.observed_role_distribution.items():
        mapped = ROLE_MAP.get(reply_role)
        if mapped is not None:
            bystander_counts[mapped] += count

    return DatasetScenario(
        thread_id=thread_record.thread_id,
        source_text=thread_record.source_text,
        source_user=thread_record.source_user,
        risk_level=thread_record.risk_level,
        source_toxicity=thread_record.source_toxicity,
        source_profanity=thread_record.source_profanity,
        source_identity_attack=thread_record.source_identity_attack,
        source_threat=thread_record.source_threat,
        source_retweet_count=thread_record.source_retweet_count,
        source_favorite_count=thread_record.source_favorite_count,
        bystander_counts=bystander_counts,
        observed_reply_count=sum(bystander_counts.values()),
    )


def simulate_dataset_scenario(
    scenario: DatasetScenario,
    seed: int,
    max_steps: int = 20,
    escalation_threshold: float = 80.0,
    deescalation_threshold: float = 20.0,
) -> DatasetSimulationResult:
    rng = random.Random(seed)
    aggression = _bounded_100(
        25
        + 45 * scenario.source_toxicity
        + 12 * scenario.source_profanity
        + 10 * scenario.source_identity_attack
        + 8 * scenario.source_threat
    )
    aggression_history = [aggression]
    steps: list[SimulationStep] = []

    for step_index in range(1, max_steps + 1):
        step = _simulate_step(scenario, aggression, step_index, rng)
        aggression = _bounded_100(step.aggression)
        aggression_history.append(aggression)
        steps.append(step)

        if aggression >= escalation_threshold:
            return DatasetSimulationResult(
                scenario=scenario,
                aggression_history=aggression_history,
                steps=steps,
                final_outcome="Escalated",
                explanation=_build_explanation(scenario, steps, "Escalated"),
            )
        if aggression <= deescalation_threshold:
            return DatasetSimulationResult(
                scenario=scenario,
                aggression_history=aggression_history,
                steps=steps,
                final_outcome="De-escalated",
                explanation=_build_explanation(scenario, steps, "De-escalated"),
            )

    return DatasetSimulationResult(
        scenario=scenario,
        aggression_history=aggression_history,
        steps=steps,
        final_outcome="Stable / unresolved",
        explanation=_build_explanation(scenario, steps, "Stable / unresolved"),
    )


def _simulate_step(
    scenario: DatasetScenario,
    current_aggression: float,
    step_index: int,
    rng: random.Random,
) -> SimulationStep:
    total = max(1, scenario.observed_reply_count)
    aggression_ratio = current_aggression / 100.0

    instigator_prob = min(0.92, 0.28 + 0.30 * scenario.source_toxicity + 0.18 * aggression_ratio)
    defender_prob = min(0.88, 0.20 + 0.22 * scenario.source_identity_attack + 0.20 * aggression_ratio)
    neutral_prob = min(0.78, 0.18 + 0.22 * aggression_ratio)
    other_prob = min(0.22, 0.08 + 0.05 * (scenario.source_retweet_count / 10.0))

    active_instigators = _sample_count(scenario.bystander_counts["instigator"], instigator_prob, rng)
    active_defenders = _sample_count(scenario.bystander_counts["defender"], defender_prob, rng)
    active_neutrals = _sample_count(scenario.bystander_counts["neutral"], neutral_prob, rng)
    active_others = _sample_count(scenario.bystander_counts["other"], other_prob, rng)

    engagement_pressure = min(
        1.0,
        0.06 * scenario.source_retweet_count + 0.02 * scenario.source_favorite_count,
    )
    content_pressure = (
        1.10 * scenario.source_toxicity
        + 0.70 * scenario.source_profanity
        + 0.90 * scenario.source_identity_attack
        + 0.65 * scenario.source_threat
        + 0.45 * engagement_pressure
    )
    instigator_pressure = (active_instigators / total) * (14 + 7 * scenario.source_toxicity)
    defender_pressure = (active_defenders / total) * (14 + 6 * scenario.source_identity_attack)
    neutral_pressure = (active_neutrals / total) * (4 + 3 * aggression_ratio)
    other_pressure = (active_others / total) * 1.0
    randomness = rng.uniform(-1.0, 1.0)

    change = (
        5.5 * content_pressure
        + instigator_pressure
        + neutral_pressure
        + 0.4 * other_pressure
        - defender_pressure
        + randomness
    )
    next_aggression = current_aggression + change

    return SimulationStep(
        step=step_index,
        aggression=next_aggression,
        active_instigators=active_instigators,
        active_defenders=active_defenders,
        active_neutrals=active_neutrals,
        active_others=active_others,
        change=change,
        summary=_build_step_summary(
            active_instigators=active_instigators,
            active_defenders=active_defenders,
            active_neutrals=active_neutrals,
            active_others=active_others,
            change=change,
        ),
    )


def _sample_count(count: int, probability: float, rng: random.Random) -> int:
    active = 0
    for _ in range(count):
        if rng.random() < probability:
            active += 1
    return active


def _build_step_summary(
    active_instigators: int,
    active_defenders: int,
    active_neutrals: int,
    active_others: int,
    change: float,
) -> str:
    if active_instigators > active_defenders:
        summary = "Instigators were more active than defenders, so aggression increased."
    elif active_defenders > active_instigators:
        summary = "Defenders were more active than instigators, so aggression eased."
    else:
        summary = "Support for the bully and pushback stayed fairly balanced."

    if active_neutrals > 0 and active_instigators >= active_defenders:
        summary += " Neutral silence made it easier for hostility to continue."
    if active_others > 0:
        summary += " Unrelated replies had little effect on the main conflict."
    summary += f" Net change: {change:+.1f}."
    return summary


def _build_explanation(
    scenario: DatasetScenario,
    steps: list[SimulationStep],
    final_outcome: str,
) -> str:
    dominant_role = max(scenario.bystander_counts, key=scenario.bystander_counts.get)
    final_aggression = steps[-1].aggression if steps else 0.0
    if final_outcome == "Escalated":
        outcome_text = "This conversation escalated because harmful content signals and supporting bystanders outweighed protective responses."
    elif final_outcome == "De-escalated":
        outcome_text = "This conversation de-escalated because defending behaviour reduced aggression faster than harmful pressure increased it."
    else:
        outcome_text = "This conversation stayed unresolved because neither escalation nor de-escalation fully dominated."

    return (
        f"{outcome_text} The selected conversation comes directly from the CYBY23 dataset. "
        f"The largest observed bystander group was {dominant_role}. "
        f"The simulation ended with aggression at {final_aggression:.1f} after {len(steps)} steps."
    )


def _bounded_100(value: float) -> float:
    return max(0.0, min(100.0, value))
