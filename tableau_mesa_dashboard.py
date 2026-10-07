"""Tableau-style Streamlit dashboard for the Mesa cyber-bystander simulation.

This is a second dashboard view for the same Mesa backend used by the main app.
It keeps the project as a behavioural simulation, not a prediction product.

What this page does:
- collects scenario settings from the sidebar
- runs the Mesa model through mesa_bridge.py
- shows the simulation as an interactive analytics dashboard
- explains outcomes in plain English for non-technical viewers

Run locally with:
    streamlit run tableau_mesa_dashboard.py
"""

from __future__ import annotations

import os
import random

os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib")

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st

from abm_explanations import build_dataset_connection_text
from mesa_bridge import SimulationConfig, SimulationResult, build_preview_state, simulate_scenario
from mesa_learning import reset_learning_state
from preprocess_cyby23 import (
    DEFAULT_DATASET_PATH,
    build_thread_records,
    clean_dataset,
    load_raw_dataset,
    preprocessing_summary,
    resolve_dataset_path,
)


st.set_page_config(
    page_title="Mesa Cyber-Bystander Simulation Dashboard",
    page_icon="ABM",
    layout="wide",
)


THEME = {
    "ink": "#172033",
    "muted": "#697386",
    "panel": "#f8fafc",
    "border": "#d8dee9",
    "grid": "#e5e9f0",
    "abuser": "#9f1239",
    "victim": "#0f766e",
    "instigator": "#d95f02",
    "defender": "#1b9e77",
    "neutral": "#7570b3",
    "other": "#66a61e",
    "accent": "#2f6f9f",
    "warning": "#e6ab02",
    "danger": "#c0392b",
}

ROLE_LABELS = {
    "instigator": "Bully supporters",
    "defender": "Victim supporters",
    "neutral": "Silent bystanders",
    "other": "Unrelated people",
}

ACTION_LABELS = {
    "support_bully": "Supported bully",
    "support_victim": "Defended victim",
    "stay_silent": "Stayed silent",
    "step_aside": "Unrelated",
}

ACTION_COLORS = {
    "support_bully": THEME["instigator"],
    "support_victim": THEME["defender"],
    "stay_silent": THEME["neutral"],
    "step_aside": THEME["other"],
}

ROLE_ORDER = ["instigator", "defender", "neutral", "other"]
ACTION_ORDER = ["support_bully", "support_victim", "stay_silent", "step_aside"]


DEFAULTS = {
    "td_dataset_path": DEFAULT_DATASET_PATH,
    "td_total_bystanders": 24,
    "td_instigator_input": 6,
    "td_defender_input": 6,
    "td_neutral_input": 8,
    "td_initial_aggression": 52,
    "td_toxicity_level": 72,
    "td_profanity_level": 55,
    "td_identity_attack_level": 48,
    "td_like_influence": 32,
    "td_retweet_influence": 40,
    "td_random_seed": 17,
    "td_social_influence_on": True,
    "td_learning_on": True,
    "td_memory_on": True,
    "td_carry_learning": True,
    "td_result": None,
}


def initialize_state() -> None:
    for key, value in DEFAULTS.items():
        st.session_state.setdefault(key, value)
    st.session_state.setdefault("td_learning_state", reset_learning_state())


def inject_styles() -> None:
    st.markdown(
        f"""
        <style>
        .stApp {{
            background: linear-gradient(135deg, #f7fbff 0%, #eef4f8 46%, #f9f7f0 100%);
            color: {THEME["ink"]};
        }}
        [data-testid="stSidebar"] {{
            background: #ffffff;
            border-right: 1px solid {THEME["border"]};
        }}
        .hero-card {{
            background: #ffffff;
            border: 1px solid {THEME["border"]};
            border-radius: 18px;
            padding: 1.15rem 1.35rem;
            box-shadow: 0 10px 30px rgba(23, 32, 51, 0.07);
        }}
        .kpi-card {{
            background: #ffffff;
            border: 1px solid {THEME["border"]};
            border-radius: 16px;
            padding: 1rem;
            min-height: 120px;
            box-shadow: 0 8px 24px rgba(23, 32, 51, 0.06);
        }}
        .kpi-label {{
            color: {THEME["muted"]};
            font-size: 0.85rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.06em;
        }}
        .kpi-value {{
            color: {THEME["ink"]};
            font-size: 1.7rem;
            font-weight: 800;
            margin-top: 0.35rem;
        }}
        .kpi-note {{
            color: {THEME["muted"]};
            font-size: 0.88rem;
            margin-top: 0.35rem;
        }}
        .section-note {{
            color: {THEME["muted"]};
            font-size: 0.95rem;
            margin-top: -0.5rem;
            margin-bottom: 0.75rem;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def current_config() -> SimulationConfig:
    total_bystanders = int(st.session_state["td_total_bystanders"])
    instigator = min(max(0, int(st.session_state["td_instigator_input"])), total_bystanders)
    defender = min(max(0, int(st.session_state["td_defender_input"])), max(0, total_bystanders - instigator))
    neutral = min(max(0, int(st.session_state["td_neutral_input"])), max(0, total_bystanders - instigator - defender))
    other = max(0, total_bystanders - instigator - defender - neutral)
    role_counts = {
        "instigator": instigator,
        "defender": defender,
        "neutral": neutral,
        "other": other,
    }
    total_roles = max(1, sum(role_counts.values()))
    social_influence_on = bool(st.session_state["td_social_influence_on"])
    learning_on = bool(st.session_state["td_learning_on"])
    memory_on = bool(st.session_state["td_memory_on"])
    return SimulationConfig(
        total_bystanders=total_bystanders,
        instigator_pct=(role_counts["instigator"] / total_roles) * 100,
        defender_pct=(role_counts["defender"] / total_roles) * 100,
        neutral_pct=(role_counts["neutral"] / total_roles) * 100,
        other_pct=(role_counts["other"] / total_roles) * 100,
        initial_aggression=float(st.session_state["td_initial_aggression"]),
        toxicity_level=float(st.session_state["td_toxicity_level"]),
        profanity_level=float(st.session_state["td_profanity_level"]),
        identity_attack_level=float(st.session_state["td_identity_attack_level"]),
        like_influence=float(st.session_state["td_like_influence"]),
        retweet_influence=float(st.session_state["td_retweet_influence"]),
        simulation_speed=0.0,
        random_seed=int(st.session_state["td_random_seed"]),
        tom_influence_strength=0.55 if social_influence_on else 0.0,
        learning_rate=0.30 if learning_on else 0.0,
        reward_strength=0.90 if learning_on else 0.0,
        memory_retention_strength=0.80 if memory_on else 0.0,
        adaptation_speed=0.35 if memory_on else 0.0,
        carry_learning=bool(st.session_state["td_carry_learning"]) and memory_on,
    )


def load_dataset_example() -> None:
    try:
        resolved_path = resolve_dataset_path(st.session_state["td_dataset_path"])
        raw_df = load_raw_dataset(resolved_path)
        cleaned_df = clean_dataset(raw_df)
        threads = build_thread_records(cleaned_df)
    except (FileNotFoundError, ValueError, RuntimeError) as exc:
        st.warning(f"CYBY23 dataset could not be loaded: {exc}")
        return
    if not threads:
        st.warning("No dataset conversations were available to load.")
        return

    rng = random.Random(st.session_state["td_random_seed"])
    thread = rng.choice(threads)
    counts = thread.observed_role_distribution
    total = max(1, sum(counts.values()))

    st.session_state["td_total_bystanders"] = total
    st.session_state["td_instigator_input"] = int(counts.get("reinforce", 0))
    st.session_state["td_defender_input"] = int(counts.get("defend", 0))
    st.session_state["td_neutral_input"] = int(counts.get("neutral", 0))
    st.session_state["td_initial_aggression"] = round(
        min(
            100,
            25
            + 45 * thread.source_toxicity
            + 12 * thread.source_profanity
            + 10 * thread.source_identity_attack,
        )
    )
    st.session_state["td_toxicity_level"] = round(thread.source_toxicity * 100)
    st.session_state["td_profanity_level"] = round(thread.source_profanity * 100)
    st.session_state["td_identity_attack_level"] = round(thread.source_identity_attack * 100)
    st.session_state["td_like_influence"] = min(100, round(thread.source_favorite_count * 5))
    st.session_state["td_retweet_influence"] = min(100, round(thread.source_retweet_count * 10))
    st.session_state["td_result"] = None


def apply_preset(name: str) -> None:
    if name == "reset":
        for key, value in DEFAULTS.items():
            if key != "td_result":
                st.session_state[key] = value
    elif name == "random":
        rng = random.Random()
        total = rng.randint(12, 40)
        instigator = rng.randint(1, max(1, total // 3))
        defender = rng.randint(1, max(1, total // 3))
        neutral = rng.randint(1, max(1, total - instigator - defender))
        other = max(0, total - instigator - defender - neutral)
        st.session_state["td_total_bystanders"] = total
        st.session_state["td_instigator_input"] = instigator
        st.session_state["td_defender_input"] = defender
        st.session_state["td_neutral_input"] = neutral
        st.session_state["td_initial_aggression"] = rng.randint(35, 70)
        st.session_state["td_toxicity_level"] = rng.randint(30, 95)
        st.session_state["td_profanity_level"] = rng.randint(10, 90)
        st.session_state["td_identity_attack_level"] = rng.randint(10, 90)
        st.session_state["td_like_influence"] = rng.randint(0, 80)
        st.session_state["td_retweet_influence"] = rng.randint(0, 80)
        st.session_state["td_random_seed"] = rng.randint(1, 99999)
    elif name == "defender":
        total = int(st.session_state["td_total_bystanders"])
        st.session_state["td_defender_input"] = round(total * 0.58)
        st.session_state["td_instigator_input"] = round(total * 0.12)
        st.session_state["td_neutral_input"] = round(total * 0.22)
    elif name == "neutral":
        total = int(st.session_state["td_total_bystanders"])
        st.session_state["td_neutral_input"] = round(total * 0.54)
        st.session_state["td_instigator_input"] = round(total * 0.18)
        st.session_state["td_defender_input"] = round(total * 0.16)
    elif name == "instigator":
        total = int(st.session_state["td_total_bystanders"])
        st.session_state["td_instigator_input"] = round(total * 0.54)
        st.session_state["td_defender_input"] = round(total * 0.14)
        st.session_state["td_neutral_input"] = round(total * 0.22)


def result_or_preview(config: SimulationConfig) -> tuple[SimulationResult | None, object]:
    result = st.session_state["td_result"]
    if result is None:
        return None, build_preview_state(config)
    return result, result


def current_role_counts() -> dict[str, int]:
    total = int(st.session_state["td_total_bystanders"])
    instigator = min(max(0, int(st.session_state["td_instigator_input"])), total)
    defender = min(max(0, int(st.session_state["td_defender_input"])), max(0, total - instigator))
    neutral = min(max(0, int(st.session_state["td_neutral_input"])), max(0, total - instigator - defender))
    other = max(0, total - instigator - defender - neutral)
    return {
        "instigator": instigator,
        "defender": defender,
        "neutral": neutral,
        "other": other,
    }


def action_frame(result: SimulationResult) -> pd.DataFrame:
    rows = []
    for snapshot in result.snapshots:
        row = {"Step": snapshot.step, "Bullying level": snapshot.bullying_level}
        for action in ACTION_ORDER:
            row[ACTION_LABELS[action]] = snapshot.action_counts.get(action, 0)
        rows.append(row)
    return pd.DataFrame(rows)


def role_frame(result_or_preview_obj) -> pd.DataFrame:
    counts = result_or_preview_obj.composition.as_dict()
    total = max(1, result_or_preview_obj.composition.total)
    return pd.DataFrame(
        {
            "Role": [ROLE_LABELS[role] for role in ROLE_ORDER],
            "Count": [counts[role] for role in ROLE_ORDER],
            "Share": [counts[role] / total for role in ROLE_ORDER],
            "Color": [THEME[role] for role in ROLE_ORDER],
        }
    )


def render_kpi_card(label: str, value: str, note: str) -> None:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
            <div class="kpi-note">{note}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def build_bullying_area_chart(history: list[float]):
    fig, ax = plt.subplots(figsize=(9, 4.3))
    x = list(range(len(history)))
    ax.fill_between(x, history, color="#f4c7a1", alpha=0.65)
    ax.plot(x, history, color=THEME["danger"], linewidth=3.0, marker="o", markersize=5)
    ax.axhspan(80, 100, color="#f8d7da", alpha=0.45, label="High risk zone")
    ax.axhspan(0, 20, color="#d8f3dc", alpha=0.55, label="Calming zone")
    ax.set_title("Bullying level over time", loc="left", fontsize=14, fontweight="bold", color=THEME["ink"])
    ax.set_xlabel("Simulation step")
    ax.set_ylabel("Bullying level")
    ax.set_ylim(0, 100)
    ax.grid(axis="y", color=THEME["grid"], linewidth=0.8)
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(loc="upper left", fontsize=8, frameon=False)
    fig.tight_layout()
    return fig


def build_role_donut_chart(frame: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(5.5, 4.2))
    ax.pie(
        frame["Count"],
        labels=frame["Role"],
        colors=frame["Color"],
        startangle=90,
        counterclock=False,
        wedgeprops={"width": 0.42, "edgecolor": "white", "linewidth": 2},
        autopct=lambda pct: f"{pct:.0f}%" if pct >= 5 else "",
        pctdistance=0.78,
        textprops={"fontsize": 9, "color": THEME["ink"]},
    )
    ax.text(0, 0, "Roles", ha="center", va="center", fontsize=14, fontweight="bold", color=THEME["ink"])
    ax.set_title("Bystander mix", loc="left", fontsize=14, fontweight="bold", color=THEME["ink"])
    fig.tight_layout()
    return fig


def build_role_bar_chart(frame: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(6.5, 4.2))
    ordered = frame.sort_values("Count", ascending=True)
    ax.barh(ordered["Role"], ordered["Count"], color=ordered["Color"], alpha=0.9)
    ax.set_title("How many people are in each bystander role", loc="left", fontsize=14, fontweight="bold", color=THEME["ink"])
    ax.set_xlabel("Number of people")
    ax.set_ylabel("")
    ax.grid(axis="x", color=THEME["grid"], linewidth=0.8)
    ax.spines[["top", "right", "left"]].set_visible(False)
    for index, value in enumerate(ordered["Count"]):
        ax.text(value + 0.2, index, str(value), va="center", fontsize=10, color=THEME["ink"])
    fig.tight_layout()
    return fig


def build_action_stack_chart(result: SimulationResult):
    frame = action_frame(result)
    fig, ax = plt.subplots(figsize=(9, 4.4))
    if frame.empty:
        ax.text(0.5, 0.5, "Run the simulation to see actions over time.", ha="center", va="center")
        ax.axis("off")
        return fig

    bottom = np.zeros(len(frame))
    x = frame["Step"].tolist()
    for action in ACTION_ORDER:
        label = ACTION_LABELS[action]
        values = frame[label].to_numpy()
        ax.bar(x, values, bottom=bottom, color=ACTION_COLORS[action], label=label, width=0.72)
        bottom += values

    ax.set_title("What bystanders did at each step", loc="left", fontsize=14, fontweight="bold", color=THEME["ink"])
    ax.set_xlabel("Simulation step")
    ax.set_ylabel("Number of actions")
    ax.grid(axis="y", color=THEME["grid"], linewidth=0.8)
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.16), ncols=2, frameon=False)
    fig.tight_layout()
    return fig


def build_total_action_chart(result: SimulationResult):
    totals = {action: 0 for action in ACTION_ORDER}
    for snapshot in result.snapshots:
        for action in ACTION_ORDER:
            totals[action] += snapshot.action_counts.get(action, 0)

    labels = [ACTION_LABELS[action] for action in ACTION_ORDER]
    values = [totals[action] for action in ACTION_ORDER]
    colors = [ACTION_COLORS[action] for action in ACTION_ORDER]

    fig, ax = plt.subplots(figsize=(7.5, 4.2))
    ax.bar(labels, values, color=colors, alpha=0.9)
    ax.set_title("What people did overall", loc="left", fontsize=14, fontweight="bold", color=THEME["ink"])
    ax.set_ylabel("Total actions during this run")
    ax.tick_params(axis="x", rotation=12)
    ax.grid(axis="y", color=THEME["grid"], linewidth=0.8)
    ax.spines[["top", "right"]].set_visible(False)
    for index, value in enumerate(values):
        ax.text(index, value + 0.2, str(value), ha="center", fontsize=10, color=THEME["ink"])
    fig.tight_layout()
    return fig


def build_step_impact_chart(result: SimulationResult):
    fig, ax = plt.subplots(figsize=(7, 4.2))
    if not result.snapshots:
        ax.text(0.5, 0.5, "Run the simulation to see step impact.", ha="center", va="center")
        ax.axis("off")
        return fig

    steps = [snapshot.step for snapshot in result.snapshots]
    changes = [snapshot.bullying_change for snapshot in result.snapshots]
    colors = [THEME["danger"] if value >= 0 else THEME["defender"] for value in changes]
    ax.barh(steps, changes, color=colors, alpha=0.9)
    ax.axvline(0, color=THEME["ink"], linewidth=1)
    ax.set_title("Which steps pushed the situation up or down", loc="left", fontsize=14, fontweight="bold", color=THEME["ink"])
    ax.set_xlabel("Change in bullying level")
    ax.set_ylabel("Step")
    ax.grid(axis="x", color=THEME["grid"], linewidth=0.8)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    return fig


def build_simple_step_change_chart(result: SimulationResult):
    fig, ax = plt.subplots(figsize=(7.5, 4.2))
    if not result.snapshots:
        ax.text(0.5, 0.5, "Run the simulation to see step changes.", ha="center", va="center")
        ax.axis("off")
        return fig

    steps = [snapshot.step for snapshot in result.snapshots]
    changes = [snapshot.bullying_change for snapshot in result.snapshots]
    colors = [THEME["danger"] if value >= 0 else THEME["defender"] for value in changes]
    ax.bar(steps, changes, color=colors, alpha=0.9)
    ax.axhline(0, color=THEME["ink"], linewidth=1)
    ax.set_title("Did each step make things worse or calmer?", loc="left", fontsize=14, fontweight="bold", color=THEME["ink"])
    ax.set_xlabel("Simulation step")
    ax.set_ylabel("Change in bullying level")
    ax.grid(axis="y", color=THEME["grid"], linewidth=0.8)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    return fig


def build_agent_canvas(result_or_preview_obj, selected_step: int | None):
    fig, ax = plt.subplots(figsize=(7.5, 5.6))
    active_ids: set[str] = set()
    if selected_step is not None and hasattr(result_or_preview_obj, "snapshots"):
        snapshots = result_or_preview_obj.snapshots
        if snapshots:
            snapshot = snapshots[min(max(selected_step - 1, 0), len(snapshots) - 1)]
            active_ids = set(snapshot.active_agent_ids)

    ax.scatter([-0.55], [0], s=620, color=THEME["abuser"], marker="X", label="Abuser", edgecolors="white", linewidths=1.5)
    ax.scatter([0.55], [0], s=620, color=THEME["victim"], marker="o", label="Victim", edgecolors="white", linewidths=1.5)
    ax.plot([-0.35, 0.35], [0, 0], color="#b8c2cc", linewidth=2, alpha=0.9)

    for role in ROLE_ORDER:
        agents = [agent for agent in result_or_preview_obj.agents if agent.role == role]
        if not agents:
            continue
        sizes = [260 if agent.agent_id in active_ids else 120 for agent in agents]
        alpha = [1.0 if agent.agent_id in active_ids else 0.58 for agent in agents]
        ax.scatter(
            [agent.x for agent in agents],
            [agent.y for agent in agents],
            s=sizes,
            color=THEME[role],
            alpha=alpha,
            edgecolors="white",
            linewidths=1,
            label=ROLE_LABELS[role],
        )

    ax.set_title("Mesa agent environment", loc="left", fontsize=14, fontweight="bold", color=THEME["ink"])
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_xlim(-2.8, 2.8)
    ax.set_ylim(-2.8, 2.8)
    ax.set_facecolor("#fbfdff")
    ax.set_aspect("equal")
    for spine in ax.spines.values():
        spine.set_edgecolor(THEME["border"])
    handles, labels = ax.get_legend_handles_labels()
    unique = dict(zip(labels, handles))
    ax.legend(unique.values(), unique.keys(), loc="upper right", fontsize=8, frameon=False)
    fig.tight_layout()
    return fig


def build_learning_dashboard_chart(run_history):
    fig, ax = plt.subplots(figsize=(8, 4.1))
    if not run_history:
        ax.text(0.5, 0.5, "Run multiple scenarios to see how learning carries forward.", ha="center", va="center")
        ax.axis("off")
        return fig

    x = [item.run_number for item in run_history]
    ax.plot(x, [item.defender_tendency for item in run_history], color=THEME["defender"], marker="o", linewidth=2.4, label="Defender tendency")
    ax.plot(x, [item.bully_support_tendency for item in run_history], color=THEME["instigator"], marker="o", linewidth=2.4, label="Bully-support tendency")
    ax.plot(x, [item.silent_tendency for item in run_history], color=THEME["neutral"], marker="o", linewidth=2.4, label="Silent tendency")
    ax.set_title("How learned tendencies change across runs", loc="left", fontsize=14, fontweight="bold", color=THEME["ink"])
    ax.set_xlabel("Run number")
    ax.set_ylabel("Learned tendency")
    ax.grid(axis="y", color=THEME["grid"], linewidth=0.8)
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(frameon=False)
    fig.tight_layout()
    return fig


def build_story_frame(result: SimulationResult) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "Step": snapshot.step,
                "Bullying level": round(snapshot.bullying_level, 1),
                "Change": round(snapshot.bullying_change, 1),
                "Story": snapshot.story_line,
            }
            for snapshot in result.snapshots
        ]
    )


def interpret_bullying_history(history: list[float]) -> str:
    if len(history) <= 1:
        return "This chart will show whether the bullying level moves up or down after the simulation runs."

    start = history[0]
    end = history[-1]
    change = end - start
    if change >= 8:
        return f"The bullying level increased by {change:.1f} points, so the conversation became noticeably more harmful."
    if change <= -8:
        return f"The bullying level decreased by {abs(change):.1f} points, so the conversation became noticeably calmer."
    return f"The bullying level changed by only {change:+.1f} points, so the conversation stayed fairly close to where it started."


def interpret_role_mix(frame: pd.DataFrame) -> str:
    dominant = frame.sort_values("Count", ascending=False).iloc[0]
    return f"The largest group is {dominant['Role'].lower()} with {int(dominant['Count'])} people, so this role has the most influence on the starting environment."


def interpret_actions(result: SimulationResult) -> str:
    totals = {action: 0 for action in ACTION_ORDER}
    for snapshot in result.snapshots:
        for action in ACTION_ORDER:
            totals[action] += snapshot.action_counts.get(action, 0)

    dominant_action = max(totals, key=totals.get)
    return f"The most common action was: {ACTION_LABELS[dominant_action].lower()}."


def interpret_step_changes(result: SimulationResult) -> str:
    if not result.snapshots:
        return "This will show whether each step pushed the situation up or down."
    worsening_steps = sum(1 for snapshot in result.snapshots if snapshot.bullying_change > 0)
    calming_steps = sum(1 for snapshot in result.snapshots if snapshot.bullying_change < 0)
    if worsening_steps > calming_steps:
        return f"More steps made the situation worse ({worsening_steps}) than calmer ({calming_steps})."
    if calming_steps > worsening_steps:
        return f"More steps made the situation calmer ({calming_steps}) than worse ({worsening_steps})."
    return "The number of worsening and calming steps was balanced."


def interpret_learning(run_history) -> str:
    if len(run_history) < 2:
        return "Run more than one scenario to see whether learned tendencies carry forward."
    first = run_history[0]
    latest = run_history[-1]
    defender_change = latest.defender_tendency - first.defender_tendency
    silent_change = latest.silent_tendency - first.silent_tendency
    return (
        f"Across runs, defender tendency changed by {defender_change:+.2f} and silent tendency changed by {silent_change:+.2f}. "
        "This is a simple view of how carried learning is affecting later runs."
    )


def outcome_note(result: SimulationResult | None) -> tuple[str, str]:
    if result is None:
        return "Not run yet", "Choose a scenario and run the Mesa simulation."
    if result.final_outcome == "Got worse":
        return result.final_outcome, "The run crossed the high-risk threshold."
    if result.final_outcome == "Calmed down":
        return result.final_outcome, "The run crossed the calming threshold."
    return result.final_outcome, "The conversation did not clearly resolve before the step limit."


def dataset_note(dataset_path: str) -> str:
    try:
        resolved_path = resolve_dataset_path(dataset_path)
        raw_df = load_raw_dataset(resolved_path)
        cleaned_df = clean_dataset(raw_df)
        summary = preprocessing_summary(cleaned_df)
        return (
            f"Connected to CYBY23 with {summary['source_posts']} source posts and "
            f"{summary['labelled_bystander_replies']} labelled bystander replies. "
            "The dataset informs role patterns and harmful-content context, but this dashboard remains a simulation."
        )
    except Exception as exc:
        return f"Dataset note unavailable: {exc}"


initialize_state()
inject_styles()

st.markdown(
    """
    <div class="hero-card">
        <div class="kpi-label">Mesa agent-based simulation</div>
        <h1 style="margin: 0.15rem 0 0.35rem 0;">Cyber-Bystander Behaviour Dashboard</h1>
        <div style="color: #697386; font-size: 1rem;">
            Explore how bystanders can make an online bullying conversation worse, calmer, or unresolved.
            This view uses a Tableau-style analytics layout, but the simulation engine is still Mesa in Python.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.info(
    "How to read this page: start with the four summary cards, then look at the agent environment, then read the chart captions. "
    "Green means behaviour that supports the victim, orange/red means behaviour that supports harm, and purple means silence."
)

st.sidebar.title("Scenario controls")
st.sidebar.caption("Change the environment, then run the Mesa simulation.")

with st.sidebar:
    st.text_input(
        "Data file",
        key="td_dataset_path",
        help="CYBY23 provides role patterns and harmful-content context. It is not used as a prediction target here.",
    )

    st.markdown("### Presets")
    preset_col_a, preset_col_b = st.columns(2)
    if preset_col_a.button("Random", use_container_width=True):
        apply_preset("random")
    if preset_col_b.button("Dataset example", use_container_width=True):
        load_dataset_example()
    if st.button("Defender-heavy", use_container_width=True):
        apply_preset("defender")
    if st.button("Neutral-heavy", use_container_width=True):
        apply_preset("neutral")
    if st.button("Bully-support-heavy", use_container_width=True):
        apply_preset("instigator")

    st.markdown("### Bystander mix")
    st.number_input("Total bystanders", min_value=4, max_value=80, key="td_total_bystanders", help="How many people are watching or replying.")
    total_bystanders = int(st.session_state["td_total_bystanders"])
    st.caption(f"Allocate the {total_bystanders} bystanders across the roles below. The four role counts must add up to {total_bystanders}.")

    instigator_value = min(max(0, int(st.session_state["td_instigator_input"])), total_bystanders)
    instigator_count = st.number_input(
        "1. Supporting the bully",
        min_value=0,
        max_value=total_bystanders,
        value=instigator_value,
        key="td_instigator_input",
        help=f"Choose how many of the {total_bystanders} bystanders reinforce or support the harmful post.",
    )
    defender_max = max(0, total_bystanders - int(instigator_count))
    st.caption(f"Remaining after bully supporters: {defender_max}")

    defender_value = min(max(0, int(st.session_state["td_defender_input"])), defender_max)
    defender_count = st.number_input(
        "2. Supporting the victim",
        min_value=0,
        max_value=defender_max,
        value=defender_value,
        key="td_defender_input",
        help=f"Choose from the {defender_max} remaining bystanders after bully supporters are counted.",
    )
    neutral_max = max(0, total_bystanders - int(instigator_count) - int(defender_count))
    st.caption(f"Remaining after victim supporters: {neutral_max}")

    neutral_value = min(max(0, int(st.session_state["td_neutral_input"])), neutral_max)
    neutral_count = st.number_input(
        "3. Staying silent",
        min_value=0,
        max_value=neutral_max,
        value=neutral_value,
        key="td_neutral_input",
        help=f"Choose from the {neutral_max} remaining bystanders after bully and victim supporters are counted.",
    )
    other_count = max(0, total_bystanders - int(instigator_count) - int(defender_count) - int(neutral_count))
    st.metric(
        "4. Unrelated bystanders",
        other_count,
        help="Automatically calculated as the final remaining people so all roles add up to the total.",
    )
    st.caption(
        f"Final allocation: "
        f"{int(instigator_count)} supporting the bully, "
        f"{int(defender_count)} supporting the victim, "
        f"{int(neutral_count)} staying silent, and "
        f"{int(other_count)} unrelated = {total_bystanders} total bystanders."
    )

    st.markdown("### Starting situation")
    st.slider("Starting bullying level", 0, 100, key="td_initial_aggression", help="How intense the situation is at the beginning.")
    st.slider("Toxicity", 0, 100, key="td_toxicity_level", help="How hostile the harmful content is.")
    st.slider("Profanity", 0, 100, key="td_profanity_level", help="How much offensive language is present.")
    st.slider("Identity attack", 0, 100, key="td_identity_attack_level", help="How much the content targets identity or background.")
    st.slider("Likes influence", 0, 100, key="td_like_influence", help="How much visible approval amplifies pressure.")
    st.slider("Retweets influence", 0, 100, key="td_retweet_influence", help="How much sharing amplifies pressure.")
    with st.expander("Technical repeat option", expanded=False):
        st.caption(
            "Most viewers can ignore this. It only keeps the random choices consistent when you want to repeat the exact same run."
        )
        st.number_input(
            "Repeat setting",
            min_value=1,
            max_value=99999,
            key="td_random_seed",
            help="Keeps runs consistent when settings are the same.",
        )

    st.markdown("### Advanced behaviour")
    st.caption("Use simple switches for the behavioural extensions. The dashboard chooses sensible internal values for the Mesa model.")
    st.toggle(
        "Social influence on",
        key="td_social_influence_on",
        help="When on, agents are influenced by what they think other bystanders may do.",
    )
    st.toggle(
        "Learning from outcomes on",
        key="td_learning_on",
        help="When on, agents adjust after seeing whether their action helped or worsened the situation.",
    )
    st.toggle(
        "Memory across runs on",
        key="td_memory_on",
        help="When on, the simulation keeps part of what agents learned from earlier runs.",
    )
    st.toggle(
        "Carry learning into next run",
        key="td_carry_learning",
        disabled=not st.session_state["td_memory_on"],
        help="When on, agents keep some experience between runs. This only applies when memory is on.",
    )
    st.caption(
        "Internal settings used: social influence = 0.55 when on, learning rate = 0.30 when on, reward strength = 0.90 when on, memory retention = 0.80 when on."
    )
    if st.button("Reset learning memory", use_container_width=True):
        st.session_state["td_learning_state"] = reset_learning_state()
        st.session_state["td_result"] = None

    run_col, reset_col = st.columns(2)
    if run_col.button("Run simulation", type="primary", use_container_width=True):
        st.session_state["td_result"] = simulate_scenario(current_config(), st.session_state["td_learning_state"])
        st.session_state["td_learning_state"] = st.session_state["td_result"].updated_learning_state
    if reset_col.button("Reset view", use_container_width=True):
        apply_preset("reset")
        st.session_state["td_result"] = None

config = current_config()
result, view_obj = result_or_preview(config)

final_level = result.bullying_history[-1] if result else config.initial_aggression
level_change = final_level - config.initial_aggression
outcome_value, outcome_help = outcome_note(result)
role_data = role_frame(view_obj)

st.write("")
kpi_cols = st.columns(4)
with kpi_cols[0]:
    render_kpi_card("Final outcome", outcome_value, outcome_help)
with kpi_cols[1]:
    render_kpi_card("Bullying level", f"{final_level:.1f}", f"Started at {config.initial_aggression:.1f}.")
with kpi_cols[2]:
    render_kpi_card("Change", f"{level_change:+.1f}", "Positive means the situation became more harmful.")
with kpi_cols[3]:
    render_kpi_card("Mesa agents", str(view_obj.composition.total), "Bystanders created as Mesa agents.")

st.caption("Scenario basis: interactive Mesa simulation. Use the dataset example button when you want the controls filled from CYBY23.")

st.write("")
left, right = st.columns((1.45, 1.0))

with left:
    st.subheader("Simulation view")
    st.markdown('<div class="section-note">This panel shows the Mesa agents and how the bullying level changes during the run.</div>', unsafe_allow_html=True)

    if result and result.snapshots:
        if len(result.snapshots) == 1:
            selected_step = 1
            st.caption("This run ended after one step, so there is only one step to inspect.")
        else:
            selected_step = st.slider(
                "Inspect simulation step",
                1,
                len(result.snapshots),
                len(result.snapshots),
                help="Move through the run to see which agents were active.",
            )
        history_to_show = result.bullying_history[: selected_step + 1]
    else:
        selected_step = None
        history_to_show = view_obj.bullying_history

    canvas_col, role_col = st.columns((1.35, 0.85))
    with canvas_col:
        st.pyplot(build_agent_canvas(view_obj, selected_step), use_container_width=True)
        st.caption("How to read it: larger dots are bystanders who acted in the selected simulation step.")
    with role_col:
        st.pyplot(build_role_bar_chart(role_data), use_container_width=True)
        st.caption(interpret_role_mix(role_data))
        st.dataframe(
            role_data[["Role", "Count"]].assign(Share=lambda df: (role_data["Share"] * 100).round(1).astype(str) + "%"),
            use_container_width=True,
            hide_index=True,
        )

    st.pyplot(build_bullying_area_chart(history_to_show), use_container_width=True)
    st.caption(interpret_bullying_history(history_to_show))

with right:
    st.subheader("Outcome explanation")
    st.markdown('<div class="section-note">This is written for a non-technical audience.</div>', unsafe_allow_html=True)
    if result:
        st.markdown("**What happened here?**")
        st.write(result.explanation)
        st.markdown("**What this means in simple terms**")
        st.write(result.simple_takeaway)
    else:
        st.info("Run the simulation to generate the outcome explanation.")

    st.markdown("**How this connects to CYBY23**")
    st.write(dataset_note(st.session_state["td_dataset_path"]))
    st.caption(build_dataset_connection_text())

st.write("")
chart_left, chart_right = st.columns((1.15, 1.0))

with chart_left:
    st.subheader("What people did")
    st.markdown('<div class="section-note">This chart adds up the actions across the run, so it is easier to compare behaviour types.</div>', unsafe_allow_html=True)
    if result:
        st.pyplot(build_total_action_chart(result), use_container_width=True)
        st.caption(interpret_actions(result))
    else:
        st.info("Run the simulation to see what people did.")

with chart_right:
    st.subheader("Step-by-step impact")
    st.markdown('<div class="section-note">Bars above zero mean the bullying got worse. Bars below zero mean it got calmer.</div>', unsafe_allow_html=True)
    if result:
        st.pyplot(build_simple_step_change_chart(result), use_container_width=True)
        st.caption(interpret_step_changes(result))
    else:
        st.info("Run the simulation to see step-by-step impact.")

st.write("")
learning_col, story_col = st.columns((1.0, 1.25))

with learning_col:
    st.subheader("Learning across runs")
    st.markdown('<div class="section-note">If carry-over learning is on, agents keep some experience from earlier runs.</div>', unsafe_allow_html=True)
    st.pyplot(build_learning_dashboard_chart(st.session_state["td_learning_state"].run_history), use_container_width=True)
    st.caption(interpret_learning(st.session_state["td_learning_state"].run_history))

with story_col:
    st.subheader("Simulation story")
    st.markdown('<div class="section-note">A plain-English timeline of what happened inside the Mesa run.</div>', unsafe_allow_html=True)
    if result:
        st.dataframe(build_story_frame(result), use_container_width=True, hide_index=True)
    else:
        st.info("Run the simulation to generate the story timeline.")

st.write("")
with st.expander("Technical note: how this dashboard uses Mesa"):
    st.write(
        "This dashboard is built with Streamlit for the interactive web interface. "
        "The simulation itself is run by the Mesa backend through `mesa_bridge.py`. "
        "When you click Run simulation, the app creates `CyberBystanderMesaModel`, creates bystander agents, "
        "activates them step by step with Mesa, collects the results, and then renders the charts here."
    )
