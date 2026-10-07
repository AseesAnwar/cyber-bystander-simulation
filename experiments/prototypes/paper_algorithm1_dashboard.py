from __future__ import annotations

import argparse
import copy
from datetime import datetime
import json
import math
from pathlib import Path
import random
import subprocess
from collections import Counter, deque
from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd
import streamlit as st
from mesa import Agent, Model
from mesa.space import MultiGrid


PAPER_TITLE = "Theory of mind and continual reinforcement learning for bullying intervention"
PDF_PATH = "/Users/aseesanwar/Desktop/applied project /Theory of mind and continual reinforcement learning for bullying intervention.pdf"
APP_DIR = Path(__file__).resolve().parent
RUN_HISTORY_PATH = APP_DIR / "dashboard_run_history.json"
EXPORT_DIR = APP_DIR / "dashboard_exports"
EXPORT_DIR.mkdir(exist_ok=True)
EXCEL_EXPORT_INPUT_PATH = EXPORT_DIR / "dashboard_run_history_export.json"
EXCEL_EXPORT_BUILDER_PATH = APP_DIR / "dashboard_run_export_builder.mjs"
ARTIFACT_TOOL_MODULE_PATH = "/Users/aseesanwar/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/@oai/artifact-tool/dist/artifact_tool.mjs"
WORKSPACE_NODE_PATH = "/Users/aseesanwar/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node"

GRID_WIDTH = 10
GRID_HEIGHT = 10
MAX_DISTANCE = math.sqrt((GRID_WIDTH - 1) ** 2 + (GRID_HEIGHT - 1) ** 2)
T_MAX_PAPER = 20_000

ACTION_LABELS = {
    "a1": "Direct Confrontation",
    "a2": "Distraction",
    "a3": "Help-Seeking",
    "a4": "Mediation",
    "a5": "Support to Victim",
    "a6": "Move Closer to AB",
    "a7": "Move Closer to AV",
    "a8": "Remain Passive",
    "a9": "Move Away from AB",
    "a10": "Move Away from AV",
}
ACTION_ORDER = list(ACTION_LABELS.keys())
ACTION_TO_INDEX = {action: index for index, action in enumerate(ACTION_ORDER)}
INDEX_TO_ACTION = {index: action for action, index in ACTION_TO_INDEX.items()}

EMOTION_ENCODING = {
    "neutral": 0.0,
    "stressed": 0.5,
    "fear": 1.0,
    "aggressive": 1.0,
}

PAPER_HYPERPARAMETERS = {
    "Fully-connected layer dimensions": "512 x 256",
    "Adam learning rate": 0.000452,
    "Loss function": "MSE",
    "Initial epsilon": 1.0,
    "Final epsilon": 0.0001,
    "Number of exploration steps": 20_000,
    "Steps between target network updates": 1_000,
    "Replay memory size": 10_000,
    "Minibatch size": 32,
    "Epsilon": 0.1,
    "Mixing parameter eta": 0.001,
    "Discount factor gamma": 0.99,
    "Regularization coefficient lambda": 0.001,
    "Dropout rate p": 0.1,
}

PAPER_TABLE_5 = pd.DataFrame(
    [
        {"Risk Profile": "Low", "ISR (%)": "92 (+/-3)", "Precision (%)": "94 (+/-2)", "Recall (%)": "90 (+/-3)", "F1-Score (%)": "92 (+/-2.5)", "AER": "155 (+/-9)", "Avg. TPR (%)": "95 (+/-2)", "Avg. TNR (%)": "98 (+/-0.8)"},
        {"Risk Profile": "Middle", "ISR (%)": "96 (+/-2)", "Precision (%)": "97 (+/-1.5)", "Recall (%)": "96 (+/-1.5)", "F1-Score (%)": "96.5 (+/-1.5)", "AER": "165 (+/-8)", "Avg. TPR (%)": "98 (+/-1)", "Avg. TNR (%)": "99 (+/-0.5)"},
        {"Risk Profile": "High", "ISR (%)": "88 (+/-3)", "Precision (%)": "90 (+/-2.5)", "Recall (%)": "85 (+/-3)", "F1-Score (%)": "87 (+/-2.5)", "AER": "140 (+/-10)", "Avg. TPR (%)": "92 (+/-2)", "Avg. TNR (%)": "96 (+/-1.2)"},
    ]
)

PAPER_TABLE_11 = pd.DataFrame(
    [
        {"Configuration": "Complete", "Risk": "Low", "ISR (%)": "89 (+/-3)", "Precision (%)": "86.7 (+/-2.4)", "Recall (%)": "83.0 (+/-3.1)", "F1 (%)": "84.8 (+/-2.7)"},
        {"Configuration": "Complete", "Risk": "Mid", "ISR (%)": "92 (+/-3)", "Precision (%)": "88.5 (+/-2.2)", "Recall (%)": "87.9 (+/-2.5)", "F1 (%)": "88.2 (+/-2.3)"},
        {"Configuration": "Complete", "Risk": "High", "ISR (%)": "95 (+/-2)", "Precision (%)": "91.4 (+/-1.9)", "Recall (%)": "91.5 (+/-2.1)", "F1 (%)": "91.4 (+/-2.0)"},
        {"Configuration": "Non-ToM", "Risk": "Low", "ISR (%)": "73 (+/-4)", "Precision (%)": "74.5 (+/-3.5)", "Recall (%)": "69.2 (+/-3.9)", "F1 (%)": "71.2 (+/-3.6)"},
        {"Configuration": "Non-ToM", "Risk": "Mid", "ISR (%)": "77 (+/-4)", "Precision (%)": "77.8 (+/-3.2)", "Recall (%)": "73.8 (+/-3.5)", "F1 (%)": "75.6 (+/-3.4)"},
        {"Configuration": "Non-ToM", "Risk": "High", "ISR (%)": "81 (+/-3)", "Precision (%)": "80.3 (+/-3.1)", "Recall (%)": "79.5 (+/-3.2)", "F1 (%)": "79.8 (+/-3.1)"},
        {"Configuration": "Non-CL", "Risk": "Low", "ISR (%)": "64 (+/-5)", "Precision (%)": "66.9 (+/-4.0)", "Recall (%)": "65.3 (+/-4.3)", "F1 (%)": "66.1 (+/-4.1)"},
        {"Configuration": "Non-CL", "Risk": "Mid", "ISR (%)": "69 (+/-4)", "Precision (%)": "71.5 (+/-3.7)", "Recall (%)": "70.6 (+/-3.8)", "F1 (%)": "71.0 (+/-3.6)"},
        {"Configuration": "Non-CL", "Risk": "High", "ISR (%)": "74 (+/-4)", "Precision (%)": "75.1 (+/-3.5)", "Recall (%)": "72.0 (+/-3.7)", "F1 (%)": "73.5 (+/-3.4)"},
        {"Configuration": "Baseline", "Risk": "Low", "ISR (%)": "67 (+/-5)", "Precision (%)": "69.8 (+/-4.3)", "Recall (%)": "67.1 (+/-4.4)", "F1 (%)": "68.4 (+/-4.2)"},
        {"Configuration": "Baseline", "Risk": "Mid", "ISR (%)": "72 (+/-5)", "Precision (%)": "72.4 (+/-3.9)", "Recall (%)": "69.6 (+/-4.1)", "F1 (%)": "70.9 (+/-4.0)"},
        {"Configuration": "Baseline", "Risk": "High", "ISR (%)": "75 (+/-4)", "Precision (%)": "73.5 (+/-3.8)", "Recall (%)": "71.7 (+/-3.9)", "F1 (%)": "72.5 (+/-3.7)"},
    ]
)

PAPER_TABLE_12 = pd.DataFrame(
    [
        {"Configuration": "Complete", "Risk": "Low", "AER": "159 (+/-8)", "TPR (%)": "91.3 (+/-2.2)", "FPR (%)": "4.2 (+/-1.0)", "TNR (%)": "95.8 (+/-1.0)"},
        {"Configuration": "Complete", "Risk": "Mid", "AER": "165 (+/-9)", "TPR (%)": "93.1 (+/-1.8)", "FPR (%)": "3.5 (+/-0.8)", "TNR (%)": "96.5 (+/-0.8)"},
        {"Configuration": "Complete", "Risk": "High", "AER": "172 (+/-7)", "TPR (%)": "94.6 (+/-1.5)", "FPR (%)": "2.9 (+/-0.6)", "TNR (%)": "97.1 (+/-0.6)"},
        {"Configuration": "Non-ToM", "Risk": "Low", "AER": "121 (+/-11)", "TPR (%)": "80.2 (+/-2.9)", "FPR (%)": "7.4 (+/-1.3)", "TNR (%)": "92.6 (+/-1.3)"},
        {"Configuration": "Non-ToM", "Risk": "Mid", "AER": "129 (+/-10)", "TPR (%)": "82.3 (+/-2.7)", "FPR (%)": "6.6 (+/-1.1)", "TNR (%)": "93.4 (+/-1.1)"},
        {"Configuration": "Non-ToM", "Risk": "High", "AER": "137 (+/-9)", "TPR (%)": "84.1 (+/-2.4)", "FPR (%)": "5.8 (+/-1.0)", "TNR (%)": "94.2 (+/-1.0)"},
        {"Configuration": "Non-CL", "Risk": "Low", "AER": "93 (+/-13)", "TPR (%)": "75.6 (+/-3.4)", "FPR (%)": "9.1 (+/-1.6)", "TNR (%)": "90.9 (+/-1.6)"},
        {"Configuration": "Non-CL", "Risk": "Mid", "AER": "97 (+/-11)", "TPR (%)": "76.4 (+/-3.2)", "FPR (%)": "8.3 (+/-1.3)", "TNR (%)": "91.7 (+/-1.3)"},
        {"Configuration": "Non-CL", "Risk": "High", "AER": "102 (+/-10)", "TPR (%)": "78.2 (+/-3.0)", "FPR (%)": "7.4 (+/-1.1)", "TNR (%)": "92.6 (+/-1.1)"},
        {"Configuration": "Baseline", "Risk": "Low", "AER": "97 (+/-12)", "TPR (%)": "73.9 (+/-3.5)", "FPR (%)": "9.0 (+/-1.5)", "TNR (%)": "91.0 (+/-1.5)"},
        {"Configuration": "Baseline", "Risk": "Mid", "AER": "102 (+/-12)", "TPR (%)": "75.2 (+/-3.3)", "FPR (%)": "8.1 (+/-1.3)", "TNR (%)": "91.9 (+/-1.3)"},
        {"Configuration": "Baseline", "Risk": "High", "AER": "108 (+/-11)", "TPR (%)": "77.0 (+/-3.1)", "FPR (%)": "7.2 (+/-1.2)", "TNR (%)": "92.8 (+/-1.2)"},
    ]
)

PAPER_TABLE_9 = pd.DataFrame(
    [
        {"Role": "AO", "Norm ID": "N1", "Description": "Must intervene (e.g., via a2, a3) when aggression is detected", "Deontic type": "Obligation", "Risk level": "High"},
        {"Role": "AO", "Norm ID": "N2", "Description": "May not remain passive (a8) if victim distress is high", "Deontic type": "Prohibition", "Risk level": "High"},
        {"Role": "AO", "Norm ID": "N3", "Description": "Should avoid direct aggression (a1) unless in response to escalation", "Deontic type": "Permission", "Risk level": "Medium"},
        {"Role": "AB", "Norm ID": "N4", "Description": "May exhibit aggression (a1) only if norm tolerance is above threshold", "Deontic type": "Permission", "Risk level": "Medium, High"},
        {"Role": "AB", "Norm ID": "N5", "Description": "Must refrain from aggression if victim is in low-risk state", "Deontic type": "Prohibition", "Risk level": "Low"},
        {"Role": "AV", "Norm ID": "N6", "Description": "Should request help (a3) when emotional state drops below 0.4", "Deontic type": "Obligation", "Risk level": "Medium, High"},
        {"Role": "AV", "Norm ID": "N7", "Description": "May remain inactive if perceived threat is low", "Deontic type": "Permission", "Risk level": "Low"},
    ]
)

PAPER_TABLE_10 = pd.DataFrame(
    [
        {"Risk Level": "Low", "Behavioral Role Expression": "Bully suppressed; victim low reactivity; observer passive unless strong cues detected", "Permitted Actions and Constraints by Role": "Observer only indirect actions such as a2 and a5; a1 blocked; a3 rarely triggered; passive a8 tolerated."},
        {"Risk Level": "Middle", "Behavioral Role Expression": "Bully moderately aggressive; victim moderately sensitive; observer balanced", "Permitted Actions and Constraints by Role": "Observer can use most actions; a1 conditionally allowed; teacher help a3 moderately frequent; a8 discouraged but not penalized."},
        {"Risk Level": "High", "Behavioral Role Expression": "Bully highly aggressive; victim fragile; observer highly proactive", "Permitted Actions and Constraints by Role": "All observer actions permitted; help-seeking a3 encouraged; passive a8 explicitly penalized."},
    ]
)


PLAIN_ENGLISH_CONCEPTS = [
    ("Agent", "A character in the simulation."),
    ("Environment", "The situation all the characters are in."),
    ("State", "A snapshot of what is happening right now."),
    ("Action", "What the observer chooses to do next."),
    ("Reward", "A score showing whether the action helped or hurt."),
    ("Policy", "The observer's habit for choosing actions."),
    ("Q(s, a)", "A score for how good action a is expected to be in situation s."),
    ("Replay memory", "A notebook of past experiences used for learning."),
    ("Target network", "A slower copy of the learner that makes training more stable."),
    ("Exploration", "Trying actions to learn what works."),
    ("Exploitation", "Using the action currently believed to be best."),
    ("Continual learning", "Learning new situations without forgetting old ones."),
    ("Fisher information", "A way to mark which learned parts of the model are important."),
    ("EWC", "A penalty that stops the model from overwriting important old knowledge too much."),
    ("Theory of Mind", "Trying to infer what other people may be feeling, intending, or believing."),
    ("Norms", "Social rules about what is acceptable."),
    ("Roles", "Expected behavior based on who the agent is in the situation."),
    ("Terminal state", "The point where the episode ends because the problem is solved or time runs out."),
]

PLAIN_ENGLISH_ALGORITHM_STEPS = [
    "Start with a model that estimates how useful each action is.",
    "Keep a memory of past situations, actions, rewards, and next situations.",
    "Look at the current bullying situation.",
    "Choose what to do next.",
    "Sometimes use the best-known action.",
    "Sometimes explore instead.",
    "If exploring, use a safe socially acceptable action set.",
    "Perform the chosen action in the environment.",
    "Observe what changed after the action.",
    "Give the action a reward based on whether it helped or harmed the situation.",
    "Store that experience in replay memory.",
    "Sample older experiences from memory for learning.",
    "Compare predicted action quality with the reward and likely future reward.",
    "Add a continual-learning penalty so important old knowledge is not forgotten.",
    "Update the learner.",
    "Occasionally update the target network too.",
    "At task boundaries, update Fisher information so the model knows what knowledge matters most.",
]

PLAIN_ENGLISH_SECTION_GUIDE = [
    ("Core idea", "The paper builds an AI observer that watches a bullying situation, tries to understand it socially, and learns which intervention works best over time."),
    ("The four agents", "AB is the bully, AV is the victim, AO is the observer, and AT is the teacher or authority figure. Only AO learns."),
    ("What problem the paper is solving", "Bullying intervention is hard because the same action does not always work. The system needs to react to emotions, context, and risk level."),
    ("What reinforcement learning means here", "The observer learns by trying actions, seeing what happens, and getting reward or penalty signals."),
    ("What Theory of Mind means here", "The observer tries to infer hidden things like fear, aggression, or intention from visible clues."),
    ("What continual learning means here", "The system should improve on new situations without erasing what it already learned from older ones."),
    ("What the state contains", "The state includes positions, distances, emotions, and recent observer actions."),
    ("What the action space means", "The observer can confront, distract, seek help, mediate, support, move closer, move away, or stay passive."),
    ("What the reward is trying to teach", "Actions that reduce harm, protect the victim, and resolve the bullying get rewarded. Unhelpful or passive behavior can be penalized."),
    ("What terminal conditions mean", "An episode stops when the bullying is resolved or when the time limit is reached."),
    ("What norms and roles do", "They limit actions so the observer behaves in socially acceptable ways for the situation."),
    ("What risk profiles mean", "Low, Middle, and High risk settings represent easier and harder bullying situations."),
    ("Why the teacher exists", "Sometimes the best intervention is to call someone with authority instead of solving it alone."),
    ("What the evaluation metrics mean", "The paper measures how often intervention succeeds, how much reward the system gets, and how accurately it detects bullying."),
]


def apply_dashboard_css() -> None:
    st.markdown(
        """
        <style>
        div[data-testid="stMetric"] {
            padding-top: 0.35rem;
            padding-bottom: 0.35rem;
        }
        div[data-testid="stMetricLabel"] {
            white-space: normal !important;
            overflow-wrap: anywhere !important;
            line-height: 1.25 !important;
        }
        div[data-testid="stMetricValue"] {
            white-space: normal !important;
        }
        button[kind] p,
        div[role="tab"] p,
        label p {
            white-space: normal !important;
            overflow-wrap: anywhere !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def load_run_history_from_disk() -> list[dict[str, Any]]:
    if not RUN_HISTORY_PATH.exists():
        return []
    try:
        return json.loads(RUN_HISTORY_PATH.read_text())
    except json.JSONDecodeError:
        return []


def save_run_history_to_disk(run_history: list[dict[str, Any]]) -> None:
    RUN_HISTORY_PATH.write_text(json.dumps(run_history, indent=2))


def ensure_session_history() -> None:
    if "run_history" not in st.session_state:
        st.session_state["run_history"] = load_run_history_from_disk()


def build_run_record(
    risk_profile: str,
    training_episodes: int,
    evaluation_episodes: int,
    episode_max_steps: int,
    seed: int,
    results: dict[str, Any],
) -> dict[str, Any]:
    run_number = len(st.session_state.get("run_history", [])) + 1
    run_timestamp = datetime.now().isoformat(timespec="seconds")
    evaluation = results["evaluation"]
    return {
        "run_id": f"run_{run_number:03d}",
        "saved_at": run_timestamp,
        "parameters": {
            "risk_profile": risk_profile,
            "training_episodes": training_episodes,
            "evaluation_episodes": evaluation_episodes,
            "episode_max_steps": episode_max_steps,
            "starting_pattern_number": seed,
        },
        "summary": {
            "training_success_rate": round(results["training_success_rate"], 4),
            "evaluation_success_rate": round(evaluation["isr"], 4),
            "average_overall_score": round(evaluation["aer"], 4),
            "average_steps": round(evaluation["avg_steps"], 4),
            "final_exploration_rate": round(results["final_epsilon"], 6),
        },
        "paper_reference": results["paper_reference"],
        "action_counts": results["action_counts"],
        "evaluation_outcomes": evaluation["outcomes"],
        "training_rewards": results["training_rewards"],
        "training_losses": results["training_losses"],
        "sample_episode": results["sample_episode"],
    }


def build_run_history_summary_df(run_history: list[dict[str, Any]]) -> pd.DataFrame:
    rows = []
    for run in run_history:
        rows.append(
            {
                "Run ID": run["run_id"],
                "Saved At": run["saved_at"],
                "Risk Profile": run["parameters"]["risk_profile"],
                "Practice Runs": run["parameters"]["training_episodes"],
                "Test Runs": run["parameters"]["evaluation_episodes"],
                "Max Steps Per Run": run["parameters"]["episode_max_steps"],
                "Starting Pattern Number": run["parameters"]["starting_pattern_number"],
                "Solved Bullying (%)": run["summary"]["evaluation_success_rate"],
                "Average Overall Score": run["summary"]["average_overall_score"],
                "Average Steps": run["summary"]["average_steps"],
            }
        )
    return pd.DataFrame(rows)


def export_run_history_to_excel(run_history: list[dict[str, Any]]) -> Path:
    export_stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = EXPORT_DIR / f"algorithm1_run_history_{export_stamp}.xlsx"
    EXCEL_EXPORT_INPUT_PATH.write_text(json.dumps({"run_history": run_history}, indent=2))
    subprocess.run(
        [WORKSPACE_NODE_PATH, str(EXCEL_EXPORT_BUILDER_PATH), str(EXCEL_EXPORT_INPUT_PATH), str(output_path)],
        check=True,
        capture_output=True,
        text=True,
    )
    return output_path


def euclidean(pos_a: tuple[int, int], pos_b: tuple[int, int]) -> float:
    return math.dist(pos_a, pos_b)


def move_toward(current: tuple[int, int], target: tuple[int, int]) -> tuple[int, int]:
    x, y = current
    tx, ty = target
    next_x = x + (1 if tx > x else -1 if tx < x else 0)
    next_y = y + (1 if ty > y else -1 if ty < y else 0)
    return max(0, min(GRID_WIDTH - 1, next_x)), max(0, min(GRID_HEIGHT - 1, next_y))


def move_away(current: tuple[int, int], target: tuple[int, int]) -> tuple[int, int]:
    x, y = current
    tx, ty = target
    next_x = x + (-1 if tx > x else 1 if tx < x else random.choice([-1, 1]))
    next_y = y + (-1 if ty > y else 1 if ty < y else random.choice([-1, 1]))
    return max(0, min(GRID_WIDTH - 1, next_x)), max(0, min(GRID_HEIGHT - 1, next_y))


def one_hot(index: int, size: int) -> np.ndarray:
    vector = np.zeros(size, dtype=np.float64)
    vector[index] = 1.0
    return vector


def risk_to_one_hot(risk_profile: str) -> np.ndarray:
    mapping = {"Low": 0, "Middle": 1, "High": 2}
    return one_hot(mapping[risk_profile], 3)


def base_reward_for_action(action: str) -> float:
    rewards = {
        "a1": 10.0,
        "a2": 3.0,
        "a3": 5.0,
        "a4": 7.0,
        "a5": 4.0,
        "a8": -2.0,
        "a9": -3.0,
        "a10": -5.0,
    }
    return rewards.get(action, 0.0)


def allowed_actions_for_profile(risk_profile: str, aggression_active: bool, victim_emotion: str, ao_ab_distance: float) -> list[str]:
    if risk_profile == "Low":
        actions = ["a2", "a5", "a6", "a7", "a8", "a9", "a10"]
        if aggression_active and victim_emotion == "fear":
            actions.append("a3")
        return actions
    if risk_profile == "Middle":
        actions = ["a2", "a3", "a4", "a5", "a6", "a7", "a8", "a9", "a10"]
        if aggression_active and ao_ab_distance <= 1.5:
            actions.append("a1")
        return actions
    return ACTION_ORDER.copy()


def safe_subset_actions(allowed_actions: list[str]) -> list[str]:
    safe_actions = {"a2", "a3", "a4", "a5", "a6", "a7", "a8", "a9", "a10"}
    filtered = [action for action in allowed_actions if action in safe_actions]
    return filtered or allowed_actions


class BullyAgent(Agent):
    def __init__(self, model: "BullyingInterventionModel") -> None:
        super().__init__(model)


class VictimAgent(Agent):
    def __init__(self, model: "BullyingInterventionModel") -> None:
        super().__init__(model)


class ObserverAgent(Agent):
    def __init__(self, model: "BullyingInterventionModel") -> None:
        super().__init__(model)


class TeacherAgent(Agent):
    def __init__(self, model: "BullyingInterventionModel") -> None:
        super().__init__(model)


@dataclass
class Transition:
    state: np.ndarray
    action_index: int
    reward: float
    next_state: np.ndarray
    done: bool


class NumpyDQN:
    def __init__(
        self,
        state_dim: int,
        action_dim: int,
        learning_rate: float,
        gamma: float,
        dropout_rate: float,
        replay_memory_size: int,
        minibatch_size: int,
        target_update_steps: int,
        fisher_lambda: float,
        seed: int,
    ) -> None:
        self.state_dim = state_dim
        self.action_dim = action_dim
        self.learning_rate = learning_rate
        self.gamma = gamma
        self.dropout_rate = dropout_rate
        self.replay_memory = deque(maxlen=replay_memory_size)
        self.minibatch_size = minibatch_size
        self.target_update_steps = target_update_steps
        self.fisher_lambda = fisher_lambda
        self.random = np.random.default_rng(seed)
        self.train_steps = 0

        scale = 0.05
        self.params = {
            "W1": self.random.normal(0, scale, size=(state_dim, 512)),
            "b1": np.zeros(512, dtype=np.float64),
            "W2": self.random.normal(0, scale, size=(512, 256)),
            "b2": np.zeros(256, dtype=np.float64),
            "W3": self.random.normal(0, scale, size=(256, action_dim)),
            "b3": np.zeros(action_dim, dtype=np.float64),
        }
        self.target_params = copy.deepcopy(self.params)
        self.theta_star = copy.deepcopy(self.params)
        self.fisher = {name: np.zeros_like(value) for name, value in self.params.items()}

    def relu(self, x: np.ndarray) -> np.ndarray:
        return np.maximum(0.0, x)

    def forward(self, states: np.ndarray, training: bool = False, params: dict[str, np.ndarray] | None = None) -> tuple[np.ndarray, dict[str, np.ndarray]]:
        current = self.params if params is None else params
        z1 = states @ current["W1"] + current["b1"]
        a1 = self.relu(z1)
        mask1 = np.ones_like(a1)
        if training and self.dropout_rate > 0:
            mask1 = (self.random.random(a1.shape) > self.dropout_rate).astype(np.float64) / (1.0 - self.dropout_rate)
            a1 = a1 * mask1

        z2 = a1 @ current["W2"] + current["b2"]
        a2 = self.relu(z2)
        mask2 = np.ones_like(a2)
        if training and self.dropout_rate > 0:
            mask2 = (self.random.random(a2.shape) > self.dropout_rate).astype(np.float64) / (1.0 - self.dropout_rate)
            a2 = a2 * mask2

        q_values = a2 @ current["W3"] + current["b3"]
        cache = {"states": states, "z1": z1, "a1": a1, "mask1": mask1, "z2": z2, "a2": a2, "mask2": mask2}
        return q_values, cache

    def predict(self, state: np.ndarray) -> np.ndarray:
        q_values, _ = self.forward(state.reshape(1, -1), training=False)
        return q_values[0]

    def store(self, transition: Transition) -> None:
        self.replay_memory.append(transition)

    def sample_batch(self) -> list[Transition]:
        indices = self.random.choice(len(self.replay_memory), size=self.minibatch_size, replace=False)
        return [self.replay_memory[int(index)] for index in indices]

    def _ewc_gradient(self) -> dict[str, np.ndarray]:
        gradients = {}
        for name, values in self.params.items():
            gradients[name] = self.fisher_lambda * self.fisher[name] * (values - self.theta_star[name])
        return gradients

    def _backward(self, cache: dict[str, np.ndarray], actions: np.ndarray, targets: np.ndarray, q_values: np.ndarray) -> dict[str, np.ndarray]:
        batch_size = actions.shape[0]
        gradients = {name: np.zeros_like(value) for name, value in self.params.items()}
        dq = np.zeros_like(q_values)
        selected = q_values[np.arange(batch_size), actions]
        dq[np.arange(batch_size), actions] = (2.0 / batch_size) * (selected - targets)

        gradients["W3"] = cache["a2"].T @ dq
        gradients["b3"] = dq.sum(axis=0)

        da2 = dq @ self.params["W3"].T
        da2 = da2 * cache["mask2"]
        dz2 = da2 * (cache["z2"] > 0)
        gradients["W2"] = cache["a1"].T @ dz2
        gradients["b2"] = dz2.sum(axis=0)

        da1 = dz2 @ self.params["W2"].T
        da1 = da1 * cache["mask1"]
        dz1 = da1 * (cache["z1"] > 0)
        gradients["W1"] = cache["states"].T @ dz1
        gradients["b1"] = dz1.sum(axis=0)
        return gradients

    def train_from_replay(self) -> float | None:
        if len(self.replay_memory) < self.minibatch_size:
            return None

        batch = self.sample_batch()
        states = np.stack([item.state for item in batch], axis=0)
        actions = np.array([item.action_index for item in batch], dtype=np.int64)
        rewards = np.array([item.reward for item in batch], dtype=np.float64)
        next_states = np.stack([item.next_state for item in batch], axis=0)
        dones = np.array([item.done for item in batch], dtype=np.float64)

        q_values, cache = self.forward(states, training=True)
        next_q_target, _ = self.forward(next_states, training=False, params=self.target_params)
        targets = rewards + (1.0 - dones) * self.gamma * next_q_target.max(axis=1)

        data_loss = np.mean((q_values[np.arange(len(batch)), actions] - targets) ** 2)
        gradients = self._backward(cache, actions, targets, q_values)
        ewc_gradients = self._ewc_gradient()
        ewc_loss = 0.0

        for name in gradients:
            gradients[name] += ewc_gradients[name]
            ewc_loss += 0.5 * self.fisher_lambda * np.sum(self.fisher[name] * (self.params[name] - self.theta_star[name]) ** 2)

        for name in self.params:
            self.params[name] -= self.learning_rate * gradients[name]

        self.train_steps += 1
        if self.train_steps % self.target_update_steps == 0:
            self.target_params = copy.deepcopy(self.params)

        return float(data_loss + ewc_loss)

    def update_fisher(self, sample_size: int = 32) -> None:
        if len(self.replay_memory) < sample_size:
            return
        batch = random.sample(list(self.replay_memory), sample_size)
        states = np.stack([item.state for item in batch], axis=0)
        actions = np.array([item.action_index for item in batch], dtype=np.int64)
        rewards = np.array([item.reward for item in batch], dtype=np.float64)
        next_states = np.stack([item.next_state for item in batch], axis=0)
        dones = np.array([item.done for item in batch], dtype=np.float64)

        q_values, cache = self.forward(states, training=False)
        next_q_target, _ = self.forward(next_states, training=False, params=self.target_params)
        targets = rewards + (1.0 - dones) * self.gamma * next_q_target.max(axis=1)
        gradients = self._backward(cache, actions, targets, q_values)

        for name in self.fisher:
            self.fisher[name] = 0.9 * self.fisher[name] + 0.1 * (gradients[name] ** 2)
            self.theta_star[name] = self.params[name].copy()


class BullyingInterventionModel(Model):
    def __init__(self, risk_profile: str, max_steps: int, seed: int) -> None:
        super().__init__(seed=seed)
        self.risk_profile = risk_profile
        self.max_steps = max_steps
        self.grid = MultiGrid(GRID_WIDTH, GRID_HEIGHT, torus=False)
        self.rng = random.Random(seed)
        self.current_step = 0
        self.teacher_alerted = False
        self.bullying_resolved = False
        self.resolved_by_action: str | None = None
        self.last_action = "a8"
        self.history_actions = deque(["a8", "a8"], maxlen=2)
        self.last_reward = 0.0
        self.action_log: list[dict[str, Any]] = []

        self.ab = BullyAgent(self)
        self.av = VictimAgent(self)
        self.ao = ObserverAgent(self)
        self.at = TeacherAgent(self)

        self._place_initial_agents()
        self.victim_emotion = "neutral"
        self.bully_emotion = "aggressive"
        self.aggression_active = self._initial_aggression_flag()
        if self.aggression_active:
            self.victim_emotion = "fear"

    def _place_initial_agents(self) -> None:
        positions = {
            self.ab: (7, 5),
            self.av: (5, 5),
            self.ao: (3, 5),
            self.at: (1, 1),
        }
        for agent, position in positions.items():
            self.grid.place_agent(agent, position)

    def _initial_aggression_flag(self) -> bool:
        return self.risk_profile in {"Middle", "High"}

    def _aggression_probability(self) -> float:
        mapping = {"Low": 0.15, "Middle": 0.45, "High": 0.75}
        return mapping[self.risk_profile]

    def _is_terminal(self) -> bool:
        return self.bullying_resolved or self.current_step >= self.max_steps

    def _teacher_intervene(self) -> None:
        self.teacher_alerted = True
        self.aggression_active = False
        self.bully_emotion = "neutral"
        self.victim_emotion = "neutral"
        self.bullying_resolved = True
        self.resolved_by_action = "a3"
        self.grid.move_agent(self.at, move_toward(self.at.pos, self.ab.pos))

    def _bully_rule_step(self) -> None:
        if self.teacher_alerted or self.bullying_resolved:
            self.aggression_active = False
            return

        self.grid.move_agent(self.ab, move_toward(self.ab.pos, self.av.pos))
        bully_near_victim = euclidean(self.ab.pos, self.av.pos) <= 1.5

        if self.risk_profile == "Low":
            self.aggression_active = False
        else:
            roll = self.rng.random()
            self.aggression_active = bully_near_victim and roll < self._aggression_probability()

        if self.aggression_active:
            self.bully_emotion = "aggressive"
            self.victim_emotion = "fear"
        elif self.victim_emotion != "neutral":
            self.victim_emotion = "stressed"

    def _victim_rule_step(self) -> None:
        if self.victim_emotion == "fear":
            if self.risk_profile == "High":
                return
            self.grid.move_agent(self.av, move_away(self.av.pos, self.ab.pos))
        elif self.victim_emotion == "stressed":
            if euclidean(self.ao.pos, self.av.pos) <= 1.5:
                self.victim_emotion = "neutral"

    def get_state_vector(self) -> np.ndarray:
        positions = np.array(
            [
                self.ab.pos[0] / (GRID_WIDTH - 1),
                self.ab.pos[1] / (GRID_HEIGHT - 1),
                self.av.pos[0] / (GRID_WIDTH - 1),
                self.av.pos[1] / (GRID_HEIGHT - 1),
                self.ao.pos[0] / (GRID_WIDTH - 1),
                self.ao.pos[1] / (GRID_HEIGHT - 1),
                self.at.pos[0] / (GRID_WIDTH - 1),
                self.at.pos[1] / (GRID_HEIGHT - 1),
            ],
            dtype=np.float64,
        )
        distances = np.array(
            [
                euclidean(self.ab.pos, self.av.pos) / MAX_DISTANCE,
                euclidean(self.ao.pos, self.ab.pos) / MAX_DISTANCE,
                euclidean(self.ao.pos, self.av.pos) / MAX_DISTANCE,
                euclidean(self.at.pos, self.ab.pos) / MAX_DISTANCE,
            ],
            dtype=np.float64,
        )
        emotions = np.array(
            [
                EMOTION_ENCODING[self.victim_emotion],
                EMOTION_ENCODING[self.bully_emotion],
            ],
            dtype=np.float64,
        )
        history = np.concatenate(
            [one_hot(ACTION_TO_INDEX[action], len(ACTION_ORDER)) for action in self.history_actions],
            axis=0,
        )
        flags = np.array(
            [
                float(self.aggression_active),
                float(self.teacher_alerted),
            ],
            dtype=np.float64,
        )
        risk = risk_to_one_hot(self.risk_profile)
        return np.concatenate([positions, distances, emotions, history, flags, risk], axis=0)

    def allowed_actions(self) -> list[str]:
        return allowed_actions_for_profile(
            self.risk_profile,
            self.aggression_active,
            self.victim_emotion,
            euclidean(self.ao.pos, self.ab.pos),
        )

    def _apply_observer_action(self, action: str) -> None:
        if action == "a1":
            self.grid.move_agent(self.ao, move_toward(self.ao.pos, self.ab.pos))
            if euclidean(self.ao.pos, self.ab.pos) <= 1.5 and self.aggression_active:
                self.aggression_active = False
                self.bully_emotion = "neutral"
                self.victim_emotion = "neutral"
                self.bullying_resolved = True
                self.resolved_by_action = "a1"
        elif action == "a2":
            midpoint = move_toward(self.ao.pos, self.av.pos)
            self.grid.move_agent(self.ao, midpoint)
            if self.aggression_active and euclidean(self.ao.pos, self.ab.pos) <= 2.5:
                self.aggression_active = False
                self.bully_emotion = "neutral"
        elif action == "a3":
            self._teacher_intervene()
        elif action == "a4":
            self.grid.move_agent(self.ao, move_toward(self.ao.pos, self.av.pos))
            if self.aggression_active and euclidean(self.ao.pos, self.ab.pos) <= 2.5:
                self.aggression_active = False
                self.bully_emotion = "neutral"
                self.victim_emotion = "neutral"
                self.bullying_resolved = True
                self.resolved_by_action = "a4"
        elif action == "a5":
            self.grid.move_agent(self.ao, move_toward(self.ao.pos, self.av.pos))
            if euclidean(self.ao.pos, self.av.pos) <= 1.5 and self.victim_emotion in {"fear", "stressed"}:
                self.victim_emotion = "neutral"
        elif action == "a6":
            self.grid.move_agent(self.ao, move_toward(self.ao.pos, self.ab.pos))
        elif action == "a7":
            self.grid.move_agent(self.ao, move_toward(self.ao.pos, self.av.pos))
        elif action == "a8":
            pass
        elif action == "a9":
            self.grid.move_agent(self.ao, move_away(self.ao.pos, self.ab.pos))
        elif action == "a10":
            self.grid.move_agent(self.ao, move_away(self.ao.pos, self.av.pos))

    def _reward(self, action: str, old_ao_av: float, old_ao_ab: float, previous_victim_emotion: str, previous_aggression: bool) -> float:
        reward = base_reward_for_action(action)

        new_ao_av = euclidean(self.ao.pos, self.av.pos)
        new_ao_ab = euclidean(self.ao.pos, self.ab.pos)
        delta_ao_av = old_ao_av - new_ao_av
        delta_ao_ab = old_ao_ab - new_ao_ab
        reward += 2.0 * delta_ao_av + 1.0 * delta_ao_ab

        if previous_aggression and not self.aggression_active:
            reward += 5.0
        if previous_victim_emotion == "fear" and self.victim_emotion == "neutral":
            reward += 3.0

        if self.bullying_resolved and action in {"a1", "a3", "a4"}:
            reward += 15.0
        elif self.current_step >= self.max_steps and not self.bullying_resolved:
            reward -= 10.0

        if self.risk_profile == "High" and action == "a8":
            reward -= 3.0

        return reward

    def step_with_action(self, action: str) -> tuple[np.ndarray, float, bool, dict[str, Any]]:
        self._bully_rule_step()
        state = self.get_state_vector()
        old_ao_av = euclidean(self.ao.pos, self.av.pos)
        old_ao_ab = euclidean(self.ao.pos, self.ab.pos)
        previous_victim_emotion = self.victim_emotion
        previous_aggression = self.aggression_active

        self._apply_observer_action(action)
        if not self.teacher_alerted:
            self._victim_rule_step()

        self.current_step += 1
        reward = self._reward(action, old_ao_av, old_ao_ab, previous_victim_emotion, previous_aggression)
        self.last_reward = reward
        self.last_action = action
        self.history_actions.append(action)

        done = self._is_terminal()
        next_state = self.get_state_vector()
        step_record = {
            "step": self.current_step,
            "action": action,
            "action_label": ACTION_LABELS[action],
            "reward": reward,
            "aggression_active": self.aggression_active,
            "victim_emotion": self.victim_emotion,
            "bully_emotion": self.bully_emotion,
            "teacher_alerted": self.teacher_alerted,
            "resolved": self.bullying_resolved,
            "observer_pos": self.ao.pos,
            "bully_pos": self.ab.pos,
            "victim_pos": self.av.pos,
            "teacher_pos": self.at.pos,
        }
        self.action_log.append(step_record)
        return next_state, reward, done, step_record


def build_agent(seed: int, state_dim: int) -> NumpyDQN:
    return NumpyDQN(
        state_dim=state_dim,
        action_dim=len(ACTION_ORDER),
        learning_rate=float(PAPER_HYPERPARAMETERS["Adam learning rate"]),
        gamma=float(PAPER_HYPERPARAMETERS["Discount factor gamma"]),
        dropout_rate=float(PAPER_HYPERPARAMETERS["Dropout rate p"]),
        replay_memory_size=int(PAPER_HYPERPARAMETERS["Replay memory size"]),
        minibatch_size=int(PAPER_HYPERPARAMETERS["Minibatch size"]),
        target_update_steps=int(PAPER_HYPERPARAMETERS["Steps between target network updates"]),
        fisher_lambda=float(PAPER_HYPERPARAMETERS["Regularization coefficient lambda"]),
        seed=seed,
    )


def epsilon_for_episode(episode: int, total_exploration_steps: int) -> float:
    initial_epsilon = float(PAPER_HYPERPARAMETERS["Initial epsilon"])
    final_epsilon = float(PAPER_HYPERPARAMETERS["Final epsilon"])
    progress = min(1.0, episode / max(1, total_exploration_steps))
    return initial_epsilon + (final_epsilon - initial_epsilon) * progress


def choose_action(agent: NumpyDQN, model: BullyingInterventionModel, state: np.ndarray, epsilon: float) -> str:
    allowed = model.allowed_actions()
    if random.random() < epsilon:
        safe = safe_subset_actions(allowed)
        return random.choice(safe)

    q_values = agent.predict(state)
    allowed_indices = [ACTION_TO_INDEX[action] for action in allowed]
    best_index = max(allowed_indices, key=lambda idx: q_values[idx])
    return INDEX_TO_ACTION[best_index]


def run_training(risk_profile: str, training_episodes: int, evaluation_episodes: int, episode_max_steps: int, seed: int) -> dict[str, Any]:
    state_dim = 39
    agent = build_agent(seed=seed, state_dim=state_dim)
    losses: list[float] = []
    episode_rewards: list[float] = []
    success_flags: list[int] = []
    action_counter: Counter[str] = Counter()

    for episode in range(training_episodes):
        model = BullyingInterventionModel(risk_profile=risk_profile, max_steps=episode_max_steps, seed=seed + episode)
        state = model.get_state_vector()
        epsilon = epsilon_for_episode(episode, int(PAPER_HYPERPARAMETERS["Number of exploration steps"]))
        total_reward = 0.0

        while not model._is_terminal():
            action = choose_action(agent, model, state, epsilon)
            next_state, reward, done, _ = model.step_with_action(action)
            transition = Transition(
                state=state,
                action_index=ACTION_TO_INDEX[action],
                reward=reward,
                next_state=next_state,
                done=done,
            )
            agent.store(transition)
            loss = agent.train_from_replay()
            if loss is not None:
                losses.append(loss)
            action_counter[action] += 1
            total_reward += reward
            state = next_state
            if done:
                break

        agent.update_fisher()
        episode_rewards.append(total_reward)
        success_flags.append(int(model.bullying_resolved))

    evaluation = run_evaluation(agent, risk_profile, evaluation_episodes, episode_max_steps, seed + 50_000)
    paper_reference = PAPER_TABLE_5[PAPER_TABLE_5["Risk Profile"] == risk_profile].iloc[0].to_dict()
    return {
        "training_rewards": episode_rewards,
        "training_losses": losses,
        "training_success_rate": 100.0 * (sum(success_flags) / max(1, len(success_flags))),
        "action_counts": dict(action_counter),
        "evaluation": evaluation,
        "paper_reference": paper_reference,
        "final_epsilon": epsilon_for_episode(training_episodes, int(PAPER_HYPERPARAMETERS["Number of exploration steps"])),
        "sample_episode": evaluation["sample_episode"],
    }


def run_evaluation(agent: NumpyDQN, risk_profile: str, evaluation_episodes: int, episode_max_steps: int, seed: int) -> dict[str, Any]:
    rewards = []
    successes = 0
    step_counts = []
    outcomes = Counter()
    sample_episode_log: list[dict[str, Any]] = []

    for episode in range(evaluation_episodes):
        model = BullyingInterventionModel(risk_profile=risk_profile, max_steps=episode_max_steps, seed=seed + episode)
        state = model.get_state_vector()
        total_reward = 0.0

        while not model._is_terminal():
            allowed = model.allowed_actions()
            q_values = agent.predict(state)
            action_index = max([ACTION_TO_INDEX[action] for action in allowed], key=lambda idx: q_values[idx])
            action = INDEX_TO_ACTION[action_index]
            next_state, reward, done, _ = model.step_with_action(action)
            total_reward += reward
            state = next_state
            if done:
                break

        rewards.append(total_reward)
        step_counts.append(model.current_step)
        if model.bullying_resolved:
            successes += 1
            outcomes[f"Resolved via {model.resolved_by_action}"] += 1
        else:
            outcomes["Time-limit terminal"] += 1
        if episode == 0:
            sample_episode_log = model.action_log

    return {
        "isr": 100.0 * successes / max(1, evaluation_episodes),
        "aer": float(np.mean(rewards)) if rewards else 0.0,
        "avg_steps": float(np.mean(step_counts)) if step_counts else 0.0,
        "outcomes": dict(outcomes),
        "sample_episode": sample_episode_log,
    }


def build_action_table(action_counts: dict[str, int]) -> pd.DataFrame:
    rows = []
    total = sum(action_counts.values()) or 1
    for action in ACTION_ORDER:
        count = action_counts.get(action, 0)
        rows.append(
            {
                "Action": action,
                "Label": ACTION_LABELS[action],
                "Count": count,
                "Share (%)": round(100.0 * count / total, 2),
            }
        )
    return pd.DataFrame(rows)


def build_grid_snapshot(step_row: pd.Series) -> pd.DataFrame:
    grid = [["" for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
    placements = [
        ("AB", step_row["bully_pos"]),
        ("AV", step_row["victim_pos"]),
        ("AO", step_row["observer_pos"]),
        ("AT", step_row["teacher_pos"]),
    ]
    for label, position in placements:
        x, y = position
        current = grid[y][x]
        grid[y][x] = label if not current else f"{current}/{label}"
    display = pd.DataFrame(grid, index=[f"y={y}" for y in range(GRID_HEIGHT)], columns=[f"x={x}" for x in range(GRID_WIDTH)])
    return display.iloc[::-1]


def render_paper_tables() -> None:
    st.subheader("Paper-Sourced Definitions")
    st.caption("All tables below were transcribed from the paper and its appendices.")

    st.markdown("**Algorithm 1 inputs and hyperparameters**")
    hyperparameter_df = pd.DataFrame(PAPER_HYPERPARAMETERS.items(), columns=["Parameter", "Value"])
    hyperparameter_df["Value"] = hyperparameter_df["Value"].astype(str)
    st.dataframe(hyperparameter_df, use_container_width=True)

    st.markdown("**Action space from Appendix B.3**")
    st.dataframe(
        pd.DataFrame(
            [{"Action": action, "Description": label} for action, label in ACTION_LABELS.items()]
        ),
        use_container_width=True,
    )

    st.markdown("**Risk-profile norms and permissions**")
    st.dataframe(PAPER_TABLE_9, use_container_width=True)
    st.dataframe(PAPER_TABLE_10, use_container_width=True)

    st.markdown("**Reported performance tables from the paper**")
    st.dataframe(PAPER_TABLE_5, use_container_width=True)
    st.dataframe(PAPER_TABLE_11, use_container_width=True)
    st.dataframe(PAPER_TABLE_12, use_container_width=True)


def render_plain_english_explainer() -> None:
    st.subheader("Plain English Guide")
    st.caption("This section rewrites the paper's main ideas in simple language for non-technical readers.")

    st.markdown("**One-sentence summary**")
    st.write(
        "The paper builds a learning observer that watches bullying, guesses what people may be feeling or intending, "
        "chooses an intervention, and improves over time without forgetting older lessons."
    )

    st.markdown("**Section-by-section explanation**")
    for title, explanation in PLAIN_ENGLISH_SECTION_GUIDE:
        with st.expander(title, expanded=False):
            st.write(explanation)

    st.markdown("**Main concepts in simple language**")
    concept_df = pd.DataFrame(PLAIN_ENGLISH_CONCEPTS, columns=["Concept", "Plain English Meaning"])
    st.dataframe(concept_df, use_container_width=True)

    st.markdown("**Algorithm 1 step-by-step in plain English**")
    for index, step in enumerate(PLAIN_ENGLISH_ALGORITHM_STEPS, start=1):
        st.write(f"{index}. {step}")

    st.markdown("**What each observer action means**")
    action_explainer = pd.DataFrame(
        [
            ("a1", "Direct confrontation", "The observer directly tells the bully to stop."),
            ("a2", "Distraction", "The observer tries to break the tension indirectly."),
            ("a3", "Help-seeking", "The observer gets the teacher or authority involved."),
            ("a4", "Mediation", "The observer tries to calm both sides and reduce tension."),
            ("a5", "Support to victim", "The observer stands by the victim or comforts them."),
            ("a6", "Move closer to bully", "The observer approaches the bully to watch closely or add social pressure."),
            ("a7", "Move closer to victim", "The observer gets nearer to the victim for support or protection."),
            ("a8", "Remain passive", "The observer does nothing at that moment."),
            ("a9", "Move away from bully", "The observer creates more distance from the bully."),
            ("a10", "Move away from victim", "The observer creates more distance from the victim."),
        ],
        columns=["Action", "Label", "Plain English Meaning"],
    )
    st.dataframe(action_explainer, use_container_width=True)

    st.markdown("**Metrics in simple language**")
    metrics_df = pd.DataFrame(
        [
            ("ISR", "How often the intervention actually succeeds."),
            ("AER", "The average total reward the observer earns per episode."),
            ("Precision", "When the system says there is bullying, how often it is right."),
            ("Recall", "How often the system catches real bullying situations."),
            ("F1-Score", "A balance between precision and recall."),
            ("TPR", "How often true bullying is correctly identified."),
            ("TNR", "How often non-bullying situations are correctly left alone."),
        ],
        columns=["Metric", "Plain English Meaning"],
    )
    st.dataframe(metrics_df, use_container_width=True)


def render_results(results: dict[str, Any], risk_profile: str) -> None:
    evaluation = results["evaluation"]
    paper_reference = results["paper_reference"]
    training_rewards = results["training_rewards"]
    action_counts = results["action_counts"]
    total_actions = sum(action_counts.values())

    metric_1, metric_2 = st.columns(2)
    metric_3, metric_4 = st.columns(2)
    metric_1.metric("Solved bullying rate", f"{evaluation['isr']:.1f}%")
    metric_2.metric("Average score per test run", f"{evaluation['aer']:.1f}")
    metric_3.metric("Average steps per test run", f"{evaluation['avg_steps']:.1f}")
    metric_4.metric("Paper success rate", paper_reference["ISR (%)"])

    st.markdown(f"**Risk profile:** `{risk_profile}`")
    st.markdown(
        f"**Paper reference for {risk_profile}:** success rate `{paper_reference['ISR (%)']}`, "
        f"average reward `{paper_reference['AER']}`, detection precision `{paper_reference['Precision (%)']}`, "
        f"Recall `{paper_reference['Recall (%)']}`."
    )
    st.info(
        f"In this run, the observer was trained in a `{risk_profile}` risk scenario, then tested on new episodes. "
        f"The most important number is the success rate: it shows how often the observer managed to calm or resolve the bullying situation."
    )

    reward_series = pd.DataFrame(
        {
            "Episode": list(range(1, len(results["training_rewards"]) + 1)),
            "Overall score": results["training_rewards"],
        }
    )
    st.markdown("**How the observer's score changed while learning**")
    st.line_chart(reward_series.set_index("Episode"))
    if training_rewards:
        first_reward = training_rewards[0]
        last_reward = training_rewards[-1]
        direction = "higher" if last_reward > first_reward else "lower" if last_reward < first_reward else "about the same"
        st.caption(
            f"Plain English: this line shows whether the observer's decisions became more helpful over time. "
            f"The score started at `{first_reward:.1f}` and ended at `{last_reward:.1f}`, so the latest learning result is `{direction}` than the first one."
        )

    if results["training_losses"]:
        loss_series = pd.DataFrame(
            {
                "Learning update": list(range(1, len(results["training_losses"]) + 1)),
                "Prediction error": results["training_losses"],
            }
        )
        st.markdown("**How much prediction error remained during learning**")
        st.line_chart(loss_series.set_index("Learning update"))
        latest_loss = results["training_losses"][-1]
        st.caption(
            f"Plain English: this chart shows how far the model's guesses were from the rewards it actually received. "
            f"Lower values usually mean the observer is becoming more consistent. The latest prediction error was `{latest_loss:.3f}`."
        )

    st.markdown("**Which actions the observer used most often while learning**")
    action_table = build_action_table(results["action_counts"])
    st.dataframe(action_table, use_container_width=True)
    if total_actions:
        top_action = action_table.sort_values("Count", ascending=False).iloc[0]
        st.caption(
            f"Plain English: this table shows the observer's habits during training. "
            f"The most common action was `{top_action['Label']}` and it was chosen `{int(top_action['Count'])}` times "
            f"which is `{top_action['Share (%)']:.1f}%` of all training actions."
        )

    st.markdown("**What happened in the final test runs**")
    outcomes_df = pd.DataFrame(
        [{"Outcome": outcome, "Count": count} for outcome, count in evaluation["outcomes"].items()]
    )
    st.dataframe(
        outcomes_df,
        use_container_width=True,
    )
    if not outcomes_df.empty:
        top_outcome = outcomes_df.sort_values("Count", ascending=False).iloc[0]
        st.caption(
            f"Plain English: this table summarizes the endings of the test episodes after learning. "
            f"The most common result was `{top_outcome['Outcome']}` with `{int(top_outcome['Count'])}` cases."
        )

    sample_episode = pd.DataFrame(results["sample_episode"])
    if not sample_episode.empty:
        st.markdown("**One example test run after learning**")
        st.dataframe(
            sample_episode[
                [
                    "step",
                    "action",
                    "action_label",
                    "reward",
                    "aggression_active",
                    "victim_emotion",
                    "resolved",
                    "observer_pos",
                    "bully_pos",
                    "victim_pos",
                    "teacher_pos",
                ]
            ],
            use_container_width=True,
        )
        if len(sample_episode) > 0:
            final_row = sample_episode.iloc[-1]
            end_text = "resolved the bullying" if bool(final_row["resolved"]) else "did not fully resolve the bullying before the run ended"
            st.caption(
                f"Plain English: this table is one full example run after training. "
                f"In this example, the observer took `{len(sample_episode)}` step(s) and `{end_text}`."
            )
        max_step = int(sample_episode["step"].max())
        if max_step > 1:
            selected_step = st.slider(
                "Choose a step from the example run to inspect",
                min_value=1,
                max_value=max_step,
                value=1,
                step=1,
                key="sample_episode_step_slider",
            )
        else:
            selected_step = 1
            st.caption("This sample episode ended in a single step, so there is only one state to inspect.")
        step_row = sample_episode[sample_episode["step"] == selected_step].iloc[0]
        detail_1, detail_2, detail_3, detail_4 = st.columns(4)
        detail_1.metric("Action", f"{step_row['action']} ({step_row['action_label']})")
        detail_2.metric("Score at this step", f"{step_row['reward']:.2f}")
        detail_3.metric("Victim's emotional state", str(step_row["victim_emotion"]))
        detail_4.metric("Was bullying still active?", "Yes" if bool(step_row["aggression_active"]) else "No")

        st.markdown("**Where each person was standing at the chosen step**")
        st.dataframe(build_grid_snapshot(step_row), use_container_width=True)
        st.caption(
            "Plain English: this grid is a snapshot of the scene. It helps you see who was near whom when the observer made that decision."
        )


def render_run_history_section() -> None:
    run_history = st.session_state.get("run_history", [])
    st.markdown("**Saved run history**")
    if not run_history:
        st.write("No runs have been saved yet. Each time you run the simulation, the dashboard will add that run to the saved history automatically.")
        return

    history_df = build_run_history_summary_df(run_history)
    st.dataframe(history_df, use_container_width=True)
    st.caption(
        f"Plain English: the dashboard is currently storing `{len(run_history)}` run(s). "
        "This means you can compare experiments instead of losing the older ones."
    )

    control_1, control_2 = st.columns(2)
    with control_1:
        if st.button("Create Excel file with all saved runs", use_container_width=True):
            try:
                export_path = export_run_history_to_excel(run_history)
                st.session_state["latest_export_path"] = str(export_path)
                st.success(f"Excel file created: {export_path.name}")
            except subprocess.CalledProcessError as exc:
                st.error(f"Could not create the Excel file. {exc.stderr or exc.stdout or exc}")
    with control_2:
        if st.button("Clear saved run history", use_container_width=True):
            st.session_state["run_history"] = []
            save_run_history_to_disk([])
            st.session_state.pop("latest_export_path", None)
            st.rerun()

    latest_export_path = st.session_state.get("latest_export_path")
    if latest_export_path and Path(latest_export_path).exists():
        export_bytes = Path(latest_export_path).read_bytes()
        st.download_button(
            label="Download the Excel file",
            data=export_bytes,
            file_name=Path(latest_export_path).name,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )
        st.caption(f"Latest export file: `{latest_export_path}`")


def app() -> None:
    st.set_page_config(page_title="Algorithm 1 Bullying Intervention Dashboard", layout="wide")
    ensure_session_history()
    apply_dashboard_css()
    st.title("Algorithm 1 Bullying Intervention Dashboard")
    st.caption(f"Source paper: {PAPER_TITLE}")

    st.info(
        "This dashboard is intentionally limited to Algorithm 1 and Appendix B definitions from the paper. "
        "The Algorithm 2 Theory-of-Mind branch is not implemented here because you asked to use Algorithm 1 only."
    )

    with st.sidebar:
        st.header("Simulation Controls")
        risk_profile = st.selectbox("Risk profile", ["Low", "Middle", "High"], index=1)
        training_episodes = st.slider("How many practice runs for learning", min_value=50, max_value=1_000, value=250, step=50)
        evaluation_episodes = st.slider("How many test runs after learning", min_value=10, max_value=300, value=50, step=10)
        episode_max_steps = st.slider("Maximum steps allowed in each run (paper Tmax = 20,000)", min_value=10, max_value=200, value=40, step=10)
        seed = st.number_input("Starting pattern number", min_value=1, max_value=999_999, value=42, step=1)
        st.caption(
            "This number controls the repeatable random starting patterns. If you use the same number again, you should get the same run setup."
        )
        run_button = st.button("Run Algorithm 1 Simulation", use_container_width=True)

        st.markdown("**Paper defaults shown in the dashboard**")
        st.write(f"Replay memory: {PAPER_HYPERPARAMETERS['Replay memory size']}")
        st.write(f"Minibatch size: {PAPER_HYPERPARAMETERS['Minibatch size']}")
        st.write(f"Gamma: {PAPER_HYPERPARAMETERS['Discount factor gamma']}")
        st.write(f"Lambda: {PAPER_HYPERPARAMETERS['Regularization coefficient lambda']}")
        st.write(f"Dropout: {PAPER_HYPERPARAMETERS['Dropout rate p']}")

    overview_tab, explainer_tab, simulation_tab, tables_tab = st.tabs(["Overview", "Plain English", "Simulation", "Paper Tables"])

    with overview_tab:
        st.markdown("**What this build uses from the paper**")
        st.markdown(
            "- Algorithm 1 structure from Section 5.3.1: DQN-style action-value learning, replay memory, target network, epsilon-guided exploration, and continual-learning regularization.\n"
            "- Appendix B state space, terminal conditions, action space, and reward equations.\n"
            "- Table 4 hyperparameters and Tables 5, 9, 10, 11, and 12 for reference views.\n"
            "- Rule-based behavior for AB, AV, and AT from Appendix B.3.1."
        )
        st.markdown("**Important paper-faithful constraint**")
        st.markdown(
            "Because the request was to use only Algorithm 1, the exploration branch that would call Algorithm 2 "
            "is disabled. Exploration samples from the paper's safe action subset instead."
        )
        st.markdown("**Small inference choices kept explicit**")
        st.markdown(
            "- `a6` and `a7` have base reward `0` here because the paper's piecewise base-reward equation names eight actions and does not assign explicit intrinsic values to those two movement actions.\n"
            "- The paper describes the environment semantically rather than with full transition probabilities, so the step-level resolution rules are minimal interpretations of Appendix B and Table 8.\n"
            f"- The paper's formal terminal limit is `Tmax = {T_MAX_PAPER:,}`. The dashboard defaults to a smaller live step cap for responsiveness, but keeps the paper's terminal definition visible."
        )
        st.markdown(f"**Paper file**: `{PDF_PATH}`")

    with explainer_tab:
        render_plain_english_explainer()

    with simulation_tab:
        if run_button:
            with st.spinner("Training and evaluating the Algorithm 1 observer agent..."):
                results = run_training(
                    risk_profile=risk_profile,
                    training_episodes=training_episodes,
                    evaluation_episodes=evaluation_episodes,
                    episode_max_steps=episode_max_steps,
                    seed=int(seed),
                )
            run_record = build_run_record(
                risk_profile=risk_profile,
                training_episodes=training_episodes,
                evaluation_episodes=evaluation_episodes,
                episode_max_steps=episode_max_steps,
                seed=int(seed),
                results=results,
            )
            st.session_state["run_history"].append(run_record)
            save_run_history_to_disk(st.session_state["run_history"])
            st.session_state["algorithm1_results"] = results
            st.session_state["algorithm1_risk_profile"] = risk_profile

        if "algorithm1_results" in st.session_state:
            render_results(st.session_state["algorithm1_results"], st.session_state["algorithm1_risk_profile"])
            render_run_history_section()
        else:
            st.write("Run the simulation from the sidebar to generate interactive results.")
            render_run_history_section()

    with tables_tab:
        render_paper_tables()


def smoke_test() -> None:
    results = run_training(
        risk_profile="Middle",
        training_episodes=20,
        evaluation_episodes=10,
        episode_max_steps=20,
        seed=42,
    )
    summary = {
        "interactive_isr": round(results["evaluation"]["isr"], 2),
        "interactive_aer": round(results["evaluation"]["aer"], 2),
        "final_epsilon": round(results["final_epsilon"], 6),
        "sample_actions": len(results["sample_episode"]),
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke-test", action="store_true")
    args = parser.parse_args()
    if args.smoke_test:
        smoke_test()
    else:
        app()
