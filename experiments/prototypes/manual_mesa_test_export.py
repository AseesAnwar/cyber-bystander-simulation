"""Run manually specified Mesa cyber-bystander tests and export Excel results.

This script reproduces the manual test cases shown in the spreadsheet-style
table and runs them through the current Mesa backend.

How to run:
    python3 manual_mesa_test_export.py

Output:
    manual_mesa_test_results.xlsx

The Excel workbook contains:
    - manual_test_cases: the input scenarios copied from the manual table
    - mesa_run_results: one row per repeated Mesa run
    - mesa_summary: averaged results per test case
    - manual_vs_mesa: comparison between manual expected outcomes and Mesa output
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path

import pandas as pd

from mesa_bridge import SimulationConfig, simulate_scenario
from mesa_learning import MesaLearningState


OUTPUT_FILE = Path("manual_mesa_test_results.xlsx")


@dataclass(frozen=True)
class ManualTestCase:
    test_group: str
    run: int
    initial_aggression: float
    toxicity_level: float
    profanity_level: float
    identity_attack_level: float
    like_influence: float
    retweet_influence: float
    defender_count: int
    instigator_count: int
    neutral_count: int
    other_count: int
    manual_got_worse: str
    manual_calmed_down: str
    social_influence: str
    scenario_note: str

    @property
    def total_bystanders(self) -> int:
        return self.defender_count + self.instigator_count + self.neutral_count + self.other_count

    def to_config(self, seed: int) -> SimulationConfig:
        """Convert role counts into percentages expected by the Mesa bridge."""

        total = max(1, self.total_bystanders)
        social_on = self.social_influence.strip().lower() == "on"

        return SimulationConfig(
            total_bystanders=total,
            instigator_pct=100 * self.instigator_count / total,
            defender_pct=100 * self.defender_count / total,
            neutral_pct=100 * self.neutral_count / total,
            other_pct=100 * self.other_count / total,
            initial_aggression=self.initial_aggression,
            toxicity_level=self.toxicity_level,
            profanity_level=self.profanity_level,
            identity_attack_level=self.identity_attack_level,
            like_influence=self.like_influence,
            retweet_influence=self.retweet_influence,
            simulation_speed=0.5,
            random_seed=seed,
            tom_influence_strength=0.55 if social_on else 0.0,
            learning_rate=0.0,
            reward_strength=0.0,
            memory_retention_strength=0.0,
            adaptation_speed=0.0,
            carry_learning=False,
            max_steps=18,
        )


TEST_CASES: list[ManualTestCase] = [
    # Role composition test
    ManualTestCase("role composition test", 1, 50, 70, 50, 50, 30, 30, 4, 10, 6, 4, "yes", "no", "on", "supporter heavy"),
    ManualTestCase("role composition test", 2, 50, 70, 50, 50, 30, 30, 10, 4, 6, 4, "yes", "no", "on", "defender heavy"),
    ManualTestCase("role composition test", 3, 50, 70, 50, 50, 30, 30, 4, 5, 12, 4, "yes", "no", "on", "silent heavy"),
    ManualTestCase("role composition test", 4, 50, 70, 50, 50, 30, 30, 6, 6, 8, 4, "yes", "no", "on", "balanced"),

    # Severity test
    ManualTestCase("severity test", 1, 50, 20, 10, 10, 30, 30, 6, 6, 8, 4, "yes", "no", "on", "low severity"),
    ManualTestCase("severity test", 2, 50, 50, 40, 40, 30, 30, 6, 6, 8, 4, "yes", "no", "on", "medium severity"),
    ManualTestCase("severity test", 3, 50, 85, 75, 80, 30, 30, 6, 6, 8, 4, "yes", "no", "on", "high severity"),

    # Initial aggression test
    ManualTestCase("initial aggression test", 1, 10, 85, 75, 80, 30, 30, 6, 6, 8, 4, "no", "yes", "on", "initial aggression low"),
    ManualTestCase("initial aggression test", 2, 11, 85, 75, 80, 30, 30, 6, 6, 8, 4, "yes", "no", "on", "initial aggression slightly higher"),

    # Social amplification test
    ManualTestCase("social amplification test", 1, 40, 40, 40, 40, 0, 0, 6, 6, 8, 4, "yes", "no", "on", "low amplification"),
    ManualTestCase("social amplification test", 2, 40, 40, 40, 40, 30, 30, 6, 6, 8, 4, "yes", "no", "on", "medium amplification"),
    ManualTestCase("social amplification test", 3, 40, 40, 40, 40, 80, 80, 6, 6, 8, 4, "yes", "no", "on", "high amplification"),
    ManualTestCase("social amplification test", 4, 0, 13, 20, 10, 30, 30, 6, 6, 8, 4, "no", "yes", "on", "very low starting aggression"),
    ManualTestCase("social amplification test", 5, 0, 13, 20, 10, 100, 100, 6, 6, 8, 4, "no", "yes", "on", "very low aggression with high engagement"),
    ManualTestCase("social amplification test", 6, 25, 13, 20, 10, 100, 100, 6, 6, 8, 4, "yes", "no", "on", "higher aggression with high engagement"),

    # Social influence test
    ManualTestCase("social influence test", 1, 30, 30, 30, 30, 30, 30, 7, 7, 6, 4, "yes", "no", "on", "social influence on"),
    ManualTestCase("social influence test", 2, 30, 30, 30, 30, 30, 30, 7, 7, 6, 4, "yes", "no", "off", "social influence off"),
    ManualTestCase("social influence test", 3, 30, 30, 30, 30, 30, 30, 7, 7, 6, 4, "yes", "no", "on", "social influence on repeat"),
]


def manual_rows() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for case in TEST_CASES:
        row = asdict(case)
        row["total_bystanders"] = case.total_bystanders
        row["defender_pct"] = round(100 * case.defender_count / case.total_bystanders, 2)
        row["instigator_pct"] = round(100 * case.instigator_count / case.total_bystanders, 2)
        row["neutral_pct"] = round(100 * case.neutral_count / case.total_bystanders, 2)
        row["other_pct"] = round(100 * case.other_count / case.total_bystanders, 2)
        rows.append(row)
    return rows


def run_tests(repeats_per_case: int = 30, seed_start: int = 1200) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Run repeated Mesa simulations for each manual test case."""

    run_rows: list[dict[str, object]] = []

    for case_index, case in enumerate(TEST_CASES, start=1):
        for repeat in range(1, repeats_per_case + 1):
            seed = seed_start + case_index * 100 + repeat
            result = simulate_scenario(case.to_config(seed), MesaLearningState())
            history = result.bullying_history

            total_actions = {"support_bully": 0, "support_victim": 0, "stay_silent": 0, "step_aside": 0}
            for snapshot in result.snapshots:
                for action, count in snapshot.action_counts.items():
                    total_actions[action] += count
            action_total = max(1, sum(total_actions.values()))

            run_rows.append(
                {
                    "test_group": case.test_group,
                    "run": case.run,
                    "repeat": repeat,
                    "seed": seed,
                    "scenario_note": case.scenario_note,
                    "social_influence": case.social_influence,
                    "initial_aggression": case.initial_aggression,
                    "toxicity_level": case.toxicity_level,
                    "profanity_level": case.profanity_level,
                    "identity_attack_level": case.identity_attack_level,
                    "like_influence": case.like_influence,
                    "retweet_influence": case.retweet_influence,
                    "defender_count": case.defender_count,
                    "instigator_count": case.instigator_count,
                    "neutral_count": case.neutral_count,
                    "other_count": case.other_count,
                    "total_bystanders": case.total_bystanders,
                    "manual_got_worse": case.manual_got_worse,
                    "manual_calmed_down": case.manual_calmed_down,
                    "mesa_outcome": result.final_outcome,
                    "mesa_got_worse": "yes" if result.final_outcome == "Got worse" else "no",
                    "mesa_calmed_down": "yes" if result.final_outcome == "Calmed down" else "no",
                    "initial_level": history[0],
                    "final_level": history[-1],
                    "change": history[-1] - history[0],
                    "steps": len(history) - 1,
                    "support_bully_share": total_actions["support_bully"] / action_total,
                    "support_victim_share": total_actions["support_victim"] / action_total,
                    "stay_silent_share": total_actions["stay_silent"] / action_total,
                    "step_aside_share": total_actions["step_aside"] / action_total,
                    "bullying_history": " | ".join(f"{value:.2f}" for value in history),
                }
            )

    runs_df = pd.DataFrame(run_rows)

    group_cols = ["test_group", "run", "scenario_note"]
    summary_df = (
        runs_df.groupby(group_cols, as_index=False)
        .agg(
            repeats=("repeat", "count"),
            initial_aggression=("initial_aggression", "first"),
            toxicity_level=("toxicity_level", "first"),
            profanity_level=("profanity_level", "first"),
            identity_attack_level=("identity_attack_level", "first"),
            like_influence=("like_influence", "first"),
            retweet_influence=("retweet_influence", "first"),
            defender_count=("defender_count", "first"),
            instigator_count=("instigator_count", "first"),
            neutral_count=("neutral_count", "first"),
            other_count=("other_count", "first"),
            social_influence=("social_influence", "first"),
            manual_got_worse=("manual_got_worse", "first"),
            manual_calmed_down=("manual_calmed_down", "first"),
            mean_final_level=("final_level", "mean"),
            mean_change=("change", "mean"),
            mean_steps=("steps", "mean"),
            got_worse_rate=("mesa_got_worse", lambda values: (values == "yes").mean()),
            calmed_down_rate=("mesa_calmed_down", lambda values: (values == "yes").mean()),
            support_bully_share=("support_bully_share", "mean"),
            support_victim_share=("support_victim_share", "mean"),
            stay_silent_share=("stay_silent_share", "mean"),
            step_aside_share=("step_aside_share", "mean"),
        )
        .sort_values(group_cols)
    )

    comparison_df = summary_df.copy()
    comparison_df["mesa_got_worse_majority"] = comparison_df["got_worse_rate"].apply(lambda value: "yes" if value >= 0.5 else "no")
    comparison_df["mesa_calmed_down_majority"] = comparison_df["calmed_down_rate"].apply(lambda value: "yes" if value >= 0.5 else "no")
    comparison_df["got_worse_matches_manual"] = comparison_df["mesa_got_worse_majority"] == comparison_df["manual_got_worse"]
    comparison_df["calmed_down_matches_manual"] = comparison_df["mesa_calmed_down_majority"] == comparison_df["manual_calmed_down"]

    return runs_df, summary_df, comparison_df


def write_excel() -> None:
    manual_df = pd.DataFrame(manual_rows())
    runs_df, summary_df, comparison_df = run_tests()

    with pd.ExcelWriter(OUTPUT_FILE, engine="openpyxl") as writer:
        manual_df.to_excel(writer, sheet_name="manual_test_cases", index=False)
        runs_df.to_excel(writer, sheet_name="mesa_run_results", index=False)
        summary_df.to_excel(writer, sheet_name="mesa_summary", index=False)
        comparison_df.to_excel(writer, sheet_name="manual_vs_mesa", index=False)

        readme_df = pd.DataFrame(
            [
                {
                    "sheet": "manual_test_cases",
                    "description": "Manual test cases transcribed from the provided table.",
                },
                {
                    "sheet": "mesa_run_results",
                    "description": "One row per repeated Mesa run. Default is 30 repeats per manual test case.",
                },
                {
                    "sheet": "mesa_summary",
                    "description": "Average Mesa results for each manual test case.",
                },
                {
                    "sheet": "manual_vs_mesa",
                    "description": "Compares manual yes/no outcomes with Mesa majority outcomes.",
                },
            ]
        )
        readme_df.to_excel(writer, sheet_name="README", index=False)

    print(f"Wrote Excel workbook: {OUTPUT_FILE.resolve()}")


if __name__ == "__main__":
    write_excel()
