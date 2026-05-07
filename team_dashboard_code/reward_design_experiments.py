"""Reward-design experiments for the Mesa cyber-bystander simulation.

This script explores one important scientific question:

    How does the reward system affect what bystander agents learn?

It intentionally does not change the dashboard or the core simulation files.
Instead, it temporarily swaps the reward function used by the Mesa model and
runs repeated simulations under different reward designs.

Run:
    python3 reward_design_experiments.py

Outputs are written to:
    sensitivity_outputs/reward_design_experiments/
"""

from __future__ import annotations

import csv
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

import numpy as np

import mesa_model
from mesa_bridge import SimulationConfig, simulate_scenario
from mesa_learning import MesaLearningState


RewardFunction = Callable[[str, str, float], float]


OUTPUT_DIR = Path("sensitivity_outputs/reward_design_experiments")


@dataclass(frozen=True)
class RewardDesign:
    """A named reward system used for comparison."""

    name: str
    plain_english_goal: str
    reward_function: RewardFunction


BASE_CONFIG = {
    "total_bystanders": 24,
    "instigator_pct": 25.0,
    "defender_pct": 35.0,
    "neutral_pct": 30.0,
    "other_pct": 10.0,
    "initial_aggression": 38.0,
    "toxicity_level": 10.0,
    "profanity_level": 5.0,
    "identity_attack_level": 6.0,
    "like_influence": 10.0,
    "retweet_influence": 10.0,
    "simulation_speed": 0.5,
    "tom_influence_strength": 0.55,
    "learning_rate": 0.30,
    "reward_strength": 0.90,
    "memory_retention_strength": 0.80,
    "adaptation_speed": 0.35,
    "carry_learning": True,
    "max_steps": 18,
}


SCENARIOS = {
    "low_risk_defended": {
        "initial_aggression": 38.0,
        "toxicity_level": 5.0,
        "profanity_level": 2.5,
        "identity_attack_level": 3.0,
        "like_influence": 5.0,
        "retweet_influence": 5.0,
        "instigator_pct": 15.0,
        "defender_pct": 60.0,
        "neutral_pct": 20.0,
        "other_pct": 5.0,
    },
    "medium_tipping_point": {
        "initial_aggression": 38.0,
        "toxicity_level": 15.0,
        "profanity_level": 7.5,
        "identity_attack_level": 9.0,
        "like_influence": 15.0,
        "retweet_influence": 15.0,
        "instigator_pct": 5.0,
        "defender_pct": 70.0,
        "neutral_pct": 20.0,
        "other_pct": 5.0,
    },
    "high_risk_pressure": {
        "initial_aggression": 55.0,
        "toxicity_level": 50.0,
        "profanity_level": 35.0,
        "identity_attack_level": 45.0,
        "like_influence": 50.0,
        "retweet_influence": 50.0,
        "instigator_pct": 25.0,
        "defender_pct": 35.0,
        "neutral_pct": 30.0,
        "other_pct": 10.0,
    },
}


def role_based_reward(role: str, action: str, bullying_change: float) -> float:
    """Current model logic: each role learns according to its role goal."""

    if role == "instigator":
        if action == "support_bully":
            return 1.0 if bullying_change > 0 else -0.8
        return 0.2 if bullying_change > 0 else -0.3

    if role == "defender":
        if action == "support_victim":
            return 1.0 if bullying_change < 0 else -0.8
        return 0.2 if bullying_change < 0 else -0.3

    if role == "neutral":
        if action == "stay_silent":
            return -0.7 if bullying_change > 0 else 0.1
        if action == "support_victim":
            return 0.6 if bullying_change < 0 else -0.2
        return 0.0

    if action == "step_aside":
        return 0.1 if abs(bullying_change) < 2 else -0.1
    return 0.0


def victim_safety_reward(role: str, action: str, bullying_change: float) -> float:
    """All agents are rewarded for reducing harm, not for role self-interest."""

    if bullying_change < -1.0:
        base = 1.0
    elif bullying_change < 0:
        base = 0.6
    elif bullying_change > 4.0:
        base = -1.0
    elif bullying_change > 0:
        base = -0.6
    else:
        base = 0.1

    if action == "support_victim":
        return base + 0.35
    if action == "support_bully":
        return base - 0.45
    if action == "stay_silent":
        return base - (0.25 if bullying_change > 0 else 0.0)
    return base - 0.05


def mixed_ethical_reward(role: str, action: str, bullying_change: float) -> float:
    """Agents keep role identity, but escalation is penalised for everyone."""

    role_reward = role_based_reward(role, action, bullying_change)

    if bullying_change > 4.0:
        global_safety_adjustment = -0.9
    elif bullying_change > 0:
        global_safety_adjustment = -0.45
    elif bullying_change < -1.0:
        global_safety_adjustment = 0.7
    elif bullying_change < 0:
        global_safety_adjustment = 0.35
    else:
        global_safety_adjustment = 0.0

    if action == "support_victim":
        prosocial_bonus = 0.25
    elif action == "support_bully":
        prosocial_bonus = -0.35
    elif action == "stay_silent" and bullying_change > 0:
        prosocial_bonus = -0.20
    else:
        prosocial_bonus = 0.0

    return 0.45 * role_reward + global_safety_adjustment + prosocial_bonus


REWARD_DESIGNS = [
    RewardDesign(
        name="role_based",
        plain_english_goal="Agents learn according to their role. Instigators are rewarded when escalation succeeds.",
        reward_function=role_based_reward,
    ),
    RewardDesign(
        name="victim_safety",
        plain_english_goal="All agents are rewarded when harm decreases and penalised when bullying increases.",
        reward_function=victim_safety_reward,
    ),
    RewardDesign(
        name="mixed_ethical",
        plain_english_goal="Agents keep role tendencies, but everyone is discouraged from severe escalation.",
        reward_function=mixed_ethical_reward,
    ),
]


def build_config(overrides: dict[str, float], seed: int) -> SimulationConfig:
    params = BASE_CONFIG.copy()
    params.update(overrides)
    params["random_seed"] = seed
    return SimulationConfig(**params)


def run_one_design(
    reward_design: RewardDesign,
    scenario_name: str,
    scenario_overrides: dict[str, float],
    repeated_runs: int,
    starting_seed: int,
) -> tuple[list[dict[str, object]], dict[str, object]]:
    """Run one reward design over repeated simulations with memory carried over."""

    original_reward = mesa_model.reward_for_action
    mesa_model.reward_for_action = reward_design.reward_function

    learning_state = MesaLearningState()
    rows: list[dict[str, object]] = []

    try:
        for run_index in range(1, repeated_runs + 1):
            seed = starting_seed + run_index
            result = simulate_scenario(
                build_config(scenario_overrides, seed),
                learning_state,
            )
            learning_state = result.updated_learning_state
            latest_memory = learning_state.run_history[-1]
            initial_level = result.bullying_history[0]
            final_level = result.bullying_history[-1]

            rows.append(
                {
                    "reward_design": reward_design.name,
                    "reward_goal": reward_design.plain_english_goal,
                    "scenario": scenario_name,
                    "run_number": run_index,
                    "seed": seed,
                    "initial_level": initial_level,
                    "final_level": final_level,
                    "change": final_level - initial_level,
                    "steps": len(result.bullying_history) - 1,
                    "outcome": result.final_outcome,
                    "defender_tendency": latest_memory.defender_tendency,
                    "bully_support_tendency": latest_memory.bully_support_tendency,
                    "silent_tendency": latest_memory.silent_tendency,
                    "defender_action_share": latest_memory.defender_action_share,
                    "bully_support_action_share": latest_memory.bully_support_action_share,
                    "silent_action_share": latest_memory.silent_action_share,
                }
            )
    finally:
        mesa_model.reward_for_action = original_reward

    summary = summarize_rows(rows, reward_design, scenario_name)
    return rows, summary


def summarize_rows(
    rows: list[dict[str, object]],
    reward_design: RewardDesign,
    scenario_name: str,
) -> dict[str, object]:
    """Summarise repeated-run behaviour for one reward design."""

    first = rows[0]
    last = rows[-1]
    outcomes = [row["outcome"] for row in rows]
    return {
        "reward_design": reward_design.name,
        "reward_goal": reward_design.plain_english_goal,
        "scenario": scenario_name,
        "runs": len(rows),
        "mean_final_level": float(np.mean([row["final_level"] for row in rows])),
        "mean_change": float(np.mean([row["change"] for row in rows])),
        "got_worse_rate": outcomes.count("Got worse") / len(outcomes),
        "calmed_down_rate": outcomes.count("Calmed down") / len(outcomes),
        "unresolved_rate": outcomes.count("Stayed unresolved") / len(outcomes),
        "first_run_final_level": first["final_level"],
        "last_run_final_level": last["final_level"],
        "first_defender_tendency": first["defender_tendency"],
        "last_defender_tendency": last["defender_tendency"],
        "first_bully_support_tendency": first["bully_support_tendency"],
        "last_bully_support_tendency": last["bully_support_tendency"],
        "first_silent_tendency": first["silent_tendency"],
        "last_silent_tendency": last["silent_tendency"],
        "mean_defender_action_share": float(np.mean([row["defender_action_share"] for row in rows])),
        "mean_bully_support_action_share": float(np.mean([row["bully_support_action_share"] for row in rows])),
        "mean_silent_action_share": float(np.mean([row["silent_action_share"] for row in rows])),
    }


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        return
    with path.open("w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    all_rows: list[dict[str, object]] = []
    all_summaries: list[dict[str, object]] = []
    repeated_runs = 40

    for scenario_index, (scenario_name, scenario_overrides) in enumerate(SCENARIOS.items()):
        for design_index, reward_design in enumerate(REWARD_DESIGNS):
            rows, summary = run_one_design(
                reward_design=reward_design,
                scenario_name=scenario_name,
                scenario_overrides=scenario_overrides,
                repeated_runs=repeated_runs,
                starting_seed=900 + scenario_index * 100 + design_index * 1000,
            )
            all_rows.extend(rows)
            all_summaries.append(summary)

    write_csv(OUTPUT_DIR / "reward_design_run_level_results.csv", all_rows)
    write_csv(OUTPUT_DIR / "reward_design_summary.csv", all_summaries)

    print(f"Wrote reward-design outputs to {OUTPUT_DIR.resolve()}")
    print()
    for row in all_summaries:
        print(
            f"{row['scenario']} | {row['reward_design']}: "
            f"mean_final={row['mean_final_level']:.1f}, "
            f"worse={row['got_worse_rate']:.0%}, "
            f"calm={row['calmed_down_rate']:.0%}, "
            f"bully_tendency {row['first_bully_support_tendency']:.2f}->{row['last_bully_support_tendency']:.2f}, "
            f"defender_tendency {row['first_defender_tendency']:.2f}->{row['last_defender_tendency']:.2f}"
        )


if __name__ == "__main__":
    main()
