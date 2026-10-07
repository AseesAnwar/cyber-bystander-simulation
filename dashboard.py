"""Plain-English cyberbystander simulation dashboard with ToM, RL, and CL.

This page remains a behavioural simulation environment, not a prediction tool.
It adds three richer behaviour layers:
- Theory of Mind: agents react to what they think others may do
- Reinforcement Learning: agents adjust action tendencies from outcomes
- Continual Learning: agents can keep some experience across repeated runs
"""

from __future__ import annotations

import os
import random
import time

os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib")

import matplotlib

matplotlib.use("Agg")
import streamlit as st

from abm_explanations import build_dataset_connection_text
from abm_ui_helpers import (
    build_action_share_chart,
    build_bullying_chart,
    build_environment_figure,
    build_role_breakdown_chart,
    build_story_table,
    build_tendency_chart,
    composition_table,
    learning_history_table,
)
from cyby23_learning import build_cyby23_learning_profile, build_learning_state_from_profile
from mesa_bridge import SimulationConfig, build_preview_state, simulate_scenario
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
    page_title="Cyberbystander Simulation Environment",
    page_icon="🧭",
    layout="wide",
)


DEFAULTS = {
    "dataset_path": DEFAULT_DATASET_PATH,
    "total_bystanders": 24,
    "instigator_pct": 24,
    "defender_pct": 26,
    "neutral_pct": 35,
    "other_pct": 15,
    "initial_aggression": 52,
    "toxicity_level": 72,
    "profanity_level": 55,
    "identity_attack_level": 48,
    "like_influence": 32,
    "retweet_influence": 40,
    "simulation_speed": 0.08,
    "random_seed": 17,
    "tom_influence_strength": 0.55,
    "learning_rate": 0.30,
    "reward_strength": 0.90,
    "memory_retention_strength": 0.80,
    "adaptation_speed": 0.35,
    "carry_learning": True,
    "dataset_risk_filter": "all",
    "dataset_learning_strength": 0.70,
    "dataset_profile": None,
    "result": None,
}


def initialize_state() -> None:
    for key, value in DEFAULTS.items():
        st.session_state.setdefault(key, value)
    st.session_state.setdefault("learning_state", reset_learning_state())


def load_dataset_defaults() -> None:
    try:
        threads = load_thread_records_from_state()
    except (FileNotFoundError, ValueError, RuntimeError) as exc:
        st.warning(f"CYBY23 dataset could not be loaded: {exc}")
        return
    if not threads:
        st.warning("No CYBY23 conversations were available to load.")
        return
    rng = random.Random(st.session_state["random_seed"])
    thread = rng.choice(threads)
    counts = thread.observed_role_distribution
    total = max(1, sum(counts.values()))
    st.session_state["total_bystanders"] = total
    st.session_state["instigator_pct"] = round((counts.get("reinforce", 0) / total) * 100)
    st.session_state["defender_pct"] = round((counts.get("defend", 0) / total) * 100)
    st.session_state["neutral_pct"] = round((counts.get("neutral", 0) / total) * 100)
    st.session_state["other_pct"] = round((counts.get("unrelated", 0) / total) * 100)
    st.session_state["initial_aggression"] = round(
        min(
            100,
            25
            + 45 * thread.source_toxicity
            + 12 * thread.source_profanity
            + 10 * thread.source_identity_attack,
        )
    )
    st.session_state["toxicity_level"] = round(thread.source_toxicity * 100)
    st.session_state["profanity_level"] = round(thread.source_profanity * 100)
    st.session_state["identity_attack_level"] = round(thread.source_identity_attack * 100)
    st.session_state["like_influence"] = min(100, round(thread.source_favorite_count * 5))
    st.session_state["retweet_influence"] = min(100, round(thread.source_retweet_count * 10))


def load_thread_records_from_state():
    resolved_path = resolve_dataset_path(st.session_state["dataset_path"])
    raw_df = load_raw_dataset(resolved_path)
    cleaned_df = clean_dataset(raw_df)
    return build_thread_records(cleaned_df)


def learn_from_cyby23_dataset() -> None:
    try:
        threads = load_thread_records_from_state()
    except (FileNotFoundError, ValueError, RuntimeError) as exc:
        st.warning(f"CYBY23 dataset could not be loaded: {exc}")
        return
    profile = build_cyby23_learning_profile(
        threads,
        risk_filter=st.session_state["dataset_risk_filter"],
    )
    st.session_state["learning_state"] = build_learning_state_from_profile(
        profile,
        strength=float(st.session_state["dataset_learning_strength"]),
    )
    st.session_state["dataset_profile"] = profile
    st.session_state["total_bystanders"] = max(8, min(80, round(profile.labelled_reply_count / max(1, profile.thread_count))))
    st.session_state["instigator_pct"] = round(profile.agent_role_percentages["instigator"])
    st.session_state["defender_pct"] = round(profile.agent_role_percentages["defender"])
    st.session_state["neutral_pct"] = round(profile.agent_role_percentages["neutral"])
    st.session_state["other_pct"] = round(profile.agent_role_percentages["other"])
    st.session_state["initial_aggression"] = round(
        min(
            100,
            25
            + 45 * profile.mean_toxicity
            + 12 * profile.mean_profanity
            + 10 * profile.mean_identity_attack,
        )
    )
    st.session_state["toxicity_level"] = round(profile.mean_toxicity * 100)
    st.session_state["profanity_level"] = round(profile.mean_profanity * 100)
    st.session_state["identity_attack_level"] = round(profile.mean_identity_attack * 100)
    st.session_state["like_influence"] = min(100, round(profile.mean_favorites * 5))
    st.session_state["retweet_influence"] = min(100, round(profile.mean_retweets * 10))
    st.session_state["result"] = None


def apply_preset(name: str) -> None:
    if name == "reset":
        for key, value in DEFAULTS.items():
            if key != "result":
                st.session_state[key] = value
    elif name == "random":
        rng = random.Random()
        st.session_state["total_bystanders"] = rng.randint(12, 40)
        st.session_state["instigator_pct"] = rng.randint(10, 45)
        st.session_state["defender_pct"] = rng.randint(10, 45)
        st.session_state["neutral_pct"] = rng.randint(10, 50)
        st.session_state["other_pct"] = rng.randint(5, 25)
        st.session_state["initial_aggression"] = rng.randint(35, 70)
        st.session_state["toxicity_level"] = rng.randint(30, 95)
        st.session_state["profanity_level"] = rng.randint(10, 90)
        st.session_state["identity_attack_level"] = rng.randint(10, 90)
        st.session_state["like_influence"] = rng.randint(0, 80)
        st.session_state["retweet_influence"] = rng.randint(0, 80)
        st.session_state["random_seed"] = rng.randint(1, 99999)
    elif name == "defender":
        st.session_state["instigator_pct"] = 15
        st.session_state["defender_pct"] = 50
        st.session_state["neutral_pct"] = 25
        st.session_state["other_pct"] = 10
    elif name == "neutral":
        st.session_state["instigator_pct"] = 18
        st.session_state["defender_pct"] = 18
        st.session_state["neutral_pct"] = 50
        st.session_state["other_pct"] = 14
    elif name == "instigator":
        st.session_state["instigator_pct"] = 48
        st.session_state["defender_pct"] = 16
        st.session_state["neutral_pct"] = 24
        st.session_state["other_pct"] = 12


def current_config() -> SimulationConfig:
    return SimulationConfig(
        total_bystanders=int(st.session_state["total_bystanders"]),
        instigator_pct=float(st.session_state["instigator_pct"]),
        defender_pct=float(st.session_state["defender_pct"]),
        neutral_pct=float(st.session_state["neutral_pct"]),
        other_pct=float(st.session_state["other_pct"]),
        initial_aggression=float(st.session_state["initial_aggression"]),
        toxicity_level=float(st.session_state["toxicity_level"]),
        profanity_level=float(st.session_state["profanity_level"]),
        identity_attack_level=float(st.session_state["identity_attack_level"]),
        like_influence=float(st.session_state["like_influence"]),
        retweet_influence=float(st.session_state["retweet_influence"]),
        simulation_speed=float(st.session_state["simulation_speed"]),
        random_seed=int(st.session_state["random_seed"]),
        tom_influence_strength=float(st.session_state["tom_influence_strength"]),
        learning_rate=float(st.session_state["learning_rate"]),
        reward_strength=float(st.session_state["reward_strength"]),
        memory_retention_strength=float(st.session_state["memory_retention_strength"]),
        adaptation_speed=float(st.session_state["adaptation_speed"]),
        carry_learning=bool(st.session_state["carry_learning"]),
    )


def run_and_animate(config: SimulationConfig):
    result = simulate_scenario(config, st.session_state["learning_state"])
    st.session_state["learning_state"] = result.updated_learning_state

    environment_placeholder = st.empty()
    chart_placeholder = st.empty()
    story_placeholder = st.empty()

    visible_history = [result.bullying_history[0]]
    visible_rows = []

    for index, snapshot in enumerate(result.snapshots, start=1):
        visible_history.append(result.bullying_history[index])
        environment_placeholder.pyplot(
            build_environment_figure(result.agents, snapshot),
            use_container_width=True,
        )
        chart_placeholder.pyplot(
            build_bullying_chart(visible_history),
            use_container_width=True,
        )
        visible_rows.append({"Step": snapshot.step, "What happened": snapshot.story_line})
        story_placeholder.dataframe(visible_rows, use_container_width=True, hide_index=True)
        if config.simulation_speed > 0:
            time.sleep(config.simulation_speed)

    return result


def render_outcome_card(result) -> None:
    if result.final_outcome == "Got worse":
        text_color = "#7f1d1d"
        background = "#fee2e2"
    elif result.final_outcome == "Calmed down":
        text_color = "#14532d"
        background = "#dcfce7"
    else:
        text_color = "#334155"
        background = "#e2e8f0"

    st.markdown(
        f"""
        <div style="padding: 1rem 1.2rem; border-radius: 14px; background: {background}; border: 1px solid {text_color}33;">
            <div style="font-size: 0.85rem; color: {text_color}; font-weight: 600;">Final outcome</div>
            <div style="font-size: 1.6rem; color: {text_color}; font-weight: 700; margin-top: 0.25rem;">{result.final_outcome}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def dataset_note(dataset_path: str) -> tuple[str | None, str]:
    try:
        resolved_path = resolve_dataset_path(dataset_path)
        raw_df = load_raw_dataset(resolved_path)
        cleaned_df = clean_dataset(raw_df)
        summary = preprocessing_summary(cleaned_df)
    except (FileNotFoundError, ValueError, RuntimeError) as exc:
        return (
            None,
            "CYBY23 is not currently loaded. Manual what-if simulation remains available. "
            f"Dataset-specific calibration is disabled until a valid file is provided ({exc}).",
        )

    message = (
        f"The dashboard is connected to the CYBY23 dataset, which contains `{summary['source_posts']}` online discussion starters and `{summary['labelled_bystander_replies']}` labelled replies. "
        "The dataset provides aggregate role patterns and harmful-content context for calibration. "
        "It is not used as evidence of independent predictive accuracy."
    )
    return str(resolved_path), message


initialize_state()

st.title("Cyberbystander Simulation Environment")
st.caption(
    "This dashboard is designed as a behavioural simulation environment. It shows how different kinds of bystanders can make online bullying worse, help calm it down, or leave it unresolved."
)

st.markdown(
    """
    **How to use this page**

    Use the controls to build a bystander environment, run the simulation, and then read the story of what happened.
    The goal is to understand behaviour, not to predict exact real-world outcomes.
    """
)

left_col, center_col, right_col = st.columns((1.1, 1.35, 1.05))

with left_col:
    st.subheader("Simulation controls")
    st.caption("Change the people in the environment and the starting conditions.")

    st.text_input(
        "Data file",
        key="dataset_path",
        help="The CYBY23 dataset provides the role patterns and aggression context behind this prototype.",
    )

    action_cols = st.columns(2)
    if action_cols[0].button("Run Simulation", use_container_width=True, type="primary"):
        st.session_state["result"] = "pending"
    if action_cols[1].button("Reset", use_container_width=True):
        apply_preset("reset")

    preset_cols = st.columns(2)
    if preset_cols[0].button("Random Scenario", use_container_width=True):
        apply_preset("random")
    if preset_cols[1].button("Load Dataset Example", use_container_width=True):
        load_dataset_defaults()

    st.selectbox(
        "CYBY23 calibration filter",
        ["all", "low", "medium", "high"],
        key="dataset_risk_filter",
        help="Choose which CYBY23 thread risk group should provide aggregate calibration priors.",
    )
    st.slider(
        "CYBY23 calibration strength",
        0.0,
        2.0,
        key="dataset_learning_strength",
        help="Controls how strongly observed CYBY23 role patterns bias the agents' starting behaviour.",
    )
    if st.button("Calibrate From CYBY23", use_container_width=True):
        learn_from_cyby23_dataset()

    if st.session_state["dataset_profile"] is not None:
        st.success(st.session_state["dataset_profile"].summary())

    if st.button("Defender-Heavy Scenario", use_container_width=True):
        apply_preset("defender")
    if st.button("Neutral-Heavy Scenario", use_container_width=True):
        apply_preset("neutral")
    if st.button("Instigator-Heavy Scenario", use_container_width=True):
        apply_preset("instigator")

    st.markdown("**Bystanders in the simulation**")
    st.number_input(
        "Total number of bystanders",
        min_value=4,
        max_value=80,
        key="total_bystanders",
        help="How many people are watching the bullying situation.",
    )
    st.slider(
        "How many bystanders are supporting the bully",
        0,
        100,
        key="instigator_pct",
        help="A higher value means more people actively help the bullying continue.",
    )
    st.slider(
        "How many bystanders are supporting the victim",
        0,
        100,
        key="defender_pct",
        help="A higher value means more people try to push back against the harm.",
    )
    st.slider(
        "How many people stay silent",
        0,
        100,
        key="neutral_pct",
        help="Silent bystanders do not intervene, which can make it easier for bullying to keep going.",
    )
    st.slider(
        "How many unrelated people are present",
        0,
        100,
        key="other_pct",
        help="These people do not meaningfully affect the conflict.",
    )

    st.markdown("**Starting conditions**")
    st.slider(
        "Starting bullying level",
        0,
        100,
        key="initial_aggression",
        help="How intense the harmful situation is at the beginning.",
    )
    st.slider(
        "Toxicity level",
        0,
        100,
        key="toxicity_level",
        help="How harsh or hostile the harmful content is.",
    )
    st.slider(
        "Profanity level",
        0,
        100,
        key="profanity_level",
        help="How much insulting or offensive language is present.",
    )
    st.slider(
        "Identity attack level",
        0,
        100,
        key="identity_attack_level",
        help="How much the harmful content targets identity or personal background.",
    )
    st.slider(
        "Engagement boost from likes",
        0,
        100,
        key="like_influence",
        help="A higher value means visible approval can amplify the bullying pressure.",
    )
    st.slider(
        "Engagement boost from retweets",
        0,
        100,
        key="retweet_influence",
        help="A higher value means sharing and spread can amplify the bullying pressure.",
    )
    st.slider(
        "Simulation speed",
        0.0,
        0.5,
        key="simulation_speed",
        help="Controls how quickly the simulation plays through each step.",
    )
    st.number_input(
        "Random seed",
        min_value=1,
        max_value=99999,
        key="random_seed",
        help="Keeps the same simulation path if you want to repeat the same run.",
    )

    st.markdown("**Advanced behaviour settings**")
    st.caption("These settings control how agents think, learn, and remember.")
    st.slider(
        "ToM influence strength",
        0.0,
        1.0,
        key="tom_influence_strength",
        help="Some people are influenced by what they think others will do.",
    )
    st.slider(
        "Learning rate",
        0.0,
        1.0,
        key="learning_rate",
        help="How quickly agents change behaviour after a result.",
    )
    st.slider(
        "Reward strength",
        0.0,
        1.5,
        key="reward_strength",
        help="How strongly good or bad outcomes shape future behaviour.",
    )
    st.slider(
        "Memory retention strength",
        0.0,
        1.0,
        key="memory_retention_strength",
        help="How much past experience agents keep for future runs.",
    )
    st.slider(
        "Adaptation speed",
        0.0,
        1.0,
        key="adaptation_speed",
        help="How quickly old habits change when the situation changes.",
    )
    st.toggle(
        "Carry learning into next run",
        key="carry_learning",
        help="Agents do not start from zero every time. They carry some experience from earlier runs into new situations.",
    )
    if st.button("Reset learning", use_container_width=True):
        st.session_state["learning_state"] = reset_learning_state()

with center_col:
    st.subheader("Simulation environment")
    st.caption("This is the main simulation space. The abuser, victim, and bystanders are shown here as agents in one environment.")

    config = current_config()
    if st.session_state["result"] == "pending":
        with st.spinner("Running simulation..."):
            st.session_state["result"] = run_and_animate(config)
    elif st.session_state["result"] is None:
        preview_state = build_preview_state(config)
        st.pyplot(build_environment_figure(preview_state.agents, None), use_container_width=True)
        st.pyplot(build_bullying_chart(preview_state.bullying_history), use_container_width=True)
        st.caption("Run the simulation to watch how the bystanders influence the situation over time.")
    else:
        result = st.session_state["result"]
        st.pyplot(build_environment_figure(result.agents, result.snapshots[-1] if result.snapshots else None), use_container_width=True)
        st.pyplot(build_bullying_chart(result.bullying_history), use_container_width=True)
        st.caption("The center panel lets you watch the environment change step by step, like a simple Mesa-style simulation view.")

    st.markdown("**Story mode**")
    st.caption("This reads like a simple explanation of what happened at each step.")
    if st.session_state["result"] not in (None, "pending"):
        st.dataframe(build_story_table(st.session_state["result"]), use_container_width=True, hide_index=True)
    else:
        st.info("Run a scenario to generate the step-by-step story.")

with right_col:
    st.subheader("Results and explanation")
    st.caption("This panel explains the outcome in simple language and connects it back to the dataset context.")

    resolved_dataset_path, dataset_message = dataset_note(st.session_state["dataset_path"])
    st.markdown("**How this connects to the real dataset**")
    st.write(dataset_message)
    st.caption(build_dataset_connection_text())

    if st.session_state["result"] not in (None, "pending"):
        result = st.session_state["result"]
        render_outcome_card(result)

        st.markdown("**Who is in this environment**")
        st.caption("This shows the bystander mix used in the simulation.")
        st.dataframe(composition_table(result), use_container_width=True, hide_index=True)
        st.pyplot(build_role_breakdown_chart(result), use_container_width=True)

        st.markdown("**What happened here?**")
        st.write(result.explanation)

        st.markdown("**What this means in simple terms**")
        st.write(result.simple_takeaway)

        st.markdown("**How learning changed behaviour across runs**")
        st.caption("These charts show whether agents became more defender-like, more bully-supporting, or more silent over repeated runs.")
        run_history = st.session_state["learning_state"].run_history
        st.pyplot(build_tendency_chart(run_history), use_container_width=True)
        st.pyplot(build_action_share_chart(run_history), use_container_width=True)
        st.dataframe(learning_history_table(run_history), use_container_width=True, hide_index=True)
    else:
        st.info("Run a scenario to see the outcome, explanation, and learning panels.")

st.subheader("Why this dashboard matters")
st.write(
    "This simulation helps us explore how the composition and timing of bystander behaviour can influence cyberbullying outcomes. "
    "It is designed to support understanding of behavioural dynamics rather than predict exact real-world outcomes."
)
