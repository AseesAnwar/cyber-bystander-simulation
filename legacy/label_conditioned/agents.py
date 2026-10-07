from __future__ import annotations

from dataclasses import dataclass

from mesa import Agent

from preprocess_cyby23 import BystanderRecord, ThreadRecord
from rl_module import LearningProfile
from tom_module import MentalStateEstimate, infer_mental_states


ACTION_ORDER = ["reinforce", "defend", "neutral", "unrelated"]


@dataclass(slots=True)
class DecisionSnapshot:
    reinforce: float
    defend: float
    neutral: float
    unrelated: float

    def as_dict(self) -> dict[str, float]:
        return {
            "reinforce": self.reinforce,
            "defend": self.defend,
            "neutral": self.neutral,
            "unrelated": self.unrelated,
        }


class SourcePostAgent(Agent):
    """Static source post representation used to expose thread-level severity."""

    def __init__(self, model: "CyberBystanderThreadModel", thread_record: ThreadRecord) -> None:
        super().__init__(model)
        self.agent_key = f"source::{thread_record.thread_id}"
        self.thread_id = thread_record.thread_id
        self.text = thread_record.source_text
        self.toxicity = thread_record.source_toxicity
        self.threat = thread_record.source_threat
        self.insult = thread_record.source_insult
        self.identity_attack = thread_record.source_identity_attack
        self.profanity = thread_record.source_profanity
        self.severe_toxicity = thread_record.source_severe_toxicity
        self.sentiment = thread_record.source_sentiment
        self.class_label = thread_record.source_class_label
        self.risk_level = thread_record.risk_level


class VictimAgent(Agent):
    """Simplified victim representation used for vulnerability context."""

    def __init__(self, model: "CyberBystanderThreadModel", thread_record: ThreadRecord) -> None:
        super().__init__(model)
        self.agent_key = f"victim::{thread_record.thread_id}"
        self.threat_exposure = min(
            1.0,
            0.45 * thread_record.source_toxicity
            + 0.35 * thread_record.source_threat
            + 0.20 * thread_record.source_identity_attack,
        )


class ModeratorAgent(Agent):
    """Simple moderation presence proxy based on severity and emerging defence."""

    def __init__(self, model: "CyberBystanderThreadModel", thread_record: ThreadRecord) -> None:
        super().__init__(model)
        self.agent_key = f"moderator::{thread_record.thread_id}"
        self.present = thread_record.source_toxicity >= 0.75 or thread_record.source_threat >= 0.25
        self.triggered = False
        self.intervention_step: int | None = None

    def maybe_trigger(self) -> None:
        if self.triggered:
            return
        defend_pressure = self.model.action_counts["defend"] / max(1, self.model.total_bystanders)
        if self.present and (
            self.model.source_post.toxicity >= 0.85
            or self.model.source_post.threat >= 0.30
            or defend_pressure >= 0.40
        ):
            self.triggered = True
            self.intervention_step = self.model.current_step


class BystanderAgent(Agent):
    """Sequential bystander using rules or simplified ToM + RL + continual learning."""

    def __init__(
        self,
        model: "CyberBystanderThreadModel",
        thread_record: ThreadRecord,
        record: BystanderRecord,
        arrival_index: int,
    ) -> None:
        super().__init__(model)
        self.agent_key = f"bystander::{record.tweet_id}"
        self.record = record
        self.arrival_index = arrival_index
        self.role_tendency = record.role_label
        self.sensitivity_to_toxicity = self._bounded(
            0.40 + 0.35 * abs(record.polarity) + 0.25 * record.subjectivity
        )
        self.intervention_threshold = self._bounded(
            0.75
            - 0.35 * self.sensitivity_to_toxicity
            + 0.10 * (arrival_index / max(1, len(thread_record.bystanders)))
        )
        self.conformity_tendency = self._bounded(
            0.25 + 0.25 * record.subjectivity + 0.20 * min(record.favorite_count / 25.0, 1.0)
        )
        self.empathy_score = self._bounded(
            0.55
            + 0.25 * max(-record.polarity, 0.0)
            + (0.10 if self.role_tendency == "defend" else 0.0)
            - (0.15 if self.role_tendency == "reinforce" else 0.0)
            - (0.18 if self.role_tendency == "unrelated" else 0.0)
        )
        self.reinforcement_likelihood = self._bounded(
            0.20
            + (0.38 if self.role_tendency == "reinforce" else 0.0)
            - 0.20 * self.empathy_score
            + 0.12 * max(record.polarity, 0.0)
        )
        self.learning_profile: LearningProfile = self.model.get_learning_profile(record.user_id)
        self.perceived_aggression = 0.0
        self.perceived_victim_vulnerability = 0.0
        self.perceived_social_norm = 0.5
        self.last_state: tuple[str, str] | None = None
        self.last_action: str | None = None
        self.last_probabilities: dict[str, float] | None = None
        self.last_reward = 0.0
        self.last_q_values: dict[str, float] | None = None
        self.last_was_exploration = False

    def step(self) -> None:
        mental_state = self.infer_mental_states()
        if self.model.learning_mode:
            self.last_action = self.choose_action_with_learning(mental_state)
        else:
            probabilities = self.evaluate_action_probabilities(mental_state)
            self.last_probabilities = probabilities.as_dict()
            weights = [self.last_probabilities[action] for action in ACTION_ORDER]
            self.last_action = self.random.choices(ACTION_ORDER, weights=weights, k=1)[0]

    def infer_mental_states(self) -> MentalStateEstimate:
        source = self.model.source_post
        reinforce_share = self.model.visible_share("reinforce")
        defend_share = self.model.visible_share("defend")
        neutral_share = self.model.visible_share("neutral")
        mental_state = infer_mental_states(
            source_toxicity=source.toxicity,
            source_threat=source.threat,
            source_insult=source.insult,
            source_identity_attack=source.identity_attack,
            source_severe_toxicity=source.severe_toxicity,
            source_sentiment=source.sentiment,
            reinforce_share=reinforce_share,
            defend_share=defend_share,
            neutral_share=neutral_share,
            empathy_score=self.empathy_score,
        )
        self.perceived_aggression = mental_state.perceived_aggression
        self.perceived_victim_vulnerability = mental_state.perceived_victim_vulnerability
        self.perceived_social_norm = mental_state.perceived_social_norm
        return mental_state

    def get_learning_state(self, mental_state: MentalStateEstimate) -> tuple[str, str]:
        return (mental_state.toxicity_bucket, mental_state.social_norm_bucket)

    def choose_action_with_learning(self, mental_state: MentalStateEstimate) -> str:
        state = self.get_learning_state(mental_state)
        base_probabilities = self.evaluate_action_probabilities(mental_state)
        self.last_probabilities = base_probabilities.as_dict()
        # Continual learning memory nudges the RL policy toward actions that were rewarded recently.
        memory_bias = self.learning_profile.memory.action_bias(ACTION_ORDER)
        q_values = self.learning_profile.q_learner.get_q_values(state, ACTION_ORDER)
        action, explored = self.learning_profile.q_learner.choose_action(
            state=state,
            actions=ACTION_ORDER,
            rng=self.random,
            action_bias={
                action_name: 0.35 * self.last_probabilities[action_name]
                + 0.15 * memory_bias.get(action_name, 0.0)
                for action_name in ACTION_ORDER
            },
        )
        self.last_state = state
        self.last_q_values = q_values.copy()
        self.last_was_exploration = explored
        return action

    def evaluate_action_probabilities(
        self,
        mental_state: MentalStateEstimate | None = None,
    ) -> DecisionSnapshot:
        mental_state = mental_state or self.infer_mental_states()
        source = self.model.source_post
        reinforce_share = self.model.visible_share("reinforce")
        defend_share = self.model.visible_share("defend")
        neutral_share = self.model.visible_share("neutral")
        moderation_signal = (
            1.0 if self.model.moderator.triggered else 0.3 if self.model.moderator.present else 0.0
        )
        severe_context = (
            0.45 * mental_state.perceived_aggression
            + 0.25 * source.threat
            + 0.20 * mental_state.perceived_victim_vulnerability
            + 0.10 * source.insult
        )
        # Recent successful outcomes can slightly tilt the agent toward defending or reinforcing again.
        memory_signal = self.learning_profile.memory.recent_outcome_signal() if self.model.learning_mode else 0.0

        reinforce = (
            0.18
            + 0.65 * self.reinforcement_likelihood
            + 0.55 * self.conformity_tendency * mental_state.perceived_social_norm
            - 0.45 * severe_context * self.empathy_score
            - 0.20 * moderation_signal
            - 0.15 * memory_signal
        )
        defend = (
            0.15
            + 0.55 * self.empathy_score
            + 0.65
            * (0.55 * mental_state.perceived_aggression + 0.45 * mental_state.perceived_victim_vulnerability)
            * self.sensitivity_to_toxicity
            + 0.45 * self.conformity_tendency * defend_share
            - 0.30 * reinforce_share * self.conformity_tendency
            + 0.10 * moderation_signal
            + 0.15 * memory_signal
        )
        neutral = (
            0.20
            + 0.30 * (1.0 - self.sensitivity_to_toxicity)
            + 0.30 * neutral_share
            + 0.20 * abs(source.sentiment == "neutral")
            + 0.15 * self.conformity_tendency * max(reinforce_share, defend_share)
        )
        unrelated = (
            0.10
            + (0.80 if self.role_tendency == "unrelated" else 0.0)
            + 0.18 * (1.0 - severe_context)
            - 0.10 * self.sensitivity_to_toxicity
        )

        if self.role_tendency == "reinforce":
            reinforce += 0.28
        elif self.role_tendency == "defend":
            defend += 0.25
        elif self.role_tendency == "neutral":
            neutral += 0.18

        if severe_context >= self.intervention_threshold and self.role_tendency != "unrelated":
            defend += 0.12 * self.empathy_score
            neutral -= 0.08

        if reinforce_share > defend_share and self.conformity_tendency >= 0.55:
            reinforce += 0.10
            neutral += 0.05

        if defend_share > reinforce_share and self.conformity_tendency >= 0.55:
            defend += 0.12
            reinforce -= 0.05

        return DecisionSnapshot(**self._normalize_weights(reinforce, defend, neutral, unrelated))

    @staticmethod
    def _normalize_weights(
        reinforce: float,
        defend: float,
        neutral: float,
        unrelated: float,
    ) -> dict[str, float]:
        raw = {
            "reinforce": max(reinforce, 0.01),
            "defend": max(defend, 0.01),
            "neutral": max(neutral, 0.01),
            "unrelated": max(unrelated, 0.01),
        }
        total = sum(raw.values())
        return {action: value / total for action, value in raw.items()}

    @staticmethod
    def _bounded(value: float) -> float:
        return max(0.0, min(1.0, value))
