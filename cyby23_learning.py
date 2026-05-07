"""Dataset calibration helpers for the CYBY23 cyberbystander simulation.

The dashboard can run from hand-set controls, but this module lets it learn
starting behaviour from observed CYBY23 bystander role labels. It keeps the
calibration intentionally transparent for an assessment/demo setting.
"""

from __future__ import annotations

from dataclasses import dataclass

from mesa_learning import ACTIONS, ROLE_ORDER, MesaLearningState, reset_learning_state
from preprocess_cyby23 import NORMALIZED_ROLE_ORDER, ThreadRecord


ROLE_TO_ACTION = {
    "reinforce": "support_bully",
    "defend": "support_victim",
    "neutral": "stay_silent",
    "unrelated": "step_aside",
}

ROLE_TO_AGENT_TYPE = {
    "reinforce": "instigator",
    "defend": "defender",
    "neutral": "neutral",
    "unrelated": "other",
}


@dataclass(slots=True)
class CYBY23LearningProfile:
    risk_filter: str
    thread_count: int
    labelled_reply_count: int
    role_counts: dict[str, int]
    action_priors: dict[str, float]
    agent_role_percentages: dict[str, float]
    mean_toxicity: float
    mean_profanity: float
    mean_identity_attack: float
    mean_retweets: float
    mean_favorites: float

    def summary(self) -> str:
        return (
            f"Learned from {self.labelled_reply_count} labelled CYBY23 replies across "
            f"{self.thread_count} threads. Observed behaviour was "
            f"{self.action_priors['support_bully']:.0%} bully-supporting, "
            f"{self.action_priors['support_victim']:.0%} victim-supporting, "
            f"{self.action_priors['stay_silent']:.0%} silent, and "
            f"{self.action_priors['step_aside']:.0%} unrelated/aside."
        )


def build_cyby23_learning_profile(
    thread_records: list[ThreadRecord],
    risk_filter: str = "all",
    smoothing: float = 1.0,
) -> CYBY23LearningProfile:
    selected = _filter_threads(thread_records, risk_filter)
    if not selected:
        selected = thread_records
        risk_filter = "all"
    if not selected:
        raise ValueError("No CYBY23 thread records were available for calibration.")

    role_counts = {role: 0 for role in NORMALIZED_ROLE_ORDER}
    for thread in selected:
        for role in NORMALIZED_ROLE_ORDER:
            role_counts[role] += int(thread.observed_role_distribution.get(role, 0))

    action_counts = {action: smoothing for action in ACTIONS}
    for role, count in role_counts.items():
        action_counts[ROLE_TO_ACTION[role]] += count
    action_total = sum(action_counts.values())
    action_priors = {action: action_counts[action] / action_total for action in ACTIONS}

    labelled_reply_count = sum(role_counts.values())
    role_total = max(1, labelled_reply_count)
    agent_role_percentages = {
        ROLE_TO_AGENT_TYPE[role]: (role_counts[role] / role_total) * 100
        for role in NORMALIZED_ROLE_ORDER
    }

    return CYBY23LearningProfile(
        risk_filter=risk_filter,
        thread_count=len(selected),
        labelled_reply_count=labelled_reply_count,
        role_counts=role_counts,
        action_priors=action_priors,
        agent_role_percentages=agent_role_percentages,
        mean_toxicity=_mean([thread.source_toxicity for thread in selected]),
        mean_profanity=_mean([thread.source_profanity for thread in selected]),
        mean_identity_attack=_mean([thread.source_identity_attack for thread in selected]),
        mean_retweets=_mean([thread.source_retweet_count for thread in selected]),
        mean_favorites=_mean([thread.source_favorite_count for thread in selected]),
    )


def build_learning_state_from_profile(
    profile: CYBY23LearningProfile,
    strength: float = 0.7,
) -> MesaLearningState:
    """Create a Mesa learning memory biased by observed CYBY23 action priors."""

    state = reset_learning_state()
    strength = max(0.0, min(2.0, strength))
    uniform_prior = 1.0 / len(ACTIONS)

    for role in ROLE_ORDER:
        for action in ACTIONS:
            observed_bias = profile.action_priors[action] - uniform_prior
            state.role_action_values[role][action] = observed_bias * strength

    # Keep role identities explainable while still letting the dataset shift the baseline.
    state.role_action_values["instigator"]["support_bully"] += 0.20 * strength
    state.role_action_values["defender"]["support_victim"] += 0.20 * strength
    state.role_action_values["neutral"]["stay_silent"] += 0.20 * strength
    state.role_action_values["other"]["step_aside"] += 0.20 * strength
    return state


def _filter_threads(thread_records: list[ThreadRecord], risk_filter: str) -> list[ThreadRecord]:
    normalized_filter = risk_filter.lower().strip()
    if normalized_filter == "all":
        return thread_records
    return [thread for thread in thread_records if thread.risk_level == normalized_filter]


def _mean(values: list[float]) -> float:
    return sum(values) / max(1, len(values))
