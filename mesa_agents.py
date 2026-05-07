"""Mesa agent classes for the cyber-bystander simulation.

The agents stay intentionally simple:
- they each represent one bystander role
- they observe the recent social direction of the conversation
- they choose an action using role tendency, social influence, and learning
- they update their preference after the model reveals the outcome of the step
"""

from __future__ import annotations

from dataclasses import dataclass

from mesa import Agent

from mesa_learning import BASE_ROLE_PREFERENCES, choose_weighted_action


@dataclass(slots=True)
class SocialContext:
    """What an agent thinks the surrounding conversation currently feels like."""

    bully_support_pressure: float
    defence_pressure: float
    silence_pressure: float


def infer_social_context(
    previous_action_counts: dict[str, int],
    total_agents: int,
) -> SocialContext:
    total = max(1, total_agents)
    return SocialContext(
        bully_support_pressure=previous_action_counts.get("support_bully", 0) / total,
        defence_pressure=previous_action_counts.get("support_victim", 0) / total,
        silence_pressure=previous_action_counts.get("stay_silent", 0) / total,
    )


class BaseBystanderAgent(Agent):
    """Base class for all bystander agents in the Mesa model."""

    ROLE_NAME = "neutral"
    SOCIAL_SENSITIVITY = 1.0

    def __init__(self, model, visual_id: str, display_x: float, display_y: float):
        super().__init__(model)
        self.role = self.ROLE_NAME
        self.visual_id = visual_id
        self.display_x = display_x
        self.display_y = display_y
        self.last_action = "waiting"
        self.last_reward = 0.0
        self.was_active = False

    def step(self) -> None:
        self.was_active = False
        self.last_action = "waiting"
        self.last_reward = 0.0

        if self.random.random() >= self.model.participation_probability(self.role):
            return

        self.was_active = True
        tom_adjustments = self.build_tom_adjustments(self.model.social_context)
        action = choose_weighted_action(
            base_preferences=BASE_ROLE_PREFERENCES[self.role],
            learned_values=self.model.working_action_values[self.role],
            tom_adjustments=tom_adjustments,
            rng=self.random,
        )
        self.last_action = action
        self.model.register_action(self, action)

    def build_tom_adjustments(self, social_context: SocialContext) -> dict[str, float]:
        """Agents respond to what they think others around them may do."""

        influence = max(0.0, self.model.tom_influence_strength) * self.SOCIAL_SENSITIVITY
        return {
            "support_bully": 0.35 * social_context.bully_support_pressure * influence,
            "support_victim": 0.35 * social_context.defence_pressure * influence,
            "stay_silent": 0.35 * social_context.silence_pressure * influence,
            "step_aside": 0.08,
        }


class InstigatorAgent(BaseBystanderAgent):
    ROLE_NAME = "instigator"
    SOCIAL_SENSITIVITY = 0.9


class DefenderAgent(BaseBystanderAgent):
    ROLE_NAME = "defender"
    SOCIAL_SENSITIVITY = 0.95


class NeutralAgent(BaseBystanderAgent):
    ROLE_NAME = "neutral"
    SOCIAL_SENSITIVITY = 1.15


class OtherAgent(BaseBystanderAgent):
    ROLE_NAME = "other"
    SOCIAL_SENSITIVITY = 0.8
