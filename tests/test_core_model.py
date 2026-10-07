import unittest

from mesa_learning import BASE_ROLE_PREFERENCES, update_action_value
from mesa_model import percentages_to_counts
from mesa_bridge import SimulationConfig, simulate_scenario
from mesa_learning import MesaLearningState


class CoreModelTests(unittest.TestCase):
    def test_percentage_conversion_preserves_population(self):
        counts = percentages_to_counts(
            total_bystanders=37,
            instigator_pct=18,
            defender_pct=42,
            neutral_pct=30,
            other_pct=10,
        )
        self.assertEqual(sum(counts.values()), 37)
        self.assertTrue(all(value >= 0 for value in counts.values()))

    def test_zero_percentages_fall_back_to_even_distribution(self):
        counts = percentages_to_counts(
            total_bystanders=20,
            instigator_pct=0,
            defender_pct=0,
            neutral_pct=0,
            other_pct=0,
        )
        self.assertEqual(sum(counts.values()), 20)

    def test_base_role_preferences_are_probabilities(self):
        for preferences in BASE_ROLE_PREFERENCES.values():
            self.assertAlmostEqual(sum(preferences.values()), 1.0, places=8)
            self.assertTrue(all(value >= 0 for value in preferences.values()))

    def test_positive_reward_increases_action_value(self):
        updated = update_action_value(
            current_value=0.0,
            reward=1.0,
            learning_rate=0.3,
            reward_strength=1.0,
        )
        self.assertGreater(updated, 0.0)

    def test_same_seed_produces_same_simulation_path(self):
        config = SimulationConfig(
            total_bystanders=20,
            instigator_pct=25,
            defender_pct=25,
            neutral_pct=35,
            other_pct=15,
            initial_aggression=50,
            toxicity_level=60,
            profanity_level=40,
            identity_attack_level=30,
            like_influence=20,
            retweet_influence=20,
            simulation_speed=0.0,
            random_seed=1234,
            tom_influence_strength=0.5,
            learning_rate=0.3,
            reward_strength=1.0,
            memory_retention_strength=0.8,
            adaptation_speed=0.4,
            carry_learning=False,
        )
        first = simulate_scenario(config, MesaLearningState())
        second = simulate_scenario(config, MesaLearningState())
        self.assertEqual(first.bullying_history, second.bullying_history)
        self.assertEqual(first.final_outcome, second.final_outcome)

    def test_defender_dominance_reduces_low_harm_outcomes(self):
        low_defender_levels = []
        high_defender_levels = []

        for seed in range(1, 9):
            low_defender_config = SimulationConfig(
                total_bystanders=20,
                instigator_pct=60,
                defender_pct=20,
                neutral_pct=10,
                other_pct=10,
                initial_aggression=25,
                toxicity_level=0,
                profanity_level=0,
                identity_attack_level=0,
                like_influence=0,
                retweet_influence=0,
                simulation_speed=0.0,
                random_seed=seed,
                tom_influence_strength=0.5,
                learning_rate=0.3,
                reward_strength=1.0,
                memory_retention_strength=0.8,
                adaptation_speed=0.4,
                carry_learning=False,
            )
            high_defender_config = SimulationConfig(
                total_bystanders=20,
                instigator_pct=0,
                defender_pct=80,
                neutral_pct=10,
                other_pct=10,
                initial_aggression=25,
                toxicity_level=0,
                profanity_level=0,
                identity_attack_level=0,
                like_influence=0,
                retweet_influence=0,
                simulation_speed=0.0,
                random_seed=seed,
                tom_influence_strength=0.5,
                learning_rate=0.3,
                reward_strength=1.0,
                memory_retention_strength=0.8,
                adaptation_speed=0.4,
                carry_learning=False,
            )

            low_result = simulate_scenario(low_defender_config, MesaLearningState())
            high_result = simulate_scenario(high_defender_config, MesaLearningState())
            low_defender_levels.append(low_result.bullying_history[-1])
            high_defender_levels.append(high_result.bullying_history[-1])

        self.assertLess(
            sum(high_defender_levels) / len(high_defender_levels),
            sum(low_defender_levels) / len(low_defender_levels),
        )

    def test_bullying_history_stays_in_bounds(self):
        config = SimulationConfig(
            total_bystanders=16,
            instigator_pct=40,
            defender_pct=20,
            neutral_pct=30,
            other_pct=10,
            initial_aggression=55,
            toxicity_level=90,
            profanity_level=70,
            identity_attack_level=60,
            like_influence=50,
            retweet_influence=50,
            simulation_speed=0.0,
            random_seed=9,
            tom_influence_strength=0.6,
            learning_rate=0.25,
            reward_strength=1.0,
            memory_retention_strength=0.8,
            adaptation_speed=0.4,
            carry_learning=False,
        )
        result = simulate_scenario(config, MesaLearningState())
        self.assertTrue(all(0.0 <= value <= 100.0 for value in result.bullying_history))


if __name__ == "__main__":
    unittest.main()
