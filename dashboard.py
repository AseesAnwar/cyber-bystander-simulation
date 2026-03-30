from __future__ import annotations

import io
import os
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib")

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from model import simulate_thread
from preprocess_cyby23 import (
    DEFAULT_DATASET_PATH,
    NORMALIZED_ROLE_ORDER,
    build_thread_records,
    clean_dataset,
    load_raw_dataset,
    preprocessing_summary,
    resolve_dataset_path,
)
from run_simulation import build_confusion_style_table, build_distribution_comparison, run_across_threads


st.set_page_config(
    page_title="CYBY23 Online Conversation Simulator",
    page_icon="🧭",
    layout="wide",
)

ROLE_COLORS = {
    "reinforce": "#c2410c",
    "defend": "#0f766e",
    "neutral": "#64748b",
    "unrelated": "#7c3aed",
}

PLAIN_ROLE_LABELS = {
    "reinforce": "Support the harmful post",
    "defend": "Push back against it",
    "neutral": "Stay neutral",
    "unrelated": "Say something unrelated",
}

SCENARIO_OPTIONS = {
    "all": "All conversations",
    "low": "Less harmful",
    "medium": "Mixed",
    "high": "More harmful",
}


@st.cache_data(show_spinner=False)
def load_threads(dataset_path: str) -> tuple[Path, list, dict[str, object]]:
    resolved_path = resolve_dataset_path(dataset_path)
    raw_df = load_raw_dataset(resolved_path)
    cleaned_df = clean_dataset(raw_df)
    thread_records = build_thread_records(cleaned_df)
    summary = preprocessing_summary(cleaned_df)
    return resolved_path, thread_records, summary


@st.cache_data(show_spinner=False)
def run_batch(dataset_path: str, scenario_mode: str, max_threads: int | None, seed: int, learning_mode: bool):
    return run_across_threads(
        dataset_path=dataset_path,
        scenario_mode=scenario_mode,
        max_threads=max_threads,
        seed=seed,
        learning_mode=learning_mode,
    )


@st.cache_data(show_spinner=False)
def run_single_conversation(
    dataset_path: str,
    conversation_id: str,
    seed: int,
    learning_mode: bool,
):
    _, conversation_records, _ = load_threads(dataset_path)
    selected = next(record for record in conversation_records if record.thread_id == conversation_id)
    model, result = simulate_thread(selected, seed=seed, learning_mode=learning_mode, learner_registry={})
    return selected, model.get_model_frame(), model.get_action_history_frame(), result


def dataframe_to_csv_bytes(df: pd.DataFrame) -> bytes:
    buffer = io.StringIO()
    df.to_csv(buffer, index=False)
    return buffer.getvalue().encode("utf-8")


def rename_role(role: str) -> str:
    return PLAIN_ROLE_LABELS.get(role, role)


def metric_help() -> dict[str, str]:
    return {
        "conversations": "How many separate online conversations are included in this run.",
        "accuracy": "How often the model matched the real reply type in the labelled data.",
        "hostility": "How much the conversation becomes more hostile as replies unfold.",
        "pushback": "How much people push back against the harmful original post.",
        "replies": "How many labelled replies from real data are included in the dataset being used.",
        "harm": "How toxic or hostile the original post appears.",
        "moderation": "Whether the model thinks the conversation would likely be flagged for moderation.",
        "repeat": "Keeps the same random choices so you can compare results fairly.",
        "learning_mode": "Turns on simplified Theory of Mind, reinforcement learning, and continual learning memory.",
        "reward": "A simple learning signal that rewards harmful reinforcement when hostility grows and rewards defence when hostility falls.",
    }


def build_distribution_figure(comparison_df: pd.DataFrame, title: str):
    fig, ax = plt.subplots(figsize=(7, 4))
    x = range(len(comparison_df))
    width = 0.35
    ax.bar(
        [value - width / 2 for value in x],
        comparison_df["observed"],
        width=width,
        label="Real data",
        color="#1d4ed8",
    )
    ax.bar(
        [value + width / 2 for value in x],
        comparison_df["simulated"],
        width=width,
        label="Model prediction",
        color="#f97316",
    )
    ax.set_xticks(list(x))
    ax.set_xticklabels([rename_role(role) for role in comparison_df["role"]], rotation=12, ha="right")
    ax.set_ylabel("Number of replies")
    ax.set_title(title)
    ax.legend()
    fig.tight_layout()
    return fig


def build_conversation_scatter_figure(results_df: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(7, 4))
    scatter = ax.scatter(
        results_df["source_toxicity"],
        results_df["escalation_score"],
        c=results_df["defence_score"],
        cmap="viridis",
        edgecolors="black",
        alpha=0.85,
    )
    ax.set_xlabel("Harm level of original post")
    ax.set_ylabel("How much the conversation becomes more hostile")
    ax.set_title("Do more harmful posts lead to worse conversations?")
    color_bar = fig.colorbar(scatter, ax=ax)
    color_bar.set_label("How much people push back")
    fig.tight_layout()
    return fig


def build_conversation_role_figure(conversation_record, result):
    real_counts = [conversation_record.observed_role_distribution.get(role, 0) for role in NORMALIZED_ROLE_ORDER]
    predicted_counts = [result.simulated_counts.get(role, 0) for role in NORMALIZED_ROLE_ORDER]
    fig, ax = plt.subplots(figsize=(7, 4))
    x = range(len(NORMALIZED_ROLE_ORDER))
    width = 0.35
    ax.bar([value - width / 2 for value in x], real_counts, width=width, color="#2563eb", label="Real data")
    ax.bar([value + width / 2 for value in x], predicted_counts, width=width, color="#ea580c", label="Model prediction")
    ax.set_xticks(list(x))
    ax.set_xticklabels([rename_role(role) for role in NORMALIZED_ROLE_ORDER], rotation=12, ha="right")
    ax.set_ylabel("Number of replies")
    ax.set_title("What happened in this conversation?")
    ax.legend()
    fig.tight_layout()
    return fig


def build_action_sequence_figure(action_history_df: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(8, 4))
    for role in NORMALIZED_ROLE_ORDER:
        role_df = action_history_df[action_history_df["simulated_role"] == role]
        if role_df.empty:
            continue
        ax.scatter(
            role_df["step"],
            [rename_role(role)] * len(role_df),
            color=ROLE_COLORS[role],
            label=rename_role(role),
            s=80,
            alpha=0.85,
        )
    ax.set_xlabel("Order of replies")
    ax.set_ylabel("What each person did")
    ax.set_title("What each person did as the conversation unfolded")
    handles, labels = ax.get_legend_handles_labels()
    unique = dict(zip(labels, handles))
    ax.legend(unique.values(), unique.keys(), loc="upper right")
    fig.tight_layout()
    return fig


def build_q_value_figure(results_df: pd.DataFrame):
    averages = [results_df[f"avg_q_{role}"].mean() for role in NORMALIZED_ROLE_ORDER]
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.bar(
        [rename_role(role) for role in NORMALIZED_ROLE_ORDER],
        averages,
        color=[ROLE_COLORS[role] for role in NORMALIZED_ROLE_ORDER],
    )
    ax.set_ylabel("Average learned value")
    ax.set_title("Average Q-values by reply type")
    ax.tick_params(axis="x", rotation=12)
    fig.tight_layout()
    return fig


def build_learning_progress_figure(action_history_df: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(7, 4))
    progress = (
        action_history_df.groupby("step")[["reward"]]
        .mean()
        .rename(columns={"reward": "mean_reward"})
        .reset_index()
    )
    ax.plot(progress["step"], progress["mean_reward"], marker="o", color="#0f766e")
    ax.axhline(0.0, color="#94a3b8", linestyle="--", linewidth=1)
    ax.set_xlabel("Simulation step")
    ax.set_ylabel("Average reward")
    ax.set_title("Learning progress over simulation steps")
    fig.tight_layout()
    return fig


def build_action_distribution_over_time_figure(action_history_df: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(8, 4))
    counts = (
        action_history_df.groupby(["step", "simulated_role"])
        .size()
        .unstack(fill_value=0)
        .reindex(columns=NORMALIZED_ROLE_ORDER, fill_value=0)
    )
    for role in NORMALIZED_ROLE_ORDER:
        ax.plot(
            counts.index,
            counts[role],
            marker="o",
            label=rename_role(role),
            color=ROLE_COLORS[role],
        )
    ax.set_xlabel("Simulation step")
    ax.set_ylabel("Replies of each type")
    ax.set_title("Distribution of reply types over time")
    ax.legend()
    fig.tight_layout()
    return fig


def build_before_after_figure(baseline_comparison_df: pd.DataFrame, learning_comparison_df: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(8, 4))
    x = range(len(NORMALIZED_ROLE_ORDER))
    width = 0.25
    baseline_values = baseline_comparison_df["simulated"].tolist()
    learning_values = learning_comparison_df["simulated"].tolist()
    real_values = baseline_comparison_df["observed"].tolist()
    ax.bar([value - width for value in x], real_values, width=width, label="Real data", color="#1d4ed8")
    ax.bar(x, baseline_values, width=width, label="Before learning", color="#94a3b8")
    ax.bar([value + width for value in x], learning_values, width=width, label="After learning", color="#f97316")
    ax.set_xticks(list(x))
    ax.set_xticklabels([rename_role(role) for role in NORMALIZED_ROLE_ORDER], rotation=12, ha="right")
    ax.set_ylabel("Number of replies")
    ax.set_title("Before vs after learning")
    ax.legend()
    fig.tight_layout()
    return fig


def interpret_distribution_chart(comparison_df: pd.DataFrame) -> str:
    comparison_df = comparison_df.copy()
    comparison_df["gap"] = comparison_df["simulated"] - comparison_df["observed"]
    biggest_gap = comparison_df.iloc[comparison_df["gap"].abs().idxmax()]
    role = rename_role(biggest_gap["role"]).lower()
    if biggest_gap["gap"] > 0:
        return f"In this run, the model predicted more replies that {role} than appeared in the real data."
    if biggest_gap["gap"] < 0:
        return f"In this run, the model predicted fewer replies that {role} than appeared in the real data."
    return "In this run, the model stayed very close to the real reply mix."


def interpret_scatter_chart(results_df: pd.DataFrame) -> str:
    high_harm = results_df[results_df["source_toxicity"] >= results_df["source_toxicity"].median()]
    low_harm = results_df[results_df["source_toxicity"] < results_df["source_toxicity"].median()]
    if high_harm.empty or low_harm.empty:
        return "This chart compares how the starting harm level relates to how the conversation develops."
    if high_harm["escalation_score"].mean() > low_harm["escalation_score"].mean():
        return "In this run, more harmful starting posts were more likely to lead to worse conversations."
    return "In this run, more harmful starting posts did not clearly lead to worse conversations."


def interpret_conversation_chart(conversation_record, result) -> str:
    real_top = max(conversation_record.observed_role_distribution, key=conversation_record.observed_role_distribution.get)
    predicted_top = max(result.simulated_counts, key=result.simulated_counts.get)
    if real_top == predicted_top:
        return f"For this example, the model got the main reply pattern right: most people {rename_role(real_top).lower()}."
    return (
        f"For this example, the real data mostly showed people who {rename_role(real_top).lower()}, "
        f"but the model mostly predicted people who {rename_role(predicted_top).lower()}."
    )


def summarize_conversation(conversation_record, result, learning_mode: bool) -> str:
    real_counts = conversation_record.observed_role_distribution
    predicted_counts = result.simulated_counts
    real_top = max(real_counts, key=real_counts.get)
    predicted_top = max(predicted_counts, key=predicted_counts.get)
    harm_text = (
        "started with a more harmful post"
        if conversation_record.source_toxicity >= 0.66
        else "started with a less harmful post"
        if conversation_record.source_toxicity < 0.33
        else "started with a mixed-severity post"
    )
    summary = f"This conversation {harm_text}. In the real data, most people {rename_role(real_top).lower()}."
    if real_top == predicted_top:
        summary += " The model predicted a similar main pattern."
    else:
        summary += f" The model predicted more people would {rename_role(predicted_top).lower()}."
    if learning_mode:
        summary += " In learning mode, agents also form simple beliefs about the situation, update their Q-values, and remember recent outcomes."
    return summary


def interpret_q_values(results_df: pd.DataFrame) -> str:
    average_q = {role: results_df[f"avg_q_{role}"].mean() for role in NORMALIZED_ROLE_ORDER}
    best_role = max(average_q, key=average_q.get)
    return f"Across this run, the learning system assigned the highest average value to replies that {rename_role(best_role).lower()}."


def interpret_learning_progress(action_history_df: pd.DataFrame) -> str:
    progress = action_history_df.groupby("step")["reward"].mean().reset_index()
    if progress.empty:
        return "No learning updates were recorded in this run."
    if progress["reward"].iloc[-1] > progress["reward"].iloc[0]:
        return "The average reward improved over the simulation steps, suggesting the agents were moving toward actions they found more useful."
    return "The average reward did not clearly improve over the simulation steps, suggesting learning stayed modest in this run."


def interpret_before_after(baseline_results_df: pd.DataFrame, learning_results_df: pd.DataFrame) -> str:
    baseline_accuracy = baseline_results_df["accuracy"].mean()
    learning_accuracy = learning_results_df["accuracy"].mean()
    if learning_accuracy > baseline_accuracy:
        return "After learning was enabled, the model matched the real reply labels more often than the baseline version."
    if learning_accuracy < baseline_accuracy:
        return "In this run, learning did not improve agreement with the real reply labels."
    return "In this run, learning and the baseline produced similar agreement with the real reply labels."


st.title("CYBY23 Online Conversation Simulator")
st.caption(
    "This tool shows how people reacted to a harmful online post in real data, and how our simulation predicts they might react. It helps us test whether our model behaves realistically."
)

with st.sidebar:
    st.header("Choose what to explore")
    dataset_path = st.text_input(
        "Data file",
        value=DEFAULT_DATASET_PATH,
        help="Location of the CYBY23 spreadsheet. If the default file is not available, the app uses the local copy found on this machine.",
    )
    scenario_label = st.selectbox(
        "Conversation type",
        list(SCENARIO_OPTIONS.values()),
        index=0,
        help="Filter to conversations that begin with less harmful, mixed, or more harmful original posts.",
    )
    scenario_mode = next(key for key, value in SCENARIO_OPTIONS.items() if value == scenario_label)
    max_threads = st.slider(
        "Number of conversations",
        min_value=5,
        max_value=90,
        value=20,
        step=5,
        help=metric_help()["conversations"],
    )
    seed = st.number_input(
        "Repeat setting",
        min_value=0,
        max_value=100000,
        value=11,
        step=1,
        help=metric_help()["repeat"],
    )
    enable_learning = st.toggle(
        "Enable Learning Mode (ToM + RL + CL)",
        value=False,
        help=metric_help()["learning_mode"],
    )
    st.caption("Use the same repeat setting if you want the same result again.")
    run_button = st.button("Update view", type="primary", use_container_width=True)

if run_button or "results_df" not in st.session_state:
    resolved_path, conversation_records, dataset_summary = load_threads(dataset_path)
    results_df, actions_df, summary, _ = run_batch(
        dataset_path=dataset_path,
        scenario_mode=scenario_mode,
        max_threads=max_threads,
        seed=int(seed),
        learning_mode=enable_learning,
    )
    comparison_df = build_distribution_comparison(results_df)
    confusion_df = build_confusion_style_table(actions_df)

    baseline_results_df = baseline_actions_df = baseline_summary = baseline_comparison_df = None
    if enable_learning:
        baseline_results_df, baseline_actions_df, baseline_summary, _ = run_batch(
            dataset_path=dataset_path,
            scenario_mode=scenario_mode,
            max_threads=max_threads,
            seed=int(seed),
            learning_mode=False,
        )
        baseline_comparison_df = build_distribution_comparison(baseline_results_df)

    st.session_state["resolved_path"] = str(resolved_path)
    st.session_state["conversation_records"] = conversation_records
    st.session_state["dataset_summary"] = dataset_summary
    st.session_state["results_df"] = results_df
    st.session_state["actions_df"] = actions_df
    st.session_state["summary"] = summary
    st.session_state["comparison_df"] = comparison_df
    st.session_state["confusion_df"] = confusion_df
    st.session_state["scenario_mode"] = scenario_mode
    st.session_state["seed"] = int(seed)
    st.session_state["dataset_path"] = dataset_path
    st.session_state["enable_learning"] = enable_learning
    st.session_state["baseline_results_df"] = baseline_results_df
    st.session_state["baseline_actions_df"] = baseline_actions_df
    st.session_state["baseline_summary"] = baseline_summary
    st.session_state["baseline_comparison_df"] = baseline_comparison_df

resolved_path = st.session_state["resolved_path"]
conversation_records = st.session_state["conversation_records"]
dataset_summary = st.session_state["dataset_summary"]
results_df = st.session_state["results_df"]
actions_df = st.session_state["actions_df"]
summary = st.session_state["summary"]
comparison_df = st.session_state["comparison_df"]
confusion_df = st.session_state["confusion_df"]
current_seed = st.session_state["seed"]
current_dataset_path = st.session_state["dataset_path"]
enable_learning = st.session_state["enable_learning"]
baseline_results_df = st.session_state["baseline_results_df"]
baseline_actions_df = st.session_state["baseline_actions_df"]
baseline_summary = st.session_state["baseline_summary"]
baseline_comparison_df = st.session_state["baseline_comparison_df"]

st.info(f"Using data from: `{resolved_path}`")

st.subheader("A. What this tool does")
st.write(
    "This page compares real reply behaviour from the CYBY23 dataset with the reply behaviour predicted by the simulator. "
    "You can first look at the big picture, then open one example conversation to see how the model behaves step by step."
)
with st.container(border=True):
    st.markdown("**How to read this page**")
    st.write("1. Start with the summary numbers to see the overall pattern.")
    st.write("2. Compare real replies with model predictions in the charts.")
    st.write("3. If learning mode is on, look at how Q-values and rewards change over time.")
    st.write("4. Inspect one example conversation to see what happened in detail.")

st.subheader("B. What data is being used")
data_col1, data_col2 = st.columns((1, 1))
with data_col1:
    st.write(
        f"The app is using `{dataset_summary['source_posts']}` original posts and "
        f"`{dataset_summary['labelled_bystander_replies']}` labelled replies from the CYBY23 dataset."
    )
    st.dataframe(
        pd.DataFrame(
            {
                "Reply type in plain English": [rename_role(role) for role in NORMALIZED_ROLE_ORDER],
                "Count in real data": [
                    dataset_summary["normalized_role_counts"].get(role, 0) for role in NORMALIZED_ROLE_ORDER
                ],
            }
        ),
        use_container_width=True,
        hide_index=True,
    )
with data_col2:
    st.write(
        "The simulator focuses on conversations that begin with a harmful post and then models how people replying might respond."
    )
    if enable_learning:
        st.write(
            "Learning mode adds three simple ideas: agents infer what is happening, learn from rewards, and remember recent outcomes."
        )
    else:
        st.write("Baseline mode uses transparent rules without learning.")

st.subheader("C. Overall results")
metric_cols = st.columns(6 if enable_learning else 5)
metric_cols[0].metric("Conversations simulated", int(summary["simulated_threads"]), help=metric_help()["conversations"])
metric_cols[1].metric("Match with real data", f"{summary['mean_accuracy']:.3f}", help=metric_help()["accuracy"])
metric_cols[2].metric(
    "How much conversations become more hostile",
    f"{summary['mean_escalation_score']:.3f}",
    help=metric_help()["hostility"],
)
metric_cols[3].metric(
    "How much people push back",
    f"{summary['mean_defence_score']:.3f}",
    help=metric_help()["pushback"],
)
metric_cols[4].metric(
    "Labelled replies available",
    int(dataset_summary["labelled_bystander_replies"]),
    help=metric_help()["replies"],
)
if enable_learning:
    metric_cols[5].metric("Average learning reward", f"{summary['mean_reward']:.3f}", help=metric_help()["reward"])
st.caption("These summary numbers give a quick view of how the model behaved across all conversations in this run.")

st.subheader("D. Real behaviour vs model behaviour")
comparison_col, pattern_col = st.columns((1, 1))
with comparison_col:
    st.pyplot(build_distribution_figure(comparison_df, "Real replies vs predicted replies"), use_container_width=True)
    st.caption(interpret_distribution_chart(comparison_df))
with pattern_col:
    st.pyplot(build_conversation_scatter_figure(results_df), use_container_width=True)
    st.caption(interpret_scatter_chart(results_df))

if enable_learning and baseline_results_df is not None and baseline_comparison_df is not None:
    st.subheader("Learning mode comparison")
    learning_col1, learning_col2 = st.columns((1, 1))
    with learning_col1:
        st.pyplot(build_before_after_figure(baseline_comparison_df, comparison_df), use_container_width=True)
        st.caption(interpret_before_after(baseline_results_df, results_df))
    with learning_col2:
        st.pyplot(build_q_value_figure(results_df), use_container_width=True)
        st.caption(interpret_q_values(results_df))

    learning_col3, learning_col4 = st.columns((1, 1))
    with learning_col3:
        st.pyplot(build_learning_progress_figure(actions_df), use_container_width=True)
        st.caption(interpret_learning_progress(actions_df))
    with learning_col4:
        st.pyplot(build_action_distribution_over_time_figure(actions_df), use_container_width=True)
        st.caption("This chart shows how the mix of reply types changed as the simulated conversations unfolded.")

st.subheader("E. Example conversation walkthrough")
filtered_conversation_ids = results_df["thread_id"].tolist()
conversation_lookup = {
    record.thread_id: record for record in conversation_records if record.thread_id in filtered_conversation_ids
}
selected_conversation_id = st.selectbox(
    "Choose one conversation to inspect",
    filtered_conversation_ids,
    index=0,
    format_func=lambda value: (
        f"{value} | {SCENARIO_OPTIONS.get(conversation_lookup[value].risk_level, conversation_lookup[value].risk_level)}"
        f" | {len(conversation_lookup[value].bystanders)} people replying"
    ),
    help="Pick one conversation so you can compare the real replies with the model's predicted replies.",
)

selected_conversation, model_frame, action_history_df, conversation_result = run_single_conversation(
    dataset_path=current_dataset_path,
    conversation_id=selected_conversation_id,
    seed=current_seed,
    learning_mode=enable_learning,
)

conversation_metric_cols = st.columns(5 if enable_learning else 4)
conversation_metric_cols[0].metric(
    "Harm level of original post",
    f"{selected_conversation.source_toxicity:.3f}",
    help=metric_help()["harm"],
)
conversation_metric_cols[1].metric(
    "How much the conversation becomes more hostile",
    f"{conversation_result.escalation_score:.3f}",
    help=metric_help()["hostility"],
)
conversation_metric_cols[2].metric(
    "How much people push back",
    f"{conversation_result.defence_score:.3f}",
    help=metric_help()["pushback"],
)
conversation_metric_cols[3].metric(
    "Would the system flag this conversation for moderation?",
    "Yes" if conversation_result.moderator_triggered else "No",
    help=metric_help()["moderation"],
)
if enable_learning:
    conversation_metric_cols[4].metric(
        "Average reward in this conversation",
        f"{conversation_result.mean_reward:.3f}",
        help=metric_help()["reward"],
    )

st.write(summarize_conversation(selected_conversation, conversation_result, enable_learning))

conversation_chart_col, sequence_col = st.columns((1, 1))
with conversation_chart_col:
    st.pyplot(build_conversation_role_figure(selected_conversation, conversation_result), use_container_width=True)
    st.caption(interpret_conversation_chart(selected_conversation, conversation_result))
with sequence_col:
    st.pyplot(build_action_sequence_figure(action_history_df), use_container_width=True)
    st.caption("This shows the model's predicted reply type for each person in the order they appeared in the conversation.")

st.markdown("**Original post**")
st.write(selected_conversation.source_text)
st.caption("This is the starting message that the rest of the conversation responds to.")

st.subheader("Why this matters")
st.write(
    "This prototype helps us test assumptions about online bystander behaviour before building more advanced AI models. "
    "It gives us a baseline we can improve later."
)

with st.expander("F. Advanced tables for detailed inspection", expanded=False):
    st.write("This section keeps the technical detail available for academic review without overwhelming the main page.")
    st.markdown("**Where the model matched or mismatched real reply types**")
    st.dataframe(confusion_df, use_container_width=True)
    st.caption("Rows show the real reply type, and columns show what the model predicted instead.")

    st.markdown("**Conversation-by-conversation results**")
    st.dataframe(results_df, use_container_width=True)
    st.download_button(
        "Download conversation results CSV",
        data=dataframe_to_csv_bytes(results_df),
        file_name="conversation_results.csv",
        mime="text/csv",
        use_container_width=True,
    )

    st.markdown("**Step-by-step model actions for the selected conversation**")
    st.dataframe(action_history_df, use_container_width=True)
    st.download_button(
        "Download selected conversation action history CSV",
        data=dataframe_to_csv_bytes(action_history_df),
        file_name=f"conversation_{selected_conversation_id}_action_history.csv",
        mime="text/csv",
        use_container_width=True,
    )

    st.markdown("**Internal model timeline for the selected conversation**")
    st.dataframe(model_frame, use_container_width=True)

    st.markdown("**Full batch action history**")
    st.dataframe(actions_df, use_container_width=True)

    if enable_learning and baseline_results_df is not None:
        st.markdown("**Baseline results for comparison**")
        st.dataframe(baseline_results_df, use_container_width=True)
