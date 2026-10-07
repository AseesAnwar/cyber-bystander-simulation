"""Interactive CYBY23-driven Mesa cyberbystander model.

This is intentionally separate from the existing dashboard/model files so it
can be developed without disturbing any currently running demo.
"""

from __future__ import annotations

from dataclasses import dataclass
import random

import pandas as pd
from mesa import Agent, Model
from mesa.datacollection import DataCollector

from preprocess_cyby23 import (
    ThreadRecord,
    build_thread_records,
    clean_dataset,
    load_raw_dataset,
)


ACTIONS = ["ignore", "defend", "report", "reinforce"]


ROLE_TO_ACTION = {
    "reinforce": "reinforce",
    "defend": "defend",
    "neutral": "ignore",
    "unrelated": "ignore",
}


@dataclass(slots=True)
class CYBY23SimulationConfig:
    dataset_path: str | None = None
    thread_id: str | None = None
    risk_filter: str = "all"
    steps: int = 20
    anonymity_level: float = 0.55
    peer_influence_strength: float = 0.65
    learning_rate: float = 0.30
    learning_strength: float = 0.75
    seed: int = 17


@dataclass(slots=True)
class CYBY23SimulationResult:
    thread: ThreadRecord
    time_series: pd.DataFrame
    agent_snapshot: pd.DataFrame
    final_outcome: str
    explanation: str


class CYBY23BystanderAgent(Agent):
    """One bystander reply from CYBY23, turned into an adaptive simulation agent."""

    def __init__(
        self,
        model: "CYBY23BystanderModel",
        *,
        agent_id: str,
        observed_role: str,
        polarity: float,
        subjectivity: float,
        observed_toxicity: float,
    ) -> None:
        super().__init__(model)
        self.agent_id = agent_id
        self.observed_role = observed_role
        self.observed_action = ROLE_TO_ACTION.get(observed_role, "ignore")
        self.polarity = polarity
        self.subjectivity = subjectivity
        self.observed_toxicity = observed_toxicity
        self.last_action = "none"
        self.last_reward = 0.0

        self.empathy = self._infer_empathy()
        self.anonymity_sensitivity = self._infer_anonymity_sensitivity()
        self.peer_susceptibility = self._infer_peer_susceptibility()
        self.learned_values = {action: 0.0 for action in ACTIONS}
        self.learned_values[self.observed_action] += model.learning_strength * 0.35

    def step(self) -> None:
        weights = self._action_weights()
        action = self.random.choices(
            ACTIONS,
            weights=[weights[action] for action in ACTIONS],
            k=1,
        )[0]
        self.last_action = action
        self.model.register_action(self, action)

    def apply_reward(self, bullying_change: float) -> None:
        reward = self._reward_for_action(self.last_action, bullying_change)
        self.last_reward = reward
        self.learned_values[self.last_action] += self.model.learning_rate * reward

    def _action_weights(self) -> dict[str, float]:
        peer_pressure = self.model.peer_action_share
        risk = self.model.current_risk
        anonymity = self.model.anonymity_level
        peer_strength = self.model.peer_influence_strength

        weights = {
            "ignore": 0.25 + 0.55 * anonymity + 0.35 * (1.0 - self.empathy),
            "defend": 0.18 + 0.95 * self.empathy + 0.30 * risk,
            "report": 0.10 + 0.65 * self.empathy + 0.55 * risk + 0.20 * anonymity,
            "reinforce": 0.12 + 0.75 * (1.0 - self.empathy) + 0.55 * anonymity,
        }

        for action in ACTIONS:
            weights[action] += self.learned_values[action]
            weights[action] += peer_strength * self.peer_susceptibility * peer_pressure[action]

        if self.observed_action in weights:
            weights[self.observed_action] += self.model.learning_strength * 0.25

        return {action: max(0.01, weight) for action, weight in weights.items()}

    def _infer_empathy(self) -> float:
        if self.observed_role == "defend":
            base = 0.78
        elif self.observed_role == "neutral":
            base = 0.45
        elif self.observed_role == "unrelated":
            base = 0.35
        else:
            base = 0.25
        sentiment_adjustment = 0.15 * max(-1.0, min(1.0, self.polarity))
        toxicity_penalty = 0.20 * max(0.0, min(1.0, self.observed_toxicity))
        return _clamp01(base + sentiment_adjustment - toxicity_penalty)

    def _infer_anonymity_sensitivity(self) -> float:
        if self.observed_role == "reinforce":
            base = 0.70
        elif self.observed_role == "neutral":
            base = 0.55
        else:
            base = 0.40
        return _clamp01(base + self.random.uniform(-0.10, 0.10))

    def _infer_peer_susceptibility(self) -> float:
        base = 0.45 + 0.35 * max(0.0, min(1.0, self.subjectivity))
        if self.observed_role == "neutral":
            base += 0.10
        return _clamp01(base + self.random.uniform(-0.10, 0.10))

    def _reward_for_action(self, action: str, bullying_change: float) -> float:
        if action in {"defend", "report"}:
            return 1.0 if bullying_change < 0 else -0.7
        if action == "reinforce":
            return 1.0 if bullying_change > 0 else -0.8
        return -0.45 if bullying_change > 0 else 0.15


class CYBY23BystanderModel(Model):
    """Mesa model that learns bystander behaviour from a selected CYBY23 thread."""

    def __init__(
        self,
        *,
        thread: ThreadRecord,
        steps: int,
        anonymity_level: float,
        peer_influence_strength: float,
        learning_rate: float,
        learning_strength: float,
        seed: int,
    ) -> None:
        super().__init__(rng=seed)
        self.thread = thread
        self.max_steps = int(steps)
        self.anonymity_level = _clamp01(anonymity_level)
        self.peer_influence_strength = _clamp01(peer_influence_strength)
        self.learning_rate = _clamp01(learning_rate)
        self.learning_strength = max(0.0, min(2.0, learning_strength))
        self.step_count = 0
        self.running = True
        self.final_outcome = "Running"
        self.action_counts = {action: 0 for action in ACTIONS}
        self.peer_action_share = {action: 0.0 for action in ACTIONS}
        self.current_risk = _clamp01(
            0.55 * thread.source_toxicity
            + 0.20 * thread.source_identity_attack
            + 0.15 * thread.source_threat
            + 0.10 * thread.source_profanity
        )
        self.bullying_level = _clamp100(
            25
            + 45 * thread.source_toxicity
            + 12 * thread.source_profanity
            + 10 * thread.source_identity_attack
            + 8 * thread.source_threat
        )
        self.last_bullying_change = 0.0
        self._pending_actions: list[tuple[CYBY23BystanderAgent, str]] = []

        self._build_agents_from_thread()

        self.datacollector = DataCollector(
            model_reporters={
                "step": "step_count",
                "bullying_level": "bullying_level",
                "ignore": lambda model: model.action_counts["ignore"],
                "defend": lambda model: model.action_counts["defend"],
                "report": lambda model: model.action_counts["report"],
                "reinforce": lambda model: model.action_counts["reinforce"],
                "bullying_change": "last_bullying_change",
                "outcome": "final_outcome",
            },
            agent_reporters={
                "agent_id": "agent_id",
                "observed_role": "observed_role",
                "last_action": "last_action",
                "empathy": "empathy",
                "anonymity_sensitivity": "anonymity_sensitivity",
                "peer_susceptibility": "peer_susceptibility",
                "last_reward": "last_reward",
            },
        )
        self.datacollector.collect(self)

    def _build_agents_from_thread(self) -> None:
        bystanders = self.thread.bystanders
        if not bystanders:
            return

        for index, bystander in enumerate(bystanders):
            CYBY23BystanderAgent(
                self,
                agent_id=f"{bystander.user_id}_{index}",
                observed_role=bystander.role_label,
                polarity=bystander.polarity,
                subjectivity=bystander.subjectivity,
                observed_toxicity=bystander.observed_toxicity,
            )

    def register_action(self, agent: CYBY23BystanderAgent, action: str) -> None:
        self._pending_actions.append((agent, action))

    def step(self) -> None:
        if not self.running:
            return

        self._pending_actions = []
        self.agents.shuffle_do("step")

        counts = {action: 0 for action in ACTIONS}
        for _, action in self._pending_actions:
            counts[action] += 1

        change = self._bullying_change(counts)
        self.bullying_level = _clamp100(self.bullying_level + change)

        for agent, _ in self._pending_actions:
            agent.apply_reward(change)

        self.step_count += 1
        self.action_counts = counts
        total_actions = max(1, sum(counts.values()))
        self.peer_action_share = {
            action: counts[action] / total_actions for action in ACTIONS
        }
        self.last_bullying_change = change

        if self.bullying_level >= 80:
            self.final_outcome = "Escalated"
            self.running = False
        elif self.bullying_level <= 20:
            self.final_outcome = "De-escalated"
            self.running = False
        elif self.step_count >= self.max_steps:
            self.final_outcome = "Unresolved"
            self.running = False

        self.datacollector.collect(self)

    def run_to_completion(self) -> None:
        while self.running:
            self.step()

    def _bullying_change(self, counts: dict[str, int]) -> float:
        total = max(1, len(self.agents))
        content_pressure = 5.5 * self.current_risk
        anonymity_pressure = 2.0 * self.anonymity_level
        reinforce_pressure = (counts["reinforce"] / total) * (16 + 8 * self.current_risk)
        silence_pressure = (counts["ignore"] / total) * (5 + 4 * self.current_risk)
        defend_pressure = (counts["defend"] / total) * (15 + 5 * self.current_risk)
        report_pressure = (counts["report"] / total) * (18 + 4 * self.current_risk)
        noise = self.random.uniform(-1.0, 1.0)
        return (
            content_pressure
            + anonymity_pressure
            + reinforce_pressure
            + silence_pressure
            - defend_pressure
            - report_pressure
            + noise
        )


def load_cyby23_threads(dataset_path: str | None = None) -> list[ThreadRecord]:
    raw_df = load_raw_dataset(dataset_path)
    cleaned_df = clean_dataset(raw_df)
    return build_thread_records(cleaned_df)


def filter_threads_by_risk(
    threads: list[ThreadRecord],
    risk_filter: str,
) -> list[ThreadRecord]:
    normalized = risk_filter.lower().strip()
    if normalized == "all":
        return threads
    return [thread for thread in threads if thread.risk_level == normalized]


def select_thread(
    threads: list[ThreadRecord],
    thread_id: str | None,
    risk_filter: str,
    seed: int,
) -> ThreadRecord:
    candidates = filter_threads_by_risk(threads, risk_filter)
    if not candidates:
        candidates = threads
    if not candidates:
        raise ValueError("No CYBY23 threads were available for the simulation.")

    if thread_id:
        for thread in candidates:
            if thread.thread_id == thread_id:
                return thread

    return random.Random(seed).choice(candidates)


def run_cyby23_simulation(config: CYBY23SimulationConfig) -> CYBY23SimulationResult:
    threads = load_cyby23_threads(config.dataset_path)
    thread = select_thread(
        threads=threads,
        thread_id=config.thread_id,
        risk_filter=config.risk_filter,
        seed=config.seed,
    )
    model = CYBY23BystanderModel(
        thread=thread,
        steps=config.steps,
        anonymity_level=config.anonymity_level,
        peer_influence_strength=config.peer_influence_strength,
        learning_rate=config.learning_rate,
        learning_strength=config.learning_strength,
        seed=config.seed,
    )
    model.run_to_completion()

    time_series = model.datacollector.get_model_vars_dataframe().reset_index(drop=True)
    agent_snapshot = model.datacollector.get_agent_vars_dataframe().reset_index()
    latest_agent_rows = (
        agent_snapshot.sort_values(["AgentID", "Step"])
        .groupby("AgentID", as_index=False)
        .tail(1)
        .reset_index(drop=True)
    )
    final_level = float(time_series.iloc[-1]["bullying_level"])
    explanation = _build_explanation(thread, model.final_outcome, final_level, latest_agent_rows)
    return CYBY23SimulationResult(
        thread=thread,
        time_series=time_series,
        agent_snapshot=latest_agent_rows,
        final_outcome=model.final_outcome,
        explanation=explanation,
    )


def _build_explanation(
    thread: ThreadRecord,
    outcome: str,
    final_level: float,
    agents: pd.DataFrame,
) -> str:
    final_actions = agents["last_action"].value_counts().to_dict()
    top_action = max(ACTIONS, key=lambda action: final_actions.get(action, 0))
    return (
        f"This run used CYBY23 thread `{thread.thread_id}` with `{len(thread.bystanders)}` labelled bystander replies. "
        f"The agents were initialized from the observed CYBY23 role labels, then adapted through reward learning during the run. "
        f"The final outcome was `{outcome}` with bullying level `{final_level:.1f}`. "
        f"The most common final action was `{top_action}`."
    )


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


def _clamp100(value: float) -> float:
    return max(0.0, min(100.0, float(value)))
