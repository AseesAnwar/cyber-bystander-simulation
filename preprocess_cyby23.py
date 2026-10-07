from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


DEFAULT_DATASET_PATH = "data/CYBERBYSTANDER (CYBY23) dataset.xlsx"
FALLBACK_DATASET_CANDIDATES = [
    Path(DEFAULT_DATASET_PATH),
]

REQUIRED_COLUMNS = [
    "tweet_id",
    "reply_id",
    "created_at",
    "text",
    "user",
    "user_id",
    "sentiment",
    "Bystander Roles Label",
    "retweet_count",
    "favorite_count",
    "Insult",
    "Threat",
    "Identity_Attack",
    "Profanity",
    "Toxicity",
    "Severe_Toxicity",
    "polarity",
    "subjectivity",
    "Class label",
]

NUMERIC_COLUMNS = [
    "retweet_count",
    "favorite_count",
    "Insult",
    "Threat",
    "Identity_Attack",
    "Profanity",
    "Toxicity",
    "Severe_Toxicity",
    "polarity",
    "subjectivity",
    "Class label",
]

ROLE_MAP = {
    "This person agree with the main post": "reinforce",
    "agree with the main post": "reinforce",
    "This person disagree with the main post": "defend",
    "This person is not taking any sides": "neutral",
    "This person posting unrelated replies (e.g. Advertisement)": "unrelated",
}

NORMALIZED_ROLE_ORDER = ["reinforce", "defend", "neutral", "unrelated"]


@dataclass(slots=True)
class BystanderRecord:
    user: str
    user_id: str
    tweet_id: str
    reply_id: str
    created_at: str
    text: str
    role_label: str
    polarity: float
    subjectivity: float
    sentiment: str
    retweet_count: float
    favorite_count: float
    observed_toxicity: float


@dataclass(slots=True)
class ThreadRecord:
    thread_id: str
    source_tweet_id: str
    source_user: str
    source_text: str
    source_created_at: str
    source_class_label: float | None
    source_toxicity: float
    source_severe_toxicity: float
    source_threat: float
    source_insult: float
    source_identity_attack: float
    source_profanity: float
    source_polarity: float
    source_subjectivity: float
    source_sentiment: str
    source_retweet_count: float
    source_favorite_count: float
    risk_level: str
    bystanders: list[BystanderRecord]
    observed_role_distribution: dict[str, int]


def resolve_dataset_path(dataset_path: str | Path | None = None) -> Path:
    if dataset_path is not None:
        path = Path(dataset_path)
        if path.exists():
            return path
        if str(path) == DEFAULT_DATASET_PATH:
            for candidate in FALLBACK_DATASET_CANDIDATES:
                if candidate.exists():
                    return candidate
        raise FileNotFoundError(
            f"Dataset not found at '{path}'. "
            f"Pass --dataset-path explicitly or place the spreadsheet at '{DEFAULT_DATASET_PATH}'."
        )

    for candidate in FALLBACK_DATASET_CANDIDATES:
        if candidate.exists():
            return candidate

    raise FileNotFoundError(
        "Dataset file was not found. Tried: "
        + ", ".join(str(path) for path in FALLBACK_DATASET_CANDIDATES)
    )


def load_raw_dataset(dataset_path: str | Path | None = None) -> pd.DataFrame:
    path = resolve_dataset_path(dataset_path)
    try:
        df = pd.read_excel(path)
    except Exception as exc:  # pragma: no cover - defensive path
        raise RuntimeError(f"Unable to read Excel dataset at '{path}': {exc}") from exc

    if df.empty:
        raise ValueError(f"Dataset at '{path}' is empty.")

    return df


def validate_schema(df: pd.DataFrame) -> None:
    """Fail early with a readable message when required CYBY23 columns are missing."""

    missing = [column for column in REQUIRED_COLUMNS if column not in df.columns]
    if missing:
        raise ValueError(
            "CYBY23 dataset is missing required column(s): " + ", ".join(missing)
        )


def clean_dataset(df: pd.DataFrame) -> pd.DataFrame:
    validate_schema(df)
    cleaned = df.copy()
    cleaned = cleaned.dropna(how="all").reset_index(drop=True)

    for column in NUMERIC_COLUMNS:
        if column in cleaned.columns:
            cleaned[column] = pd.to_numeric(cleaned[column], errors="coerce")

    id_columns = ["tweet_id", "reply_id"]
    for column in id_columns:
        cleaned[column] = cleaned[column].apply(_normalize_identifier)

    if "created_at" in cleaned.columns:
        cleaned["created_at"] = pd.to_datetime(cleaned["created_at"], errors="coerce", utc=True)

    cleaned["text"] = cleaned["text"].fillna("").astype(str).str.strip()
    cleaned["user"] = cleaned["user"].fillna("unknown_user").astype(str)
    cleaned["user_id"] = cleaned["user_id"].fillna(cleaned["user"]).astype(str)
    cleaned["sentiment"] = cleaned["sentiment"].fillna("unknown").astype(str)
    cleaned["raw_bystander_role"] = cleaned["Bystander Roles Label"].fillna("").astype(str).str.strip()
    cleaned["normalized_bystander_role"] = cleaned["raw_bystander_role"].map(ROLE_MAP)

    cleaned["is_source_post"] = cleaned["tweet_id"].notna() & (
        (cleaned["tweet_id"] == cleaned["reply_id"]) | cleaned["reply_id"].isna()
    )
    cleaned["is_bystander_reply"] = (
        cleaned["reply_id"].notna() & cleaned["normalized_bystander_role"].notna()
    )

    return cleaned


def preprocessing_summary(cleaned_df: pd.DataFrame) -> dict[str, Any]:
    source_df = extract_source_posts(cleaned_df)
    reply_df = extract_bystander_replies(cleaned_df, source_df)

    missing_role_rows = int(cleaned_df["raw_bystander_role"].ne("").sum() - reply_df.shape[0])
    raw_role_counts = (
        cleaned_df.loc[cleaned_df["raw_bystander_role"].ne(""), "raw_bystander_role"]
        .value_counts()
        .to_dict()
    )
    normalized_role_counts = (
        reply_df["normalized_bystander_role"]
        .value_counts()
        .reindex(NORMALIZED_ROLE_ORDER, fill_value=0)
        .to_dict()
    )
    class_distribution = (
        source_df["Class label"]
        .fillna(-1)
        .astype(int)
        .value_counts()
        .sort_index()
        .to_dict()
    )

    thread_sizes = reply_df.groupby("reply_id").size()

    return {
        "rows_after_dropna": int(cleaned_df.shape[0]),
        "source_posts": int(source_df.shape[0]),
        "labelled_bystander_replies": int(reply_df.shape[0]),
        "unique_threads_with_labelled_replies": int(thread_sizes.shape[0]),
        "unmapped_role_rows_dropped": missing_role_rows,
        "raw_role_counts": raw_role_counts,
        "normalized_role_counts": normalized_role_counts,
        "source_class_distribution": class_distribution,
        "mean_labelled_replies_per_thread": round(float(thread_sizes.mean()), 2),
        "max_labelled_replies_per_thread": int(thread_sizes.max()) if not thread_sizes.empty else 0,
    }


def extract_source_posts(cleaned_df: pd.DataFrame) -> pd.DataFrame:
    source_df = cleaned_df.loc[cleaned_df["is_source_post"]].copy()
    source_df = source_df.drop_duplicates(subset=["tweet_id"]).reset_index(drop=True)
    return source_df


def extract_bystander_replies(
    cleaned_df: pd.DataFrame,
    source_df: pd.DataFrame | None = None,
) -> pd.DataFrame:
    sources = source_df if source_df is not None else extract_source_posts(cleaned_df)
    valid_source_ids = set(sources["tweet_id"].dropna().tolist())

    reply_df = cleaned_df.loc[cleaned_df["is_bystander_reply"]].copy()
    reply_df = reply_df.loc[reply_df["reply_id"].isin(valid_source_ids)].reset_index(drop=True)
    reply_df = reply_df.sort_values(["reply_id", "created_at", "tweet_id"], kind="stable")
    reply_df = reply_df.reset_index(drop=True)
    return reply_df


def build_thread_records(cleaned_df: pd.DataFrame) -> list[ThreadRecord]:
    source_df = extract_source_posts(cleaned_df)
    reply_df = extract_bystander_replies(cleaned_df, source_df)
    source_lookup = source_df.set_index("tweet_id", drop=False)
    thresholds = compute_risk_thresholds(source_df)

    thread_records: list[ThreadRecord] = []
    for reply_id, thread_replies in reply_df.groupby("reply_id", sort=True):
        if reply_id not in source_lookup.index:
            continue

        source_row = source_lookup.loc[reply_id]
        bystanders = [
            BystanderRecord(
                user=str(row["user"]),
                user_id=str(row["user_id"]),
                tweet_id=str(row["tweet_id"]),
                reply_id=str(row["reply_id"]),
                created_at=_serialize_timestamp(row["created_at"]),
                text=str(row["text"]),
                role_label=str(row["normalized_bystander_role"]),
                polarity=_safe_float(row.get("polarity")),
                subjectivity=_safe_float(row.get("subjectivity")),
                sentiment=str(row.get("sentiment", "unknown")),
                retweet_count=_safe_float(row.get("retweet_count")),
                favorite_count=_safe_float(row.get("favorite_count")),
                observed_toxicity=_safe_float(row.get("Toxicity")),
            )
            for _, row in thread_replies.iterrows()
        ]
        observed_distribution = (
            thread_replies["normalized_bystander_role"]
            .value_counts()
            .reindex(NORMALIZED_ROLE_ORDER, fill_value=0)
            .to_dict()
        )

        source_toxicity = _safe_float(source_row.get("Toxicity"))
        risk_level = classify_risk_level(source_toxicity, thresholds)
        thread_records.append(
            ThreadRecord(
                thread_id=str(reply_id),
                source_tweet_id=str(reply_id),
                source_user=str(source_row.get("user", "unknown_user")),
                source_text=str(source_row.get("text", "")),
                source_created_at=_serialize_timestamp(source_row.get("created_at")),
                source_class_label=_safe_optional_float(source_row.get("Class label")),
                source_toxicity=source_toxicity,
                source_severe_toxicity=_safe_float(source_row.get("Severe_Toxicity")),
                source_threat=_safe_float(source_row.get("Threat")),
                source_insult=_safe_float(source_row.get("Insult")),
                source_identity_attack=_safe_float(source_row.get("Identity_Attack")),
                source_profanity=_safe_float(source_row.get("Profanity")),
                source_polarity=_safe_float(source_row.get("polarity")),
                source_subjectivity=_safe_float(source_row.get("subjectivity")),
                source_sentiment=str(source_row.get("sentiment", "unknown")),
                source_retweet_count=_safe_float(source_row.get("retweet_count")),
                source_favorite_count=_safe_float(source_row.get("favorite_count")),
                risk_level=risk_level,
                bystanders=bystanders,
                observed_role_distribution=observed_distribution,
            )
        )

    thread_records.sort(key=lambda record: (record.risk_level, record.thread_id))
    return thread_records


def compute_risk_thresholds(source_df: pd.DataFrame) -> tuple[float, float]:
    toxicity_values = source_df["Toxicity"].dropna().astype(float)
    if toxicity_values.empty:
        return (0.33, 0.66)

    low_high_boundary = float(toxicity_values.quantile(0.33))
    medium_high_boundary = float(toxicity_values.quantile(0.66))
    return low_high_boundary, medium_high_boundary


def classify_risk_level(toxicity: float, thresholds: tuple[float, float]) -> str:
    low_high_boundary, medium_high_boundary = thresholds
    if toxicity < low_high_boundary:
        return "low"
    if toxicity < medium_high_boundary:
        return "medium"
    return "high"


def summarize_thread_records(thread_records: list[ThreadRecord]) -> dict[str, Any]:
    if not thread_records:
        return {"thread_count": 0}

    risk_counts = pd.Series([record.risk_level for record in thread_records]).value_counts().to_dict()
    observed_totals = {
        role: sum(record.observed_role_distribution.get(role, 0) for record in thread_records)
        for role in NORMALIZED_ROLE_ORDER
    }
    return {
        "thread_count": len(thread_records),
        "risk_level_counts": risk_counts,
        "observed_role_totals": observed_totals,
        "avg_bystanders_per_thread": round(
            float(np.mean([len(record.bystanders) for record in thread_records])),
            2,
        ),
    }


def make_summary_lines(summary: dict[str, Any]) -> list[str]:
    lines = [
        f"Rows after cleaning: {summary['rows_after_dropna']}",
        f"Source posts: {summary['source_posts']}",
        f"Labelled bystander replies: {summary['labelled_bystander_replies']}",
        f"Threads with labelled replies: {summary['unique_threads_with_labelled_replies']}",
        f"Unmapped role rows dropped: {summary['unmapped_role_rows_dropped']}",
        "Normalized role distribution:",
    ]
    for role in NORMALIZED_ROLE_ORDER:
        lines.append(f"  - {role}: {summary['normalized_role_counts'].get(role, 0)}")
    lines.append("Source class label distribution:")
    for class_label, count in summary["source_class_distribution"].items():
        label_name = "missing" if class_label == -1 else str(class_label)
        lines.append(f"  - {label_name}: {count}")
    return lines


def export_threads_as_frame(thread_records: list[ThreadRecord]) -> pd.DataFrame:
    rows = []
    for record in thread_records:
        base = {
            "thread_id": record.thread_id,
            "risk_level": record.risk_level,
            "source_toxicity": record.source_toxicity,
            "source_threat": record.source_threat,
            "source_insult": record.source_insult,
            "source_identity_attack": record.source_identity_attack,
            "source_sentiment": record.source_sentiment,
            "bystander_count": len(record.bystanders),
        }
        for role in NORMALIZED_ROLE_ORDER:
            base[f"observed_{role}"] = record.observed_role_distribution.get(role, 0)
        rows.append(base)
    return pd.DataFrame(rows)


def _normalize_identifier(value: Any) -> str | None:
    if pd.isna(value):
        return None
    if isinstance(value, (int, np.integer)):
        return str(int(value))
    if isinstance(value, (float, np.floating)):
        if np.isnan(value):
            return None
        return str(int(value))
    text = str(value).strip()
    return text or None


def _safe_float(value: Any) -> float:
    if value is None or pd.isna(value):
        return 0.0
    return float(value)


def _safe_optional_float(value: Any) -> float | None:
    if value is None or pd.isna(value):
        return None
    return float(value)


def _serialize_timestamp(value: Any) -> str:
    if value is None or pd.isna(value):
        return ""
    return pd.Timestamp(value).isoformat()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Inspect and preprocess the CYBY23 dataset.")
    parser.add_argument(
        "--dataset-path",
        default=DEFAULT_DATASET_PATH,
        help="Path to the CYBY23 Excel dataset.",
    )
    parser.add_argument(
        "--export-thread-summary",
        default="thread_summary.csv",
        help="CSV path for an exported per-thread summary.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    requested_path = Path(args.dataset_path)
    dataset_path = (
        requested_path
        if requested_path.exists()
        else resolve_dataset_path(None if requested_path == Path(DEFAULT_DATASET_PATH) else requested_path)
    )

    raw_df = load_raw_dataset(dataset_path)
    cleaned_df = clean_dataset(raw_df)
    summary = preprocessing_summary(cleaned_df)
    thread_records = build_thread_records(cleaned_df)
    thread_summary_df = export_threads_as_frame(thread_records)
    thread_summary_df.to_csv(args.export_thread_summary, index=False)

    print(f"Dataset used: {dataset_path}")
    if str(dataset_path) != str(requested_path):
        print(f"Requested dataset path not found, used fallback path: {dataset_path}")
    for line in make_summary_lines(summary):
        print(line)
    print(f"Exported thread summary to {args.export_thread_summary}")
    print(f"Thread records built: {len(thread_records)}")
    print("Sample thread:")
    if thread_records:
        print(asdict(thread_records[0]))


if __name__ == "__main__":
    main()
