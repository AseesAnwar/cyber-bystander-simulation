from __future__ import annotations

import argparse
import os
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib")

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from model import simulate_thread
from preprocess_cyby23 import (
    DEFAULT_DATASET_PATH,
    NORMALIZED_ROLE_ORDER,
    build_thread_records,
    clean_dataset,
    load_raw_dataset,
    make_summary_lines,
    preprocessing_summary,
    resolve_dataset_path,
)


def run_across_threads(
    dataset_path: str | Path,
    scenario_mode: str = "all",
    max_threads: int | None = None,
    seed: int = 7,
    learning_mode: bool = False,
) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, object], Path]:
    resolved_path = resolve_dataset_path(dataset_path)
    raw_df = load_raw_dataset(resolved_path)
    cleaned_df = clean_dataset(raw_df)
    summary = preprocessing_summary(cleaned_df)
    thread_records = build_thread_records(cleaned_df)

    if scenario_mode != "all":
        thread_records = [record for record in thread_records if record.risk_level == scenario_mode]

    if max_threads is not None:
        thread_records = thread_records[:max_threads]

    if not thread_records:
        raise ValueError(f"No threads available for scenario mode '{scenario_mode}'.")

    result_rows: list[dict[str, object]] = []
    action_rows: list[pd.DataFrame] = []
    learner_registry: dict[str, object] = {}

    for index, thread_record in enumerate(thread_records):
        model, result = simulate_thread(
            thread_record,
            seed=seed + index,
            learning_mode=learning_mode,
            learner_registry=learner_registry,
        )
        row: dict[str, object] = {
            "thread_id": result.thread_id,
            "risk_level": result.risk_level,
            "source_toxicity": result.source_toxicity,
            "escalation_score": result.escalation_score,
            "defence_score": result.defence_score,
            "moderator_triggered": result.moderator_triggered,
            "accuracy": result.accuracy,
            "bystander_count": len(thread_record.bystanders),
            "learning_mode": learning_mode,
            "mean_reward": result.mean_reward,
        }
        for role in NORMALIZED_ROLE_ORDER:
            row[f"observed_{role}"] = result.observed_counts.get(role, 0)
            row[f"simulated_{role}"] = result.simulated_counts.get(role, 0)
            row[f"avg_q_{role}"] = result.average_q_values.get(role, 0.0)
        result_rows.append(row)

        history = model.get_action_history_frame()
        if not history.empty:
            action_rows.append(history)

    results_df = pd.DataFrame(result_rows)
    actions_df = pd.concat(action_rows, ignore_index=True) if action_rows else pd.DataFrame()
    summary["scenario_mode"] = scenario_mode
    summary["simulated_threads"] = int(results_df.shape[0])
    summary["mean_accuracy"] = round(float(results_df["accuracy"].mean()), 4)
    summary["mean_escalation_score"] = round(float(results_df["escalation_score"].mean()), 4)
    summary["mean_defence_score"] = round(float(results_df["defence_score"].mean()), 4)
    summary["learning_mode"] = learning_mode
    summary["mean_reward"] = round(float(results_df["mean_reward"].mean()), 4)
    return results_df, actions_df, summary, resolved_path


def build_distribution_comparison(results_df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for role in NORMALIZED_ROLE_ORDER:
        observed = int(results_df[f"observed_{role}"].sum())
        simulated = int(results_df[f"simulated_{role}"].sum())
        rows.append({"role": role, "observed": observed, "simulated": simulated})
    comparison_df = pd.DataFrame(rows)
    total_observed = max(1, comparison_df["observed"].sum())
    total_simulated = max(1, comparison_df["simulated"].sum())
    comparison_df["observed_share"] = comparison_df["observed"] / total_observed
    comparison_df["simulated_share"] = comparison_df["simulated"] / total_simulated
    return comparison_df


def build_confusion_style_table(actions_df: pd.DataFrame) -> pd.DataFrame:
    if actions_df.empty:
        return pd.DataFrame(index=NORMALIZED_ROLE_ORDER, columns=NORMALIZED_ROLE_ORDER).fillna(0)
    table = pd.crosstab(
        actions_df["observed_role"],
        actions_df["simulated_role"],
        dropna=False,
    )
    table = table.reindex(index=NORMALIZED_ROLE_ORDER, columns=NORMALIZED_ROLE_ORDER, fill_value=0)
    return table


def print_metrics(results_df: pd.DataFrame, comparison_df: pd.DataFrame, confusion_df: pd.DataFrame) -> None:
    total_simulated = int(sum(comparison_df["simulated"]))
    print("Simulation metrics")
    print("------------------")
    print(f"Threads simulated: {len(results_df)}")
    print(f"Mean thread accuracy: {results_df['accuracy'].mean():.3f}")
    print(f"Mean escalation score: {results_df['escalation_score'].mean():.3f}")
    print(f"Mean defence score: {results_df['defence_score'].mean():.3f}")
    print(f"Mean reward: {results_df['mean_reward'].mean():.3f}")
    print(f"Moderator triggered share: {results_df['moderator_triggered'].mean():.3f}")
    print()
    print("Simulated action counts and proportions")
    for _, row in comparison_df.iterrows():
        proportion = row["simulated"] / max(1, total_simulated)
        print(f"  {row['role']}: {int(row['simulated'])} ({proportion:.3f})")
    print()
    print("Observed vs simulated role totals")
    print(comparison_df.to_string(index=False))
    print()
    print("Confusion-style comparison")
    print(confusion_df.to_string())


def save_plots(results_df: pd.DataFrame, comparison_df: pd.DataFrame, output_dir: str | Path) -> None:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    x = range(len(comparison_df))
    width = 0.36
    axes[0].bar(
        [value - width / 2 for value in x],
        comparison_df["observed"],
        width=width,
        label="Observed",
        color="#4f46e5",
    )
    axes[0].bar(
        [value + width / 2 for value in x],
        comparison_df["simulated"],
        width=width,
        label="Simulated",
        color="#f97316",
    )
    axes[0].set_xticks(list(x))
    axes[0].set_xticklabels(comparison_df["role"])
    axes[0].set_title("Observed vs Simulated Bystander Roles")
    axes[0].set_ylabel("Reply count")
    axes[0].legend()

    axes[1].scatter(
        results_df["source_toxicity"],
        results_df["escalation_score"],
        c=results_df["defence_score"],
        cmap="viridis",
        edgecolor="black",
        alpha=0.8,
    )
    axes[1].set_title("Thread Toxicity vs Escalation")
    axes[1].set_xlabel("Source toxicity")
    axes[1].set_ylabel("Escalation score")

    fig.tight_layout()
    fig.savefig(output_path / "simulation_summary.png", dpi=180)
    plt.close(fig)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the CYBY23 Mesa cyber-bystander simulation.")
    parser.add_argument(
        "--dataset-path",
        default=DEFAULT_DATASET_PATH,
        help="Path to the CYBY23 Excel dataset.",
    )
    parser.add_argument(
        "--scenario-mode",
        choices=["all", "low", "medium", "high"],
        default="all",
        help="Run all threads or only one risk slice.",
    )
    parser.add_argument(
        "--max-threads",
        type=int,
        default=None,
        help="Optional cap on how many threads to simulate.",
    )
    parser.add_argument("--seed", type=int, default=7, help="Base random seed.")
    parser.add_argument(
        "--learning-mode",
        action="store_true",
        help="Enable simplified ToM + RL + continual learning.",
    )
    parser.add_argument(
        "--output-dir",
        default="outputs",
        help="Directory for plots and CSV exports.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    results_df, actions_df, summary, resolved_path = run_across_threads(
        dataset_path=args.dataset_path,
        scenario_mode=args.scenario_mode,
        max_threads=args.max_threads,
        seed=args.seed,
        learning_mode=args.learning_mode,
    )
    comparison_df = build_distribution_comparison(results_df)
    confusion_df = build_confusion_style_table(actions_df)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    results_df.to_csv(output_dir / "thread_level_results.csv", index=False)
    actions_df.to_csv(output_dir / "action_history.csv", index=False)
    comparison_df.to_csv(output_dir / "distribution_comparison.csv", index=False)
    confusion_df.to_csv(output_dir / "confusion_style_table.csv")
    save_plots(results_df, comparison_df, output_dir)

    print(f"Dataset used: {resolved_path}")
    for line in make_summary_lines(summary):
        print(line)
    print_metrics(results_df, comparison_df, confusion_df)
    print(f"Saved outputs to {output_dir.resolve()}")


if __name__ == "__main__":
    main()
