from __future__ import annotations

import argparse
import json
import time
from dataclasses import asdict, dataclass
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.metrics import average_precision_score, confusion_matrix, f1_score, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import ParameterGrid, train_test_split

from src.config import (
    ARTIFACTS_DIR,
    DEFAULT_RANDOM_STATE,
    DEFAULT_TARGET_COLUMN,
)
from src.models.artifact_store import ensure_local_dir, is_gcs_path, upload_directory
from src.models.preprocessing import build_preprocessing_pipeline, load_dataset, prepare_dataset, write_schema


@dataclass
class TrainingArtifacts:
    model_name: str
    threshold: float
    selected_params: dict
    preprocessor_config: dict
    train_rows: int
    validation_rows: int
    test_rows: int
    benign_train_rows: int
    benign_train_rows_used: int
    attack_validation_rows: int
    attack_test_rows: int
    selected_feature_count: int
    selected_features: list[str]
    feature_selection: dict
    experiment_count: int
    top_experiments: list[dict]


def load_csv_paths(raw_paths: str) -> list[str]:
    return [item.strip() for item in raw_paths.split(",") if item.strip()]


def fit_and_score(
    x_train_benign: np.ndarray,
    x_validation: np.ndarray,
    y_validation: pd.Series,
    params: dict,
) -> tuple[IsolationForest, float, dict]:
    model = IsolationForest(**params)
    model.fit(x_train_benign)

    scores = -model.score_samples(x_validation)
    candidate_thresholds = np.quantile(scores, np.linspace(0.4, 0.995, 60))
    candidate_thresholds = np.unique(candidate_thresholds)

    best_threshold = None
    best_metrics = None

    for threshold in candidate_thresholds:
        preds = (scores >= threshold).astype(int)
        precision = precision_score(y_validation, preds, zero_division=0)
        recall = recall_score(y_validation, preds, zero_division=0)
        f1 = f1_score(y_validation, preds, zero_division=0)
        balance_gap = abs(precision - recall)
        score = f1 - (0.1 * balance_gap)
        if best_metrics is None or score > best_metrics["selection_score"]:
            best_threshold = float(threshold)
            best_metrics = {
                "selection_strategy": "balanced_f1",
                "selection_score": float(score),
                "precision": float(precision),
                "recall": float(recall),
                "f1": float(f1),
                "balance_gap": float(balance_gap),
            }

    return model, best_threshold, best_metrics


def evaluate_model(model: IsolationForest, threshold: float, x_test: np.ndarray, y_test: pd.Series) -> dict:
    scores = -model.score_samples(x_test)
    preds = (scores >= threshold).astype(int)
    metrics = {
        "precision": float(precision_score(y_test, preds, zero_division=0)),
        "recall": float(recall_score(y_test, preds, zero_division=0)),
        "f1": float(f1_score(y_test, preds, zero_division=0)),
        "roc_auc": float(roc_auc_score(y_test, scores)),
        "pr_auc": float(average_precision_score(y_test, scores)),
        "confusion_matrix": confusion_matrix(y_test, preds).tolist(),
    }
    return metrics


def select_training_features(
    x_train_benign: pd.DataFrame,
    min_variance: float = 1e-4,
    correlation_threshold: float = 0.98,
) -> tuple[list[str], dict]:
    filled = x_train_benign.apply(pd.to_numeric, errors="coerce").replace([np.inf, -np.inf], np.nan)
    medians = filled.median()
    filled = filled.fillna(medians)

    variances = filled.var().sort_values(ascending=False)
    variance_kept = variances[variances > min_variance]
    if variance_kept.empty:
        variance_kept = variances.head(min(8, len(variances)))

    candidate_columns = list(variance_kept.index)
    correlation = filled[candidate_columns].corr().abs().fillna(0.0)
    selected: list[str] = []
    dropped_correlated: list[str] = []

    for column in candidate_columns:
        if any(float(correlation.loc[column, chosen]) >= correlation_threshold for chosen in selected):
            dropped_correlated.append(column)
            continue
        selected.append(column)

    if not selected:
        selected = candidate_columns[: min(8, len(candidate_columns))]

    summary = {
        "min_variance": min_variance,
        "correlation_threshold": correlation_threshold,
        "initial_feature_count": int(x_train_benign.shape[1]),
        "kept_after_variance_filter": int(len(candidate_columns)),
        "selected_feature_count": int(len(selected)),
        "dropped_low_variance": sorted(set(x_train_benign.columns) - set(candidate_columns)),
        "dropped_correlated": dropped_correlated,
    }
    return selected, summary


def benchmark_inference_latency(preprocessor, model: IsolationForest, threshold: float, sample: pd.DataFrame) -> dict:
    runs = 20
    timings_ms = []
    for _ in range(runs):
        started = time.perf_counter()
        transformed = preprocessor.transform(sample)
        score = float(-model.score_samples(transformed)[0])
        _ = score >= threshold
        timings_ms.append((time.perf_counter() - started) * 1000)

    return {
        "single_row_latency_ms_p50": float(np.percentile(timings_ms, 50)),
        "single_row_latency_ms_p95": float(np.percentile(timings_ms, 95)),
        "benchmark_runs": runs,
    }


def save_artifacts(
    output_dir: Path,
    model_bundle: dict,
    feature_names: list[str],
    metrics: dict,
    training_summary: dict,
) -> None:
    ensure_local_dir(output_dir)
    joblib.dump(model_bundle, output_dir / "model.joblib")
    metrics.setdefault("operational", {})
    metrics["operational"]["artifact_size_bytes"] = int((output_dir / "model.joblib").stat().st_size)
    write_schema(str(output_dir / "feature_schema.json"), feature_names)
    (output_dir / "metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    (output_dir / "training_summary.json").write_text(json.dumps(training_summary, indent=2), encoding="utf-8")


def train_model(
    csv_paths: list[str],
    target_column: str,
    output_dir: Path,
    random_state: int,
    max_benign_train_rows: int,
) -> tuple[dict, dict]:
    dataframe = load_dataset(csv_paths, target_column=target_column)
    prepared = prepare_dataset(dataframe, target_column=target_column)

    x_train_full, x_test, y_train_full, y_test = train_test_split(
        prepared.features,
        prepared.labels,
        test_size=0.2,
        stratify=prepared.labels,
        random_state=random_state,
    )
    x_train, x_validation, y_train, y_validation = train_test_split(
        x_train_full,
        y_train_full,
        test_size=0.25,
        stratify=y_train_full,
        random_state=random_state,
    )

    benign_mask = y_train == 0
    x_train_benign = x_train.loc[benign_mask]
    if max_benign_train_rows > 0 and len(x_train_benign) > max_benign_train_rows:
        x_train_benign = x_train_benign.sample(n=max_benign_train_rows, random_state=random_state)

    selected_features, feature_selection_summary = select_training_features(x_train_benign)
    x_train_benign = x_train_benign.loc[:, selected_features]
    x_validation_selected = x_validation.loc[:, selected_features]
    x_test_selected = x_test.loc[:, selected_features]

    parameter_grid = list(
        ParameterGrid(
            {
                "preprocessor__scaler_kind": ["standard", "robust"],
                "preprocessor__clip_quantile": [0.01, 0.02],
                "n_estimators": [150, 250],
                "max_samples": ["auto"],
                "max_features": [0.6, 1.0],
                "contamination": [0.01, 0.02, 0.05],
                "random_state": [random_state],
            }
        )
    )

    best = None
    experiments: list[dict] = []
    for params in parameter_grid:
        preprocess = build_preprocessing_pipeline(
            scaler_kind=params["preprocessor__scaler_kind"],
            clip_quantile=params["preprocessor__clip_quantile"],
        )
        x_train_benign_processed = preprocess.fit_transform(x_train_benign)
        x_validation_processed = preprocess.transform(x_validation_selected)
        x_test_processed = preprocess.transform(x_test_selected)

        model_params = {
            key: value
            for key, value in params.items()
            if not key.startswith("preprocessor__")
        }
        model, threshold, validation_metrics = fit_and_score(
            x_train_benign_processed,
            x_validation_processed,
            y_validation,
            model_params,
        )
        score = validation_metrics["selection_score"]
        experiment = {
            "selected_params": model_params,
            "preprocessor_config": preprocess.get_config(),
            "validation": validation_metrics,
            "selected_feature_count": len(selected_features),
        }
        experiments.append(experiment)
        if best is None or score > best["score"]:
            best = {
                "model": model,
                "threshold": threshold,
                "params": model_params,
                "preprocessor": preprocess,
                "validation_metrics": validation_metrics,
                "score": score,
                "x_test_processed": x_test_processed,
            }

    test_metrics = evaluate_model(best["model"], best["threshold"], best["x_test_processed"], y_test)
    latency_metrics = benchmark_inference_latency(
        best["preprocessor"],
        best["model"],
        best["threshold"],
        x_test_selected.iloc[[0]],
    )
    metrics = {
        "validation": best["validation_metrics"],
        "test": test_metrics,
        "operational": {
            **latency_metrics,
        },
    }
    top_experiments = sorted(experiments, key=lambda item: item["validation"]["selection_score"], reverse=True)[:5]
    training_summary = asdict(
        TrainingArtifacts(
            model_name="IsolationForest",
            threshold=best["threshold"],
            selected_params=best["params"],
            preprocessor_config=best["preprocessor"].get_config(),
            train_rows=int(len(x_train)),
            validation_rows=int(len(x_validation)),
            test_rows=int(len(x_test)),
            benign_train_rows=int(benign_mask.sum()),
            benign_train_rows_used=int(len(x_train_benign)),
            attack_validation_rows=int((y_validation == 1).sum()),
            attack_test_rows=int((y_test == 1).sum()),
            selected_feature_count=int(len(selected_features)),
            selected_features=selected_features,
            feature_selection=feature_selection_summary,
            experiment_count=int(len(experiments)),
            top_experiments=top_experiments,
        )
    )
    model_bundle = {
        "model_name": "IsolationForest",
        "model": best["model"],
        "preprocessor": best["preprocessor"],
        "threshold": best["threshold"],
        "feature_names": selected_features,
        "selected_params": best["params"],
    }

    save_artifacts(output_dir, model_bundle, selected_features, metrics, training_summary)
    return metrics, training_summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train Isolation Forest on CICIDS2017 subset.")
    parser.add_argument("--csv-paths", required=True, help="Comma-separated local CSV paths.")
    parser.add_argument("--target-column", default=DEFAULT_TARGET_COLUMN)
    parser.add_argument("--output-dir", default=str(ARTIFACTS_DIR))
    parser.add_argument("--artifact-gcs-uri", default="")
    parser.add_argument("--random-state", type=int, default=DEFAULT_RANDOM_STATE)
    parser.add_argument("--max-benign-train-rows", type=int, default=120000)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    csv_paths = load_csv_paths(args.csv_paths)
    output_dir = Path(args.output_dir)
    metrics, training_summary = train_model(
        csv_paths=csv_paths,
        target_column=args.target_column,
        output_dir=output_dir,
        random_state=args.random_state,
        max_benign_train_rows=args.max_benign_train_rows,
    )

    if args.artifact_gcs_uri and is_gcs_path(args.artifact_gcs_uri):
        upload_directory(
            output_dir,
            args.artifact_gcs_uri,
            ("model.joblib", "feature_schema.json", "metrics.json", "training_summary.json"),
        )

    print(json.dumps({"metrics": metrics, "summary": training_summary}, indent=2))


if __name__ == "__main__":
    main()
