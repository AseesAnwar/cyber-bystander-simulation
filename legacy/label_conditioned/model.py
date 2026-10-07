from __future__ import annotations

from dataclasses import dataclass

import pandas as pd
from mesa import Model
from mesa.datacollection import DataCollector

from agents import ACTION_ORDER, BystanderAgent, ModeratorAgent, SourcePostAgent, VictimAgent
from preprocess_cyby23 import ThreadRecord
from rl_module import LearningProfile


@dataclass(slots=True)
class ThreadSimulationResult:
    thread_id: str
    risk_level: str
    source_toxicity: float
    observed_counts: dict[str, int]
    simulated_counts: dict[str, int]
    escalation_score: float
    defence_score: float
    moderator_triggered: bool
    role_agreement_rate: float
    learning_mode: bool
    average_q_values: dict[str, float]
    mean_reward: float


class CyberBystanderThreadModel(Model):
    """Mesa model that activates bystanders in observed reply order for one conversation."""

    def __init__(
        self,
        thread_record: ThreadRecord,
        seed: int | None = None,
        learning_mode: bool = False,
        learner_registry: dict[str, LearningProfile] | None = None,
    ) -> None:
        super().__init__(rng=seed)
        self.thread_record = thread_record
        self.learning_mode = learning_mode
        self.learner_registry = learner_registry if learner_registry is not None else {}
        self.source_post = SourcePostAgent(self, thread_record)
        self.victim = VictimAgent(self, thread_record)
        self.moderator = ModeratorAgent(self, thread_record)
        self.bystander_agents = [
            BystanderAgent(self, thread_record, record, arrival_index)
            for arrival_index, record in enumerate(thread_record.bystanders, start=1)
        ]
        self.current_step = 0
        self.total_bystanders = len(self.bystander_agents)
        self.next_bystander_index = 0
        self.action_counts = {action: 0 for action in ACTION_ORDER}
        self.action_history: list[dict[str, object]] = []
        self.reward_history: list[float] = []

        self.datacollector = DataCollector(
            model_reporters={
                "thread_id": lambda model: model.thread_record.thread_id,
                "step": lambda model: model.current_step,
                "visible_reinforce": lambda model: model.action_counts["reinforce"],
                "visible_defend": lambda model: model.action_counts["defend"],
                "visible_neutral": lambda model: model.action_counts["neutral"],
                "visible_unrelated": lambda model: model.action_counts["unrelated"],
                "escalation_score": lambda model: model.escalation_score,
                "defence_score": lambda model: model.defence_score,
                "moderator_triggered": lambda model: model.moderator.triggered,
                "mean_reward": lambda model: model.mean_reward,
                "avg_q_reinforce": lambda model: model.average_q_values["reinforce"],
                "avg_q_defend": lambda model: model.average_q_values["defend"],
                "avg_q_neutral": lambda model: model.average_q_values["neutral"],
                "avg_q_unrelated": lambda model: model.average_q_values["unrelated"],
            },
            agent_reporters={
                "agent_key": lambda agent: getattr(agent, "agent_key", "unknown"),
                "last_action": lambda agent: getattr(agent, "last_action", None),
                "role_tendency": lambda agent: getattr(agent, "role_tendency", None),
                "empathy_score": lambda agent: getattr(agent, "empathy_score", None),
                "conformity_tendency": lambda agent: getattr(agent, "conformity_tendency", None),
                "intervention_threshold": lambda agent: getattr(agent, "intervention_threshold", None),
                "perceived_aggression": lambda agent: getattr(agent, "perceived_aggression", None),
                "perceived_victim_vulnerability": lambda agent: getattr(agent, "perceived_victim_vulnerability", None),
                "perceived_social_norm": lambda agent: getattr(agent, "perceived_social_norm", None),
            },
        )
        self.datacollector.collect(self)

    def step(self) -> None:
        if self.finished:
            return

        bystander = self.bystander_agents[self.next_bystander_index]
        self.current_step += 1
        bystander.step()
        self.action_counts[bystander.last_action] += 1
        self.moderator.maybe_trigger()

        reward = self.compute_reward(bystander.last_action)
        bystander.last_reward = reward
        self.reward_history.append(reward)

        history_row: dict[str, object] = {
            "thread_id": self.thread_record.thread_id,
            "step": self.current_step,
            "agent_key": bystander.agent_key,
            "observed_role": bystander.role_tendency,
            "simulated_role": bystander.last_action,
            "source_toxicity": self.source_post.toxicity,
            "moderator_triggered": self.moderator.triggered,
            "learning_mode": self.learning_mode,
            "reward": reward,
            "perceived_aggression": bystander.perceived_aggression,
            "perceived_victim_vulnerability": bystander.perceived_victim_vulnerability,
            "perceived_social_norm": bystander.perceived_social_norm,
            **(bystander.last_probabilities or {}),
        }

        if self.learning_mode and bystander.last_state is not None:
            next_state = bystander.get_learning_state(bystander.infer_mental_states())
            if bystander.last_q_values is not None:
                for action_name, value in bystander.last_q_values.items():
                    history_row[f"q_before_{action_name}"] = value
            bystander.learning_profile.q_learner.update(
                state=bystander.last_state,
                action=bystander.last_action,
                reward=reward,
                next_state=next_state,
                actions=ACTION_ORDER,
            )
            for action_name, value in bystander.learning_profile.q_learner.get_q_values(
                bystander.last_state, ACTION_ORDER
            ).items():
                history_row[f"q_after_{action_name}"] = value
            bystander.learning_profile.memory.remember(
                action=bystander.last_action,
                reward=reward,
                escalation_score=self.escalation_score,
                defence_score=self.defence_score,
            )
            bystander.learning_profile.interactions_seen += 1
            history_row["was_exploration"] = bystander.last_was_exploration

        self.action_history.append(history_row)
        self.next_bystander_index += 1
        self.datacollector.collect(self)

    @property
    def finished(self) -> bool:
        return self.next_bystander_index >= self.total_bystanders

    @property
    def escalation_score(self) -> float:
        total = max(1, self.total_bystanders)
        score = (self.action_counts["reinforce"] + 0.5 * self.action_counts["neutral"]) / total
        return round(float(score), 4)

    @property
    def defence_score(self) -> float:
        total = max(1, self.total_bystanders)
        score = self.action_counts["defend"] / total
        return round(float(score), 4)

    @property
    def mean_reward(self) -> float:
        if not self.reward_history:
            return 0.0
        return round(float(sum(self.reward_history) / len(self.reward_history)), 4)

    @property
    def average_q_values(self) -> dict[str, float]:
        if not self.learning_mode or not self.bystander_agents:
            return {action: 0.0 for action in ACTION_ORDER}

        totals = {action: 0.0 for action in ACTION_ORDER}
        count = 0
        seen_profiles: set[int] = set()
        for bystander in self.bystander_agents:
            profile = bystander.learning_profile
            if id(profile) in seen_profiles:
                continue
            seen_profiles.add(id(profile))
            profile_means = profile.q_learner.average_q_values(ACTION_ORDER)
            for action in ACTION_ORDER:
                totals[action] += profile_means[action]
            count += 1
        if count == 0:
            return {action: 0.0 for action in ACTION_ORDER}
        return {action: round(float(totals[action] / count), 4) for action in ACTION_ORDER}

    def visible_share(self, action: str) -> float:
        visible = max(1, sum(self.action_counts.values()))
        return self.action_counts[action] / visible

    def get_learning_profile(self, user_id: str) -> LearningProfile:
        # Reusing profiles across conversations gives us a simple continual learning effect per user.
        if user_id not in self.learner_registry:
            self.learner_registry[user_id] = LearningProfile()
        return self.learner_registry[user_id]

    def compute_reward(self, action: str) -> float:
        # Rewards stay deliberately simple so they are easy to explain in a presentation.
        escalation = self.escalation_score
        defence = self.defence_score
        if action == "reinforce":
            return round(0.60 * escalation - 0.35 * defence, 4)
        if action == "defend":
            return round(0.70 * defence - 0.40 * escalation, 4)
        if action == "neutral":
            return round(0.05 - 0.10 * abs(escalation - defence), 4)
        return round(-0.05 - 0.05 * escalation, 4)

    def run_to_completion(self) -> ThreadSimulationResult:
        while not self.finished:
            self.step()

        observed_counts = self.thread_record.observed_role_distribution
        simulated_counts = self.action_counts.copy()
        matched = 0
        for bystander in self.bystander_agents:
            if bystander.last_action == bystander.role_tendency:
                matched += 1
        role_agreement_rate = matched / max(1, self.total_bystanders)

        return ThreadSimulationResult(
            thread_id=self.thread_record.thread_id,
            risk_level=self.thread_record.risk_level,
            source_toxicity=self.thread_record.source_toxicity,
            observed_counts=observed_counts,
            simulated_counts=simulated_counts,
            escalation_score=self.escalation_score,
            defence_score=self.defence_score,
            moderator_triggered=self.moderator.triggered,
            role_agreement_rate=round(float(role_agreement_rate), 4),
            learning_mode=self.learning_mode,
            average_q_values=self.average_q_values,
            mean_reward=self.mean_reward,
        )

    def get_model_frame(self) -> pd.DataFrame:
        return self.datacollector.get_model_vars_dataframe().reset_index(drop=True)

    def get_action_history_frame(self) -> pd.DataFrame:
        return pd.DataFrame(self.action_history)


def simulate_thread(
    thread_record: ThreadRecord,
    seed: int | None = None,
    learning_mode: bool = False,
    learner_registry: dict[str, LearningProfile] | None = None,
) -> tuple[CyberBystanderThreadModel, ThreadSimulationResult]:
    model = CyberBystanderThreadModel(
        thread_record=thread_record,
        seed=seed,
        learning_mode=learning_mode,
        learner_registry=learner_registry,
    )
    result = model.run_to_completion()
    return model, result
