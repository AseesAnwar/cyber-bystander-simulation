"""Mesa model for the cyber-bystander behavioural simulation.

This model treats one online bullying conversation as a simple environment.
Each step:
1. agents observe the current situation
2. agents reason about what others may do
3. agents act
4. the bullying level changes
5. agents learn from that result

The model is intentionally lightweight so it stays explainable for a university
demo while still using a real Mesa backend.
"""

from __future__ import annotations

from dataclasses import dataclass
import math

from mesa import Model
from mesa.datacollection import DataCollector

from mesa_agents import (
    DefenderAgent,
    InstigatorAgent,
    NeutralAgent,
    OtherAgent,
    infer_social_context,
)
from mesa_learning import (
    ACTIONS,
    ROLE_ORDER,
    MesaLearningState,
    blend_persistent_learning,
    make_working_values,
    reward_for_action,
    update_action_value,
)


@dataclass(slots=True)
class ModelStepRecord:
    step: int
    bullying_level: float
    bullying_change: float
    action_counts: dict[str, int]
    active_agent_ids: list[str]
    story_line: str


def percentages_to_counts(
    total_bystanders: int,
    instigator_pct: float,
    defender_pct: float,
    neutral_pct: float,
    other_pct: float,
) -> dict[str, int]:
    raw = {
        "instigator": max(instigator_pct, 0.0),
        "defender": max(defender_pct, 0.0),
        "neutral": max(neutral_pct, 0.0),
        "other": max(other_pct, 0.0),
    }
    total_pct = sum(raw.values())
    if total_pct <= 0:
        raw = {role: 25.0 for role in ROLE_ORDER}
        total_pct = 100.0

    normalized = {role: raw[role] / total_pct for role in ROLE_ORDER}
    raw_counts = {role: normalized[role] * total_bystanders for role in ROLE_ORDER}
    counts = {role: int(raw_counts[role]) for role in ROLE_ORDER}
    remainder = total_bystanders - sum(counts.values())

    for role in sorted(ROLE_ORDER, key=lambda item: raw_counts[item] - counts[item], reverse=True):
        if remainder <= 0:
            break
        counts[role] += 1
        remainder -= 1

    return counts


class CyberBystanderMesaModel(Model):
    """Mesa model that powers the cyber-bystander dashboard."""

    def __init__(
        self,
        *,
        total_bystanders: int,
        instigator_pct: float,
        defender_pct: float,
        neutral_pct: float,
        other_pct: float,
        initial_aggression: float,
        toxicity_level: float,
        profanity_level: float,
        identity_attack_level: float,
        like_influence: float,
        retweet_influence: float,
        random_seed: int,
        tom_influence_strength: float,
        learning_rate: float,
        reward_strength: float,
        memory_retention_strength: float,
        adaptation_speed: float,
        carry_learning: bool,
        persistent_learning_state: MesaLearningState | None = None,
        max_steps: int = 18,
        escalation_threshold: float = 80.0,
        calming_threshold: float = 20.0,
    ) -> None:
        super().__init__(rng=random_seed)

        self.total_bystanders = int(total_bystanders)
        self.role_counts = percentages_to_counts(
            total_bystanders=self.total_bystanders,
            instigator_pct=instigator_pct,
            defender_pct=defender_pct,
            neutral_pct=neutral_pct,
            other_pct=other_pct,
        )

        self.bullying_intensity = self._clamp(initial_aggression)
        self.initial_aggression = self.bullying_intensity
        self.toxicity_level = self._clamp(toxicity_level)
        self.profanity_level = self._clamp(profanity_level)
        self.identity_attack_level = self._clamp(identity_attack_level)
        self.like_influence = self._clamp(like_influence)
        self.retweet_influence = self._clamp(retweet_influence)

        self.tom_influence_strength = max(0.0, min(1.0, tom_influence_strength))
        self.learning_rate = max(0.0, min(1.0, learning_rate))
        self.reward_strength = max(0.0, reward_strength)
        self.memory_retention_strength = max(0.0, min(1.0, memory_retention_strength))
        self.adaptation_speed = max(0.0, min(1.0, adaptation_speed))
        self.carry_learning = carry_learning

        self.max_steps = int(max_steps)
        self.escalation_threshold = float(escalation_threshold)
        self.calming_threshold = float(calming_threshold)

        self.persistent_learning_state = persistent_learning_state or MesaLearningState()
        self.working_action_values = make_working_values(
            self.persistent_learning_state,
            carry_learning=self.carry_learning,
        )

        self.step_count = 0
        self.running = True
        self.final_outcome = "Running"
        self.previous_action_counts = {action: 0 for action in ACTIONS}
        self.last_action_counts = {action: 0 for action in ACTIONS}
        self.total_action_counts = {action: 0 for action in ACTIONS}
        self.last_active_agent_ids: list[str] = []
        self.last_bullying_change = 0.0
        self.story_records: list[ModelStepRecord] = []
        self.social_context = infer_social_context(self.previous_action_counts, self.total_bystanders)
        self._pending_actions: list[tuple[object, str]] = []
        self._learning_finalized = False
        self.updated_learning_state = self.persistent_learning_state

        self._build_agents()

        self.datacollector = DataCollector(
            model_reporters={
                "step": "step_count",
                "bullying_level": "bullying_intensity",
                "support_bully_actions": lambda model: model.last_action_counts.get("support_bully", 0),
                "support_victim_actions": lambda model: model.last_action_counts.get("support_victim", 0),
                "silent_actions": lambda model: model.last_action_counts.get("stay_silent", 0),
                "step_aside_actions": lambda model: model.last_action_counts.get("step_aside", 0),
                "bullying_change": "last_bullying_change",
                "outcome": "final_outcome",
            },
            agent_reporters={
                "role": "role",
                "last_action": "last_action",
                "last_reward": "last_reward",
                "was_active": "was_active",
            },
        )
        self.datacollector.collect(self)

    def _build_agents(self) -> None:
        agent_classes = {
            "instigator": InstigatorAgent,
            "defender": DefenderAgent,
            "neutral": NeutralAgent,
            "other": OtherAgent,
        }
        role_stream: list[str] = []
        for role in ROLE_ORDER:
            role_stream.extend([role] * self.role_counts[role])

        for index, role in enumerate(role_stream):
            angle = (2 * math.pi * index) / max(1, len(role_stream))
            radius = 1.9 + 0.18 * (index % 3)
            agent_class = agent_classes[role]
            agent_class(
                self,
                visual_id=f"{role}_{index}",
                display_x=radius * math.cos(angle),
                display_y=radius * math.sin(angle),
            )

    def _clamp(self, value: float, minimum: float = 0.0, maximum: float = 100.0) -> float:
        return max(minimum, min(maximum, float(value)))

    def participation_probability(self, role: str) -> float:
        bullying_ratio = self.bullying_intensity / 100.0
        toxicity_ratio = self.toxicity_level / 100.0
        identity_ratio = self.identity_attack_level / 100.0

        probabilities = {
            "instigator": min(0.92, 0.30 + 0.24 * bullying_ratio + 0.20 * toxicity_ratio),
            "defender": min(0.88, 0.20 + 0.25 * bullying_ratio + 0.12 * identity_ratio),
            "neutral": min(0.80, 0.18 + 0.16 * bullying_ratio),
            "other": 0.12,
        }
        return probabilities[role]

    def register_action(self, agent, action: str) -> None:
        self._pending_actions.append((agent, action))

    def bullying_change_from_actions(self, action_counts: dict[str, int]) -> float:
        bullying_ratio = self.bullying_intensity / 100.0
        toxicity_ratio = self.toxicity_level / 100.0
        profanity_ratio = self.profanity_level / 100.0
        identity_ratio = self.identity_attack_level / 100.0
        engagement_ratio = ((self.like_influence + self.retweet_influence) / 2.0) / 100.0

        content_pressure = (
            5.2 * toxicity_ratio
            + 3.0 * profanity_ratio
            + 4.1 * identity_ratio
            + 2.2 * engagement_ratio
        )
        support_pressure = (action_counts["support_bully"] / max(1, self.total_bystanders)) * (16 + 6 * toxicity_ratio)
        defence_pressure = (action_counts["support_victim"] / max(1, self.total_bystanders)) * (16 + 5 * identity_ratio)
        silence_pressure = (action_counts["stay_silent"] / max(1, self.total_bystanders)) * (5 + 4 * bullying_ratio)
        unrelated_pressure = (action_counts["step_aside"] / max(1, self.total_bystanders)) * 1.2
        randomness = self.random.uniform(-1.0, 1.0)

        return content_pressure + support_pressure + silence_pressure + 0.4 * unrelated_pressure - defence_pressure + randomness

    def build_story_line(self, action_counts: dict[str, int], change: float) -> str:
        supporters = action_counts["support_bully"]
        defenders = action_counts["support_victim"]
        silent = action_counts["stay_silent"]

        if defenders > supporters:
            sentence = "More people stepped in to support the victim than to support the bully, so the pressure began to ease."
        elif supporters > defenders:
            sentence = "More people sided with the bully than defended the victim, so the bullying gained momentum."
        else:
            sentence = "Neither side clearly took control in this step, so the situation stayed mixed."

        if self.social_context.defence_pressure > 0.15:
            sentence += " Several agents were influenced by the feeling that others might also defend."
        if silent > 0 and self.social_context.silence_pressure > 0.10:
            sentence += " Silence also spread because some agents expected others to stay silent."

        sentence += f" Change this step: {change:+.1f}."
        return sentence

    def step(self) -> None:
        if not self.running:
            return

        self._pending_actions = []
        self.social_context = infer_social_context(
            self.previous_action_counts,
            total_agents=self.total_bystanders,
        )

        self.agents.shuffle_do("step")

        action_counts = {action: 0 for action in ACTIONS}
        active_agent_ids: list[str] = []
        for agent, action in self._pending_actions:
            action_counts[action] += 1
            active_agent_ids.append(agent.visual_id)

        change = self.bullying_change_from_actions(action_counts)
        self.bullying_intensity = self._clamp(self.bullying_intensity + change)

        for agent, action in self._pending_actions:
            reward = reward_for_action(agent.role, action, change)
            agent.last_reward = reward
            self.working_action_values[agent.role][action] = update_action_value(
                current_value=self.working_action_values[agent.role][action],
                reward=reward,
                learning_rate=self.learning_rate,
                reward_strength=self.reward_strength,
            )

        self.step_count += 1
        self.last_action_counts = action_counts.copy()
        self.last_active_agent_ids = active_agent_ids
        self.last_bullying_change = change
        self.previous_action_counts = action_counts.copy()

        for action in ACTIONS:
            self.total_action_counts[action] += action_counts[action]

        story_line = self.build_story_line(action_counts, change)
        self.story_records.append(
            ModelStepRecord(
                step=self.step_count,
                bullying_level=self.bullying_intensity,
                bullying_change=change,
                action_counts=action_counts.copy(),
                active_agent_ids=active_agent_ids,
                story_line=story_line,
            )
        )

        if self.bullying_intensity >= self.escalation_threshold:
            self.final_outcome = "Got worse"
            self.running = False
        elif self.bullying_intensity <= self.calming_threshold:
            self.final_outcome = "Calmed down"
            self.running = False
        elif self.step_count >= self.max_steps:
            self.final_outcome = "Stayed unresolved"
            self.running = False

        self.datacollector.collect(self)

    def run_to_completion(self) -> None:
        while self.running:
            self.step()
        self.finalize_learning()

    def finalize_learning(self) -> MesaLearningState:
        if self._learning_finalized:
            return self.updated_learning_state

        total_actions = max(1, sum(self.total_action_counts.values()))
        action_shares = {
            action: self.total_action_counts[action] / total_actions
            for action in ACTIONS
        }
        self.updated_learning_state = blend_persistent_learning(
            persistent_state=self.persistent_learning_state,
            working_values=self.working_action_values,
            memory_retention_strength=self.memory_retention_strength,
            adaptation_speed=self.adaptation_speed,
            action_shares=action_shares,
            outcome=self.final_outcome,
            carry_learning=self.carry_learning,
        )
        self._learning_finalized = True
        return self.updated_learning_state
