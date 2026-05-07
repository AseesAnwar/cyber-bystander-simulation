"""Standalone Streamlit dashboard for the CYBY23 interactive Mesa model.

Run with:
    python3 -m streamlit run cyby23_interactive_dashboard.py --server.port 8502
"""

from __future__ import annotations

import pandas as pd
import streamlit as st

from cyby23_interactive_model import (
    ACTIONS,
    CYBY23SimulationConfig,
    filter_threads_by_risk,
    load_cyby23_threads,
    run_cyby23_simulation,
)
from preprocess_cyby23 import DEFAULT_DATASET_PATH, NORMALIZED_ROLE_ORDER


ACTION_LABELS = {
    "ignore": "Ignore / stay silent",
    "defend": "Defend the target",
    "report": "Report the incident",
    "reinforce": "Reinforce the harm",
}

ROLE_EXPLANATIONS = {
    "reinforce": "Replies that agree with or support the harmful post.",
    "defend": "Replies that disagree with the harmful post or push back.",
    "neutral": "Replies that do not take a clear side.",
    "unrelated": "Replies that are not meaningfully part of the conflict.",
}

STRATEGY_PRESETS = {
    "Dataset baseline": {
        "anonymity_level": 0.55,
        "peer_influence_strength": 0.65,
        "learning_rate": 0.30,
        "learning_strength": 0.75,
        "steps": 25,
        "description": "Use the CYBY23 labels as the main starting point, with neutral modelling assumptions.",
    },
    "More anonymous platform": {
        "anonymity_level": 0.85,
        "peer_influence_strength": 0.80,
        "learning_rate": 0.25,
        "learning_strength": 0.85,
        "steps": 25,
        "description": "Ask what could happen if the same CYBY23 conversation occurred in a more anonymous, peer-driven environment.",
    },
    "Stronger intervention/moderation": {
        "anonymity_level": 0.35,
        "peer_influence_strength": 0.45,
        "learning_rate": 0.45,
        "learning_strength": 0.65,
        "steps": 25,
        "description": "Ask what could happen if the same CYBY23 conversation had stronger reporting/moderation feedback.",
    },
}


st.set_page_config(
    page_title="CYBY23 Dataset-Led Cyberbystander Simulation",
    page_icon="🧪",
    layout="wide",
)


@st.cache_data(show_spinner=False)
def cached_threads(dataset_path: str):
    return load_cyby23_threads(dataset_path)


def role_distribution_table(threads) -> pd.DataFrame:
    rows = []
    for role in NORMALIZED_ROLE_ORDER:
        count = sum(thread.observed_role_distribution.get(role, 0) for thread in threads)
        rows.append(
            {
                "CYBY23 role": role,
                "What it means": ROLE_EXPLANATIONS[role],
                "Labelled replies": count,
            }
        )
    return pd.DataFrame(rows)


def action_mapping_table() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "Observed CYBY23 role": "reinforce",
                "Simulation behaviour": "reinforce",
                "Meaning": "The bystander adds support to the harmful post.",
            },
            {
                "Observed CYBY23 role": "defend",
                "Simulation behaviour": "defend",
                "Meaning": "The bystander pushes back or supports the target.",
            },
            {
                "Observed CYBY23 role": "neutral",
                "Simulation behaviour": "ignore",
                "Meaning": "The bystander stays silent or avoids taking a side.",
            },
            {
                "Observed CYBY23 role": "unrelated",
                "Simulation behaviour": "ignore",
                "Meaning": "The bystander is present but does not affect the main conflict.",
            },
            {
                "Observed CYBY23 role": "not directly labelled",
                "Simulation behaviour": "report",
                "Meaning": "A latent intervention option added by the model because CYBY23 does not directly label reporting.",
            },
        ]
    )


def top_thread_options(threads, limit: int = 12) -> list:
    return sorted(threads, key=lambda thread: len(thread.bystanders), reverse=True)[:limit]


def selected_strategy_values(strategy_name: str) -> dict[str, float | str]:
    return STRATEGY_PRESETS[strategy_name]


def observed_thread_table(thread) -> pd.DataFrame:
    role_counts = thread.observed_role_distribution
    return pd.DataFrame(
        [
            {
                "Dataset-derived value": "Observed bystander replies",
                "Value": len(thread.bystanders),
                "Where it comes from": "CYBY23 labelled replies in this thread",
            },
            {
                "Dataset-derived value": "Risk level",
                "Value": thread.risk_level,
                "Where it comes from": "Source-post toxicity compared with CYBY23 thread distribution",
            },
            {
                "Dataset-derived value": "Reinforcing replies",
                "Value": role_counts.get("reinforce", 0),
                "Where it comes from": "CYBY23 bystander role labels",
            },
            {
                "Dataset-derived value": "Defending replies",
                "Value": role_counts.get("defend", 0),
                "Where it comes from": "CYBY23 bystander role labels",
            },
            {
                "Dataset-derived value": "Neutral/silent replies",
                "Value": role_counts.get("neutral", 0),
                "Where it comes from": "CYBY23 bystander role labels",
            },
            {
                "Dataset-derived value": "Unrelated replies",
                "Value": role_counts.get("unrelated", 0),
                "Where it comes from": "CYBY23 bystander role labels",
            },
            {
                "Dataset-derived value": "Source toxicity",
                "Value": f"{thread.source_toxicity:.2f}",
                "Where it comes from": "CYBY23 source-post toxicity feature",
            },
            {
                "Dataset-derived value": "Source identity attack",
                "Value": f"{thread.source_identity_attack:.2f}",
                "Where it comes from": "CYBY23 source-post identity-attack feature",
            },
        ]
    )


def assumptions_table(strategy_name: str, values: dict[str, float | str]) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "Modelling assumption": "Future interaction rounds",
                "Value": int(values["steps"]),
                "Why it is not from CYBY23": "CYBY23 records observed replies, not future simulated rounds.",
            },
            {
                "Modelling assumption": "Assumed platform anonymity",
                "Value": f"{float(values['anonymity_level']):.2f}",
                "Why it is not from CYBY23": "The dataset does not directly measure platform anonymity.",
            },
            {
                "Modelling assumption": "Assumed peer pressure strength",
                "Value": f"{float(values['peer_influence_strength']):.2f}",
                "Why it is not from CYBY23": "Peer influence is simulated from observed role patterns, not directly measured.",
            },
            {
                "Modelling assumption": "Agent adaptation speed",
                "Value": f"{float(values['learning_rate']):.2f}",
                "Why it is not from CYBY23": "Learning rate controls simulated future adaptation.",
            },
            {
                "Modelling assumption": "CYBY23 starting-pattern strength",
                "Value": f"{float(values['learning_strength']):.2f}",
                "Why it is not from CYBY23": "This controls how strongly observed labels anchor simulated agents.",
            },
            {
                "Modelling assumption": "Scenario being tested",
                "Value": strategy_name,
                "Why it is not from CYBY23": "This is a scenario comparison chosen by the user.",
            },
        ]
    )


def outcome_interpretation(outcome: str) -> str:
    if outcome == "Escalated":
        return (
            "The conversation moved toward a worse outcome. In this run, harmful pressure "
            "from reinforcement, silence, anonymity, or content risk outweighed defending/reporting."
        )
    if outcome == "De-escalated":
        return (
            "The conversation calmed down. In this run, defending and reporting pressure was strong "
            "enough to reduce the simulated bullying level."
        )
    return (
        "The conversation stayed unresolved. No behaviour pattern fully dominated within the selected steps."
    )


def action_share_sentence(time_series: pd.DataFrame) -> str:
    totals = time_series[ACTIONS].sum().to_dict()
    total_actions = max(1, sum(totals.values()))
    ranked = sorted(totals.items(), key=lambda item: item[1], reverse=True)
    top_action, top_count = ranked[0]
    return (
        f"Across the full run, the most common simulated behaviour was "
        f"`{ACTION_LABELS[top_action]}` with {top_count / total_actions:.0%} of all simulated actions."
    )


def thread_label(thread) -> str:
    source_preview = " ".join(thread.source_text.split())[:80]
    return f"{thread.thread_id} | {len(thread.bystanders)} replies | {thread.risk_level} risk | {source_preview}"


st.title("CYBY23 Dataset-Led Cyberbystander Simulation")
st.write(
    "This page is designed for a user who does not want to tune a technical model manually. "
    "Pick a real CYBY23 conversation, choose a simple scenario strategy, and run the simulation to see how bystander behaviour may affect escalation."
)

st.warning(
    "CYBY23 provides the observed thread, toxicity context, and bystander role labels. "
    "Anonymity, future interaction rounds, and learning speed are modelling assumptions used only for scenario testing."
)

with st.sidebar:
    st.header("1. Choose the data")
    dataset_path = st.text_input("CYBY23 dataset path", value=DEFAULT_DATASET_PATH)

    try:
        all_threads = cached_threads(dataset_path)
        dataset_ready = True
    except Exception as exc:
        st.error(f"Dataset could not be loaded: {exc}")
        all_threads = []
        dataset_ready = False

    if not dataset_ready:
        st.stop()

    risk_filter = st.selectbox(
        "Conversation risk group",
        ["all", "low", "medium", "high"],
        index=0,
        help="Use this to focus on all CYBY23 threads or only a risk category based on source-post toxicity.",
    )
    filtered_threads = filter_threads_by_risk(all_threads, risk_filter) or all_threads
    recommended_threads = top_thread_options(filtered_threads)
    selected_thread = st.selectbox(
        "Real CYBY23 conversation",
        recommended_threads,
        index=0,
        format_func=thread_label,
        help="The list is sorted so larger conversations appear first. Larger threads are usually easier to demonstrate.",
    )

    st.header("2. Choose what to test")
    strategy_name = st.radio(
        "Scenario",
        list(STRATEGY_PRESETS),
        index=0,
        captions=[STRATEGY_PRESETS[name]["description"] for name in STRATEGY_PRESETS],
    )
    strategy_values = selected_strategy_values(strategy_name)
    steps = int(strategy_values["steps"])
    anonymity_level = float(strategy_values["anonymity_level"])
    peer_influence_strength = float(strategy_values["peer_influence_strength"])
    learning_rate = float(strategy_values["learning_rate"])
    learning_strength = float(strategy_values["learning_strength"])
    seed = 17

    with st.expander("Advanced settings", expanded=False):
        st.caption(
            "These settings are assumptions for the simulation. They are not directly observed in CYBY23."
        )
        steps = st.slider(
            "Future interaction rounds",
            5,
            60,
            int(strategy_values["steps"]),
            5,
            help="How many future rounds the model simulates after the observed CYBY23 thread state.",
        )
        anonymity_level = st.slider(
            "Assumed platform anonymity",
            0.0,
            1.0,
            float(strategy_values["anonymity_level"]),
            0.05,
            help="CYBY23 does not directly measure anonymity. This lets us test a scenario assumption.",
        )
        peer_influence_strength = st.slider(
            "Assumed peer pressure strength",
            0.0,
            1.0,
            float(strategy_values["peer_influence_strength"]),
            0.05,
            help="Controls how strongly agents react to what other simulated bystanders are doing.",
        )
        learning_rate = st.slider(
            "Agent adaptation speed",
            0.0,
            1.0,
            float(strategy_values["learning_rate"]),
            0.05,
            help="Controls how quickly simulated agents adapt after an action makes the situation better or worse.",
        )
        learning_strength = st.slider(
            "CYBY23 starting-pattern strength",
            0.0,
            2.0,
            float(strategy_values["learning_strength"]),
            0.05,
            help="Controls how strongly observed CYBY23 labels anchor the simulated agents' initial choices.",
        )
        seed = st.number_input("Random seed", min_value=1, max_value=99999, value=17, step=1)

    st.header("3. Run")
    run_button = st.button("Run Simulation", type="primary", width="stretch")

active_assumptions = {
    "steps": steps,
    "anonymity_level": anonymity_level,
    "peer_influence_strength": peer_influence_strength,
    "learning_rate": learning_rate,
    "learning_strength": learning_strength,
}

st.subheader("What this simulation helps a user understand")
benefit_cols = st.columns(3)
benefit_cols[0].metric("Dataset threads loaded", len(all_threads))
benefit_cols[1].metric("Threads in selected risk group", len(filtered_threads))
benefit_cols[2].metric("Selected thread replies", len(selected_thread.bystanders))

st.markdown(
    """
    The benefit is that the user can start from a real CYBY23 conversation and ask a clear scenario question.
    For example: *If this same observed bystander mix continued interacting, would the simulated conversation escalate,
    de-escalate, or stay unresolved?* The scenario buttons let the user compare assumptions without manually tuning parameters.
    """
)

data_col, assumption_col = st.columns((1.15, 1))
with data_col:
    st.subheader("What is taken from CYBY23")
    st.dataframe(observed_thread_table(selected_thread), hide_index=True, width="stretch")
with assumption_col:
    st.subheader("What is a modelling assumption")
    st.dataframe(assumptions_table(strategy_name, active_assumptions), hide_index=True, width="stretch")

overview_col, mapping_col = st.columns((1.2, 1))
with overview_col:
    st.subheader("CYBY23 role distribution in the selected risk group")
    st.dataframe(role_distribution_table(filtered_threads), hide_index=True, width="stretch")
with mapping_col:
    st.subheader("How labels become simulation actions")
    st.dataframe(action_mapping_table(), hide_index=True, width="stretch")

if run_button or "guided_cyby23_result" not in st.session_state:
    config = CYBY23SimulationConfig(
        dataset_path=dataset_path,
        thread_id=selected_thread.thread_id,
        risk_filter=risk_filter,
        steps=steps,
        anonymity_level=anonymity_level,
        peer_influence_strength=peer_influence_strength,
        learning_rate=learning_rate,
        learning_strength=learning_strength,
        seed=int(seed),
    )
    with st.spinner("Running the dataset-led agent simulation..."):
        st.session_state["guided_cyby23_result"] = run_cyby23_simulation(config)
        st.session_state["guided_cyby23_strategy"] = strategy_name

result = st.session_state["guided_cyby23_result"]
time_series = result.time_series
agents = result.agent_snapshot

st.divider()
st.subheader("Simulation result")
result_cols = st.columns(4)
result_cols[0].metric("Outcome", result.final_outcome)
result_cols[1].metric("Final bullying level", f"{time_series.iloc[-1]['bullying_level']:.1f}/100")
result_cols[2].metric("Strategy tested", st.session_state.get("guided_cyby23_strategy", strategy_name))
result_cols[3].metric("CYBY23 thread", result.thread.thread_id)

st.write(outcome_interpretation(result.final_outcome))
st.write(action_share_sentence(time_series))
st.write(result.explanation)

with st.expander("Read the selected CYBY23 source post", expanded=False):
    st.write(result.thread.source_text)

chart_col, action_col = st.columns((1.2, 1))
with chart_col:
    st.subheader("Bullying level over time")
    st.line_chart(time_series.set_index("step")[["bullying_level"]], height=320)
with action_col:
    st.subheader("Bystander actions over time")
    st.line_chart(time_series.set_index("step")[ACTIONS], height=320)

final_cols = st.columns((1, 1))
with final_cols[0]:
    st.subheader("Final bystander behaviour")
    final_action_counts = (
        agents["last_action"]
        .map(ACTION_LABELS)
        .value_counts()
        .rename_axis("Final behaviour")
        .reset_index(name="Agents")
    )
    st.dataframe(final_action_counts, hide_index=True, width="stretch")
with final_cols[1]:
    st.subheader("What to take away")
    if result.final_outcome == "Escalated":
        st.write(
            "A useful next test is to choose `Stronger intervention/moderation` and compare whether the simulated bullying level changes direction."
        )
    elif result.final_outcome == "De-escalated":
        st.write(
            "This run suggests that protective actions were strong enough to reduce harm in the model. Try `More anonymous platform` to stress-test that result."
        )
    else:
        st.write(
            "The result is mixed. Try changing the risk group or strategy to see what conditions push the same dataset-led agents toward escalation or de-escalation."
        )

with st.expander("Inspect and export the data", expanded=False):
    st.markdown("**Simulation time series**")
    st.dataframe(time_series, hide_index=True, width="stretch")
    st.download_button(
        "Download time series CSV",
        time_series.to_csv(index=False).encode("utf-8"),
        "cyby23_guided_simulation_timeseries.csv",
        "text/csv",
        width="stretch",
    )
    st.markdown("**Final agent snapshot**")
    st.dataframe(agents, hide_index=True, width="stretch")
    st.download_button(
        "Download final agent snapshot CSV",
        agents.to_csv(index=False).encode("utf-8"),
        "cyby23_guided_agent_snapshot.csv",
        "text/csv",
        width="stretch",
    )
