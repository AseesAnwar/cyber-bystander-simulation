from __future__ import annotations

from pathlib import Path

from run_simulation import (
    build_confusion_style_table,
    build_distribution_comparison,
    print_metrics,
    run_across_threads,
    save_plots,
)


def main() -> None:
    output_dir = Path("demo_outputs")
    results_df, actions_df, summary, resolved_path = run_across_threads(
        dataset_path="/mnt/data/CYBERBYSTANDER (CYBY23) dataset.xlsx",
        scenario_mode="all",
        max_threads=20,
        seed=11,
    )

    comparison_df = build_distribution_comparison(results_df)
    confusion_df = build_confusion_style_table(actions_df)
    save_plots(results_df, comparison_df, output_dir)

    print("CYBY23 demo run")
    print("---------------")
    print(f"Dataset used: {resolved_path}")
    print(f"Scenario mode: {summary['scenario_mode']}")
    print(f"Threads simulated: {summary['simulated_threads']}")
    print(
        "Mean role agreement rate: "
        f"{summary['mean_role_agreement_rate']:.3f} "
        "(descriptive reproduction metric; not predictive accuracy)"
    )
    print(f"Mean escalation score: {summary['mean_escalation_score']:.3f}")
    print(f"Mean defence score: {summary['mean_defence_score']:.3f}")
    print()
    print_metrics(results_df, comparison_df, confusion_df)
    print(f"Saved demo plot to {(output_dir / 'simulation_summary.png').resolve()}")


if __name__ == "__main__":
    main()
