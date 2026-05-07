from __future__ import annotations

from pathlib import Path
import csv
import statistics
import pandas as pd

from mesa_bridge import SimulationConfig, simulate_scenario
from mesa_learning import MesaLearningState


OUTPUT_DIR = Path("manual_test_outputs")
OUTPUT_DIR.mkdir(exist_ok=True)


COLUMN_ORDER = [
    # Experiment
    "experiment",
    "test_group",
    "run",
    "scenario_note",
    "seed",

    # Inputs
    "total_bystanders",

    "instigator_count",
    "defender_count",
    "neutral_count",
    "other_count",

    "instigator_pct",
    "defender_pct",
    "neutral_pct",
    "other_pct",

    "initial_aggression",
    "toxicity_level",
    "profanity_level",
    "identity_attack_level",

    "like_influence",
    "retweet_influence",

    "social_influence",
    "tom_influence_strength",
    "learning_rate",
    "reward_strength",
    "memory_retention_strength",
    "adaptation_speed",
    "carry_learning",

    # Manual expected outputs
    "manual_got_worse",
    "manual_calmed_down",

    # Mesa outputs
    "final_outcome",
    "mesa_got_worse",
    "mesa_calmed_down",
    "final_bullying_level",
    "bullying_change",
    "steps_run",

    "support_bully_actions",
    "support_victim_actions",
    "silent_actions",
    "step_aside_actions",
]


SUMMARY_COLUMN_ORDER = [
    # Experiment
    "experiment",
    "test_group",
    "run",
    "scenario_note",
    "runs",

    # Inputs
    "total_bystanders",

    "instigator_count",
    "defender_count",
    "neutral_count",
    "other_count",

    "instigator_pct",
    "defender_pct",
    "neutral_pct",
    "other_pct",

    "initial_aggression",
    "toxicity_level",
    "profanity_level",
    "identity_attack_level",
    "like_influence",
    "retweet_influence",
    "social_influence",

    # Manual expected outputs
    "manual_got_worse",
    "manual_calmed_down",

    # Mesa summary outputs
    "got_worse",
    "calmed_down",
    "stayed_unresolved",

    "mesa_got_worse_majority",
    "mesa_calmed_down_majority",
    "got_worse_matches_manual",
    "calmed_down_matches_manual",

    "avg_final_bullying_level",
    "min_final_bullying_level",
    "max_final_bullying_level",
    "avg_bullying_change",
    "avg_steps",
]


def counts_to_percentages(
    instigator_count: int,
    defender_count: int,
    neutral_count: int,
    other_count: int,
) -> dict[str, float]:
    total = max(1, instigator_count + defender_count + neutral_count + other_count)
    return {
        "instigator_pct": (instigator_count / total) * 100,
        "defender_pct": (defender_count / total) * 100,
        "neutral_pct": (neutral_count / total) * 100,
        "other_pct": (other_count / total) * 100,
    }


def build_config(
    *,
    seed: int,
    total_bystanders: int,
    instigator_count: int,
    defender_count: int,
    neutral_count: int,
    other_count: int,
    initial_aggression: float,
    toxicity_level: float,
    profanity_level: float,
    identity_attack_level: float,
    like_influence: float,
    retweet_influence: float,
    social_influence: str,
    learning_rate: float = 0.0,
    reward_strength: float = 0.0,
    memory_retention_strength: float = 0.0,
    adaptation_speed: float = 0.0,
    carry_learning: bool = False,
    max_steps: int = 18,
) -> SimulationConfig:
    pct = counts_to_percentages(
        instigator_count=instigator_count,
        defender_count=defender_count,
        neutral_count=neutral_count,
        other_count=other_count,
    )

    social_on = social_influence.strip().lower() == "on"

    return SimulationConfig(
        total_bystanders=total_bystanders,
        instigator_pct=pct["instigator_pct"],
        defender_pct=pct["defender_pct"],
        neutral_pct=pct["neutral_pct"],
        other_pct=pct["other_pct"],
        initial_aggression=initial_aggression,
        toxicity_level=toxicity_level,
        profanity_level=profanity_level,
        identity_attack_level=identity_attack_level,
        like_influence=like_influence,
        retweet_influence=retweet_influence,
        simulation_speed=0.0,
        random_seed=seed,
        tom_influence_strength=0.55 if social_on else 0.0,
        learning_rate=learning_rate,
        reward_strength=reward_strength,
        memory_retention_strength=memory_retention_strength,
        adaptation_speed=adaptation_speed,
        carry_learning=carry_learning,
        max_steps=max_steps,
        escalation_threshold=80.0,
        calming_threshold=20.0,
    )


def manual_test_cases() -> list[dict]:
    """Manual test cases transcribed from the provided spreadsheet image."""

    return [
        # Role composition test
        {
            "test_group": "role composition test",
            "run": 1,
            "scenario_note": "supporter heavy",
            "initial_aggression": 50,
            "toxicity_level": 70,
            "profanity_level": 50,
            "identity_attack_level": 50,
            "like_influence": 30,
            "retweet_influence": 30,
            "defender_count": 4,
            "instigator_count": 10,
            "neutral_count": 6,
            "other_count": 4,
            "manual_got_worse": "yes",
            "manual_calmed_down": "no",
            "social_influence": "on",
        },
        {
            "test_group": "role composition test",
            "run": 2,
            "scenario_note": "defender heavy",
            "initial_aggression": 50,
            "toxicity_level": 70,
            "profanity_level": 50,
            "identity_attack_level": 50,
            "like_influence": 30,
            "retweet_influence": 30,
            "defender_count": 10,
            "instigator_count": 4,
            "neutral_count": 6,
            "other_count": 4,
            "manual_got_worse": "yes",
            "manual_calmed_down": "no",
            "social_influence": "on",
        },
        {
            "test_group": "role composition test",
            "run": 3,
            "scenario_note": "silent heavy",
            "initial_aggression": 50,
            "toxicity_level": 70,
            "profanity_level": 50,
            "identity_attack_level": 50,
            "like_influence": 30,
            "retweet_influence": 30,
            "defender_count": 4,
            "instigator_count": 5,
            "neutral_count": 12,
            "other_count": 4,
            "manual_got_worse": "yes",
            "manual_calmed_down": "no",
            "social_influence": "on",
        },
        {
            "test_group": "role composition test",
            "run": 4,
            "scenario_note": "balanced",
            "initial_aggression": 50,
            "toxicity_level": 70,
            "profanity_level": 50,
            "identity_attack_level": 50,
            "like_influence": 30,
            "retweet_influence": 30,
            "defender_count": 6,
            "instigator_count": 6,
            "neutral_count": 8,
            "other_count": 4,
            "manual_got_worse": "yes",
            "manual_calmed_down": "no",
            "social_influence": "on",
        },

        # Severity test
        {
            "test_group": "severity test",
            "run": 1,
            "scenario_note": "low severity",
            "initial_aggression": 50,
            "toxicity_level": 20,
            "profanity_level": 10,
            "identity_attack_level": 10,
            "like_influence": 30,
            "retweet_influence": 30,
            "defender_count": 6,
            "instigator_count": 6,
            "neutral_count": 8,
            "other_count": 4,
            "manual_got_worse": "yes",
            "manual_calmed_down": "no",
            "social_influence": "on",
        },
        {
            "test_group": "severity test",
            "run": 2,
            "scenario_note": "medium severity",
            "initial_aggression": 50,
            "toxicity_level": 50,
            "profanity_level": 40,
            "identity_attack_level": 40,
            "like_influence": 30,
            "retweet_influence": 30,
            "defender_count": 6,
            "instigator_count": 6,
            "neutral_count": 8,
            "other_count": 4,
            "manual_got_worse": "yes",
            "manual_calmed_down": "no",
            "social_influence": "on",
        },
        {
            "test_group": "severity test",
            "run": 3,
            "scenario_note": "high severity",
            "initial_aggression": 50,
            "toxicity_level": 85,
            "profanity_level": 75,
            "identity_attack_level": 80,
            "like_influence": 30,
            "retweet_influence": 30,
            "defender_count": 6,
            "instigator_count": 6,
            "neutral_count": 8,
            "other_count": 4,
            "manual_got_worse": "yes",
            "manual_calmed_down": "no",
            "social_influence": "on",
        },

        # Initial aggression test
        {
            "test_group": "initial aggression test",
            "run": 1,
            "scenario_note": "initial aggression 10",
            "initial_aggression": 10,
            "toxicity_level": 85,
            "profanity_level": 75,
            "identity_attack_level": 80,
            "like_influence": 30,
            "retweet_influence": 30,
            "defender_count": 6,
            "instigator_count": 6,
            "neutral_count": 8,
            "other_count": 4,
            "manual_got_worse": "no",
            "manual_calmed_down": "yes",
            "social_influence": "on",
        },
        {
            "test_group": "initial aggression test",
            "run": 2,
            "scenario_note": "initial aggression 11",
            "initial_aggression": 11,
            "toxicity_level": 85,
            "profanity_level": 75,
            "identity_attack_level": 80,
            "like_influence": 30,
            "retweet_influence": 30,
            "defender_count": 6,
            "instigator_count": 6,
            "neutral_count": 8,
            "other_count": 4,
            "manual_got_worse": "yes",
            "manual_calmed_down": "no",
            "social_influence": "on",
        },

        # Social amplification test
        {
            "test_group": "social amplification test",
            "run": 1,
            "scenario_note": "low amplification",
            "initial_aggression": 40,
            "toxicity_level": 40,
            "profanity_level": 40,
            "identity_attack_level": 40,
            "like_influence": 0,
            "retweet_influence": 0,
            "defender_count": 6,
            "instigator_count": 6,
            "neutral_count": 8,
            "other_count": 4,
            "manual_got_worse": "yes",
            "manual_calmed_down": "no",
            "social_influence": "on",
        },
        {
            "test_group": "social amplification test",
            "run": 2,
            "scenario_note": "medium amplification",
            "initial_aggression": 40,
            "toxicity_level": 40,
            "profanity_level": 40,
            "identity_attack_level": 40,
            "like_influence": 30,
            "retweet_influence": 30,
            "defender_count": 6,
            "instigator_count": 6,
            "neutral_count": 8,
            "other_count": 4,
            "manual_got_worse": "yes",
            "manual_calmed_down": "no",
            "social_influence": "on",
        },
        {
            "test_group": "social amplification test",
            "run": 3,
            "scenario_note": "high amplification",
            "initial_aggression": 40,
            "toxicity_level": 40,
            "profanity_level": 40,
            "identity_attack_level": 40,
            "like_influence": 80,
            "retweet_influence": 80,
            "defender_count": 6,
            "instigator_count": 6,
            "neutral_count": 8,
            "other_count": 4,
            "manual_got_worse": "yes",
            "manual_calmed_down": "no",
            "social_influence": "on",
        },
        {
            "test_group": "social amplification test",
            "run": 4,
            "scenario_note": "initial 0 medium engagement",
            "initial_aggression": 0,
            "toxicity_level": 13,
            "profanity_level": 20,
            "identity_attack_level": 10,
            "like_influence": 30,
            "retweet_influence": 30,
            "defender_count": 6,
            "instigator_count": 6,
            "neutral_count": 8,
            "other_count": 4,
            "manual_got_worse": "no",
            "manual_calmed_down": "yes",
            "social_influence": "on",
        },
        {
            "test_group": "social amplification test",
            "run": 5,
            "scenario_note": "initial 0 high engagement",
            "initial_aggression": 0,
            "toxicity_level": 13,
            "profanity_level": 20,
            "identity_attack_level": 10,
            "like_influence": 100,
            "retweet_influence": 100,
            "defender_count": 6,
            "instigator_count": 6,
            "neutral_count": 8,
            "other_count": 4,
            "manual_got_worse": "no",
            "manual_calmed_down": "yes",
            "social_influence": "on",
        },
        {
            "test_group": "social amplification test",
            "run": 6,
            "scenario_note": "initial 25 high engagement",
            "initial_aggression": 25,
            "toxicity_level": 13,
            "profanity_level": 20,
            "identity_attack_level": 10,
            "like_influence": 100,
            "retweet_influence": 100,
            "defender_count": 6,
            "instigator_count": 6,
            "neutral_count": 8,
            "other_count": 4,
            "manual_got_worse": "yes",
            "manual_calmed_down": "no",
            "social_influence": "on",
        },

        # Social influence test
        {
            "test_group": "social influence test",
            "run": 1,
            "scenario_note": "social influence on",
            "initial_aggression": 30,
            "toxicity_level": 30,
            "profanity_level": 30,
            "identity_attack_level": 30,
            "like_influence": 30,
            "retweet_influence": 30,
            "defender_count": 7,
            "instigator_count": 7,
            "neutral_count": 6,
            "other_count": 4,
            "manual_got_worse": "yes",
            "manual_calmed_down": "no",
            "social_influence": "on",
        },
        {
            "test_group": "social influence test",
            "run": 2,
            "scenario_note": "social influence off",
            "initial_aggression": 30,
            "toxicity_level": 30,
            "profanity_level": 30,
            "identity_attack_level": 30,
            "like_influence": 30,
            "retweet_influence": 30,
            "defender_count": 7,
            "instigator_count": 7,
            "neutral_count": 6,
            "other_count": 4,
            "manual_got_worse": "yes",
            "manual_calmed_down": "no",
            "social_influence": "off",
        },
        {
            "test_group": "social influence test",
            "run": 3,
            "scenario_note": "social influence on repeat",
            "initial_aggression": 30,
            "toxicity_level": 30,
            "profanity_level": 30,
            "identity_attack_level": 30,
            "like_influence": 30,
            "retweet_influence": 30,
            "defender_count": 7,
            "instigator_count": 7,
            "neutral_count": 6,
            "other_count": 4,
            "manual_got_worse": "yes",
            "manual_calmed_down": "no",
            "social_influence": "on",
        },
    ]


def prepare_test_case(raw_case: dict) -> dict:
    total_bystanders = (
        int(raw_case["instigator_count"])
        + int(raw_case["defender_count"])
        + int(raw_case["neutral_count"])
        + int(raw_case["other_count"])
    )
    pct = counts_to_percentages(
        instigator_count=int(raw_case["instigator_count"]),
        defender_count=int(raw_case["defender_count"]),
        neutral_count=int(raw_case["neutral_count"]),
        other_count=int(raw_case["other_count"]),
    )

    cleaned = raw_case.copy()
    cleaned["total_bystanders"] = total_bystanders
    cleaned["instigator_pct"] = round(pct["instigator_pct"], 2)
    cleaned["defender_pct"] = round(pct["defender_pct"], 2)
    cleaned["neutral_pct"] = round(pct["neutral_pct"], 2)
    cleaned["other_pct"] = round(pct["other_pct"], 2)
    cleaned["tom_influence_strength"] = 0.55 if cleaned["social_influence"].lower() == "on" else 0.0
    cleaned["learning_rate"] = 0.0
    cleaned["reward_strength"] = 0.0
    cleaned["memory_retention_strength"] = 0.0
    cleaned["adaptation_speed"] = 0.0
    cleaned["carry_learning"] = False
    cleaned["experiment"] = f"{cleaned['test_group']} - run {cleaned['run']}"
    return cleaned


def run_repeated_manual_test(
    raw_case: dict,
    seeds: list[int],
) -> list[dict]:
    rows: list[dict] = []
    case = prepare_test_case(raw_case)

    for seed in seeds:
        config = build_config(
            seed=seed,
            total_bystanders=case["total_bystanders"],
            instigator_count=case["instigator_count"],
            defender_count=case["defender_count"],
            neutral_count=case["neutral_count"],
            other_count=case["other_count"],
            initial_aggression=case["initial_aggression"],
            toxicity_level=case["toxicity_level"],
            profanity_level=case["profanity_level"],
            identity_attack_level=case["identity_attack_level"],
            like_influence=case["like_influence"],
            retweet_influence=case["retweet_influence"],
            social_influence=case["social_influence"],
            learning_rate=case["learning_rate"],
            reward_strength=case["reward_strength"],
            memory_retention_strength=case["memory_retention_strength"],
            adaptation_speed=case["adaptation_speed"],
            carry_learning=case["carry_learning"],
        )

        result = simulate_scenario(config, MesaLearningState())

        total_support_bully = sum(
            snap.action_counts.get("support_bully", 0) for snap in result.snapshots
        )
        total_support_victim = sum(
            snap.action_counts.get("support_victim", 0) for snap in result.snapshots
        )
        total_silent = sum(
            snap.action_counts.get("stay_silent", 0) for snap in result.snapshots
        )
        total_step_aside = sum(
            snap.action_counts.get("step_aside", 0) for snap in result.snapshots
        )

        row = {
            "experiment": case["experiment"],
            "test_group": case["test_group"],
            "run": case["run"],
            "scenario_note": case["scenario_note"],
            "seed": seed,
            "final_outcome": result.final_outcome,
            "mesa_got_worse": "yes" if result.final_outcome == "Got worse" else "no",
            "mesa_calmed_down": "yes" if result.final_outcome == "Calmed down" else "no",
            "final_bullying_level": round(result.bullying_history[-1], 2),
            "bullying_change": round(result.bullying_history[-1] - result.bullying_history[0], 2),
            "steps_run": len(result.snapshots),
            "support_bully_actions": total_support_bully,
            "support_victim_actions": total_support_victim,
            "silent_actions": total_silent,
            "step_aside_actions": total_step_aside,
            **case,
        }
        rows.append(row)

    return rows


def summarize_results(rows: list[dict]) -> dict:
    outcomes = [row["final_outcome"] for row in rows]
    final_levels = [row["final_bullying_level"] for row in rows]
    changes = [row["bullying_change"] for row in rows]
    steps = [row["steps_run"] for row in rows]

    first = rows[0] if rows else {}
    mesa_got_worse_majority = "yes" if outcomes.count("Got worse") >= len(outcomes) / 2 else "no"
    mesa_calmed_down_majority = "yes" if outcomes.count("Calmed down") >= len(outcomes) / 2 else "no"

    return {
        "experiment": first.get("experiment", "unknown"),
        "test_group": first.get("test_group"),
        "run": first.get("run"),
        "scenario_note": first.get("scenario_note"),
        "runs": len(rows),
        "total_bystanders": first.get("total_bystanders"),
        "instigator_count": first.get("instigator_count"),
        "defender_count": first.get("defender_count"),
        "neutral_count": first.get("neutral_count"),
        "other_count": first.get("other_count"),
        "instigator_pct": first.get("instigator_pct"),
        "defender_pct": first.get("defender_pct"),
        "neutral_pct": first.get("neutral_pct"),
        "other_pct": first.get("other_pct"),
        "initial_aggression": first.get("initial_aggression"),
        "toxicity_level": first.get("toxicity_level"),
        "profanity_level": first.get("profanity_level"),
        "identity_attack_level": first.get("identity_attack_level"),
        "like_influence": first.get("like_influence"),
        "retweet_influence": first.get("retweet_influence"),
        "social_influence": first.get("social_influence"),
        "manual_got_worse": first.get("manual_got_worse"),
        "manual_calmed_down": first.get("manual_calmed_down"),
        "got_worse": outcomes.count("Got worse"),
        "calmed_down": outcomes.count("Calmed down"),
        "stayed_unresolved": outcomes.count("Stayed unresolved"),
        "mesa_got_worse_majority": mesa_got_worse_majority,
        "mesa_calmed_down_majority": mesa_calmed_down_majority,
        "got_worse_matches_manual": mesa_got_worse_majority == first.get("manual_got_worse"),
        "calmed_down_matches_manual": mesa_calmed_down_majority == first.get("manual_calmed_down"),
        "avg_final_bullying_level": round(statistics.mean(final_levels), 2) if final_levels else None,
        "min_final_bullying_level": round(min(final_levels), 2) if final_levels else None,
        "max_final_bullying_level": round(max(final_levels), 2) if final_levels else None,
        "avg_bullying_change": round(statistics.mean(changes), 2) if changes else None,
        "avg_steps": round(statistics.mean(steps), 2) if steps else None,
    }


def save_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def build_column_dictionary() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"Group": "Experiment", "Column": "experiment", "Description": "Name of the manual scenario being tested."},
            {"Group": "Experiment", "Column": "test_group", "Description": "Manual test category, such as role composition or severity test."},
            {"Group": "Experiment", "Column": "run", "Description": "Run number from the manual table."},
            {"Group": "Experiment", "Column": "scenario_note", "Description": "Short plain-English note from the manual table."},
            {"Group": "Experiment", "Column": "seed", "Description": "Random seed used for reproducible repeated Mesa runs."},
            {"Group": "Inputs", "Column": "total_bystanders", "Description": "Total number of bystander agents."},
            {"Group": "Inputs", "Column": "instigator_count", "Description": "Number of bystanders supporting the bully."},
            {"Group": "Inputs", "Column": "defender_count", "Description": "Number of bystanders supporting the victim."},
            {"Group": "Inputs", "Column": "neutral_count", "Description": "Number of silent bystanders."},
            {"Group": "Inputs", "Column": "other_count", "Description": "Number of unrelated or low-impact bystanders."},
            {"Group": "Inputs", "Column": "initial_aggression", "Description": "Starting bullying level."},
            {"Group": "Inputs", "Column": "toxicity_level", "Description": "Toxicity level in the harmful situation."},
            {"Group": "Inputs", "Column": "profanity_level", "Description": "Profanity level in the harmful situation."},
            {"Group": "Inputs", "Column": "identity_attack_level", "Description": "Identity attack level in the harmful situation."},
            {"Group": "Inputs", "Column": "like_influence", "Description": "Amplification pressure from likes."},
            {"Group": "Inputs", "Column": "retweet_influence", "Description": "Amplification pressure from retweets/shares."},
            {"Group": "Inputs", "Column": "social_influence", "Description": "Whether Theory of Mind/social influence is on or off."},
            {"Group": "Manual Output", "Column": "manual_got_worse", "Description": "Manual expected got worse result from the table."},
            {"Group": "Manual Output", "Column": "manual_calmed_down", "Description": "Manual expected calmed down result from the table."},
            {"Group": "Mesa Output", "Column": "final_outcome", "Description": "Mesa result: Got worse, Calmed down, or Stayed unresolved."},
            {"Group": "Mesa Output", "Column": "final_bullying_level", "Description": "Final bullying level at the end of the Mesa run."},
            {"Group": "Mesa Output", "Column": "bullying_change", "Description": "Final bullying level minus starting bullying level."},
            {"Group": "Mesa Output", "Column": "steps_run", "Description": "Number of Mesa steps completed before stopping."},
            {"Group": "Mesa Output", "Column": "support_bully_actions", "Description": "Total actions supporting the bully."},
            {"Group": "Mesa Output", "Column": "support_victim_actions", "Description": "Total actions supporting the victim."},
            {"Group": "Mesa Output", "Column": "silent_actions", "Description": "Total actions staying silent."},
            {"Group": "Mesa Output", "Column": "step_aside_actions", "Description": "Total unrelated/step aside actions."},
            {"Group": "Comparison", "Column": "got_worse_matches_manual", "Description": "Whether Mesa majority result matched manual got worse value."},
            {"Group": "Comparison", "Column": "calmed_down_matches_manual", "Description": "Whether Mesa majority result matched manual calmed down value."},
        ]
    )


def save_excel_with_dictionary(
    detailed_rows: list[dict],
    summary_rows: list[dict],
    output_path: Path,
) -> None:
    detailed_df = pd.DataFrame(detailed_rows)
    detailed_df = detailed_df[COLUMN_ORDER]

    summary_df = pd.DataFrame(summary_rows)
    summary_df = summary_df[SUMMARY_COLUMN_ORDER]

    manual_df = pd.DataFrame([prepare_test_case(case) for case in manual_test_cases()])
    manual_columns = [
        "test_group",
        "run",
        "scenario_note",
        "initial_aggression",
        "toxicity_level",
        "profanity_level",
        "identity_attack_level",
        "like_influence",
        "retweet_influence",
        "defender_count",
        "instigator_count",
        "neutral_count",
        "other_count",
        "manual_got_worse",
        "manual_calmed_down",
        "social_influence",
    ]
    manual_df = manual_df[manual_columns]

    dictionary_df = build_column_dictionary()

    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
        manual_df.to_excel(writer, sheet_name="manual_test_cases", index=False)
        detailed_df.to_excel(writer, sheet_name="detailed_runs", index=False)
        summary_df.to_excel(writer, sheet_name="summary_results", index=False)
        dictionary_df.to_excel(writer, sheet_name="column_dictionary", index=False)


def print_summary(summary_rows: list[dict]) -> None:
    print("\n=== MANUAL TEST SUMMARY ===")
    for row in summary_rows:
        print(
            f"{row['experiment']}: "
            f"runs={row['runs']}, "
            f"got_worse={row['got_worse']}, "
            f"calmed_down={row['calmed_down']}, "
            f"stayed_unresolved={row['stayed_unresolved']}, "
            f"avg_final={row['avg_final_bullying_level']}, "
            f"manual_got_worse={row['manual_got_worse']}, "
            f"mesa_majority={row['mesa_got_worse_majority']}"
        )


def main() -> None:
    all_rows: list[dict] = []
    summary_rows: list[dict] = []

    base_seeds = list(range(1, 11))

    for raw_case in manual_test_cases():
        rows = run_repeated_manual_test(raw_case, base_seeds)
        all_rows.extend(rows)
        summary_rows.append(summarize_results(rows))

    save_csv(
        path=OUTPUT_DIR / "manual_test_detailed_runs.csv",
        rows=all_rows,
        fieldnames=COLUMN_ORDER,
    )
    save_csv(
        path=OUTPUT_DIR / "manual_test_summary_results.csv",
        rows=summary_rows,
        fieldnames=SUMMARY_COLUMN_ORDER,
    )
    save_excel_with_dictionary(
        detailed_rows=all_rows,
        summary_rows=summary_rows,
        output_path=OUTPUT_DIR / "manual_test_results.xlsx",
    )

    print_summary(summary_rows)
    print(f"\nSaved outputs to: {OUTPUT_DIR.resolve()}")


if __name__ == "__main__":
    main()
