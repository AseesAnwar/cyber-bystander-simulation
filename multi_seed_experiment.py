"""Repeat a canonical Mesa scenario across many random seeds.

This module turns a single stochastic simulation into a small sensitivity experiment.
It reports outcome frequencies and the distribution of final bullying intensity.
"""

from __future__ import annotations

import argparse
from dataclasses import replace
from pathlib import Path

import pandas as pd

from mesa_bridge import SimulationConfig, simulate_scenario
from mesa_learning import MesaLearningState


def run_multi_seed_experiment(
    config: SimulationConfig,
    *,
    runs: int = 100,
    start_seed: int = 1,
) -> tuple[pd.DataFrame, dict[str, float]]:
    if runs < 1:
        raise ValueError("runs must be at least 1")

    rows: list[dict[str, object]] = []
    for offset in range(runs):
        seed = start_seed + offset
        seeded_config = replace(config, random_seed=seed, carry_learning=False)
        result = simulate_scenario(seeded_config, MesaLearningState())
        rows.append(
            {
                "seed": seed,
                "final_outcome": result.final_outcome,
                "final_bullying_level": float(result.bullying_history[-1]),
                "steps": len(result.snapshots),
            }
        )

    frame = pd.DataFrame(rows)
    outcome_share = frame["final_outcome"].value_counts(normalize=True)

    summary = {
        "runs": float(runs),
        "mean_final_bullying": float(frame["final_bullying_level"].mean()),
        "std_final_bullying": float(frame["final_bullying_level"].std(ddof=1))
        if runs > 1
        else 0.0,
        "escalation_rate": float(outcome_share.get("Got worse", 0.0)),
        "calming_rate": float(outcome_share.get("Calmed down", 0.0)),
        "unresolved_rate": float(outcome_share.get("Stayed unresolved", 0.0)),
    }
    return frame, summary


def default_config() -> SimulationConfig:
    return SimulationConfig(
        total_bystanders=24,
        instigator_pct=25,
        defender_pct=30,
        neutral_pct=35,
        other_pct=10,
        initial_aggression=50,
        toxicity_level=60,
        profanity_level=35,
        identity_attack_level=35,
        like_influence=20,
        retweet_influence=20,
        simulation_speed=0.0,
        random_seed=1,
        tom_influence_strength=0.5,
        learning_rate=0.3,
        reward_strength=1.0,
        memory_retention_strength=0.8,
        adaptation_speed=0.4,
        carry_learning=False,
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run one cyber-bystander scenario across multiple random seeds."
    )
    parser.add_argument("--runs", type=int, default=100)
    parser.add_argument("--start-seed", type=int, default=1)
    parser.add_argument("--output", default="outputs/multi_seed_results.csv")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    frame, summary = run_multi_seed_experiment(
        default_config(),
        runs=args.runs,
        start_seed=args.start_seed,
    )

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(output_path, index=False)

    print("Multi-seed sensitivity summary")
    print("------------------------------")
    for key, value in summary.items():
        print(f"{key}: {value:.4f}")
    print(f"Saved run-level results to {output_path}")


if __name__ == "__main__":
    main()
