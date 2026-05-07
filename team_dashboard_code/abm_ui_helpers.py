from __future__ import annotations

import matplotlib.pyplot as plt
import pandas as pd

from mesa_bridge import AgentProfile, SimulationResult, SimulationSnapshot
from mesa_learning import ROLE_ORDER, RunLearningSummary


ROLE_LABELS = {
    "instigator": "Bully supporters",
    "defender": "Victim supporters",
    "neutral": "Silent bystanders",
    "other": "Unrelated people",
}

ROLE_COLORS = {
    "instigator": "#b91c1c",
    "defender": "#15803d",
    "neutral": "#64748b",
    "other": "#2563eb",
}


def build_environment_figure(agents: list[AgentProfile], snapshot: SimulationSnapshot | None):
    fig, ax = plt.subplots(figsize=(6, 6))

    ax.scatter([-0.6], [0], s=420, color="#991b1b", marker="X", label="Abuser")
    ax.scatter([0.6], [0], s=420, color="#0f766e", marker="o", edgecolors="black", label="Victim")

    active_ids = set(snapshot.active_agent_ids) if snapshot is not None else set()
    for role in ROLE_ORDER:
        role_agents = [agent for agent in agents if agent.role == role]
        if not role_agents:
            continue
        x_values = [agent.x for agent in role_agents]
        y_values = [agent.y for agent in role_agents]
        sizes = [220 if agent.agent_id in active_ids else 110 for agent in role_agents]
        alpha = [1.0 if agent.agent_id in active_ids else 0.45 for agent in role_agents]
        ax.scatter(
            x_values,
            y_values,
            s=sizes,
            color=ROLE_COLORS[role],
            alpha=alpha,
            edgecolors="black",
            linewidths=0.6,
            label=ROLE_LABELS[role],
        )

    ax.set_title("Simulation environment")
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_xlim(-2.8, 2.8)
    ax.set_ylim(-2.8, 2.8)
    ax.set_aspect("equal")
    handles, labels = ax.get_legend_handles_labels()
    unique = dict(zip(labels, handles))
    ax.legend(unique.values(), unique.keys(), loc="upper right", fontsize=8)
    fig.tight_layout()
    return fig


def build_bullying_chart(history: list[float]):
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(range(len(history)), history, color="#b91c1c", marker="o", linewidth=2.5)
    ax.axhline(80, color="#dc2626", linestyle="--", linewidth=1, label="Gets worse threshold")
    ax.axhline(20, color="#15803d", linestyle="--", linewidth=1, label="Calms down threshold")
    ax.set_title("How the bullying level changes over time")
    ax.set_xlabel("Simulation step")
    ax.set_ylabel("Bullying level")
    ax.set_ylim(0, 100)
    ax.legend(loc="upper left", fontsize=8)
    fig.tight_layout()
    return fig


def build_role_breakdown_chart(result: SimulationResult):
    counts = result.composition.as_dict()
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(
        [ROLE_LABELS[role] for role in ROLE_ORDER],
        [counts[role] for role in ROLE_ORDER],
        color=[ROLE_COLORS[role] for role in ROLE_ORDER],
    )
    ax.set_title("Who is in this simulation")
    ax.set_ylabel("Number of people")
    ax.tick_params(axis="x", rotation=10)
    fig.tight_layout()
    return fig


def build_story_table(result: SimulationResult) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "Step": snapshot.step,
                "Bullying level": round(snapshot.bullying_level, 1),
                "What happened": snapshot.story_line,
            }
            for snapshot in result.snapshots
        ]
    )


def composition_table(result: SimulationResult) -> pd.DataFrame:
    counts = result.composition.as_dict()
    total = max(1, result.composition.total)
    return pd.DataFrame(
        {
            "Role": [ROLE_LABELS[role] for role in ROLE_ORDER],
            "People": [counts[role] for role in ROLE_ORDER],
            "Share": [f"{(counts[role] / total) * 100:.1f}%" for role in ROLE_ORDER],
        }
    )


def build_tendency_chart(run_history: list[RunLearningSummary]):
    fig, ax = plt.subplots(figsize=(7, 4))
    if run_history:
        x = [item.run_number for item in run_history]
        ax.plot(x, [item.defender_tendency for item in run_history], marker="o", color="#15803d", label="Defender tendency")
        ax.plot(x, [item.bully_support_tendency for item in run_history], marker="o", color="#b91c1c", label="Bully-support tendency")
        ax.plot(x, [item.silent_tendency for item in run_history], marker="o", color="#64748b", label="Silent tendency")
    ax.set_title("How agent tendencies change over repeated runs")
    ax.set_xlabel("Run number")
    ax.set_ylabel("Learned tendency")
    ax.legend()
    fig.tight_layout()
    return fig


def build_action_share_chart(run_history: list[RunLearningSummary]):
    fig, ax = plt.subplots(figsize=(7, 4))
    if run_history:
        x = [item.run_number for item in run_history]
        ax.plot(x, [item.defender_action_share for item in run_history], marker="o", color="#15803d", label="Defending became more common")
        ax.plot(x, [item.bully_support_action_share for item in run_history], marker="o", color="#b91c1c", label="Bully support became more common")
        ax.plot(x, [item.silent_action_share for item in run_history], marker="o", color="#64748b", label="Silence became more common")
    ax.set_title("What kinds of actions became more common over repeated runs")
    ax.set_xlabel("Run number")
    ax.set_ylabel("Share of actions")
    ax.legend()
    fig.tight_layout()
    return fig


def learning_history_table(run_history: list[RunLearningSummary]) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "Run": item.run_number,
                "Defender tendency": round(item.defender_tendency, 3),
                "Bully-support tendency": round(item.bully_support_tendency, 3),
                "Silent tendency": round(item.silent_tendency, 3),
                "Defender share": round(item.defender_action_share, 3),
                "Bully-support share": round(item.bully_support_action_share, 3),
                "Silent share": round(item.silent_action_share, 3),
                "Outcome": item.outcome,
            }
            for item in run_history
        ]
    )
