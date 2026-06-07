from __future__ import annotations

import json

from src.models.artifact_store import load_json


def test_training_exports_required_artifacts(trained_artifacts):
    assert (trained_artifacts / "model.joblib").exists()
    assert (trained_artifacts / "feature_schema.json").exists()
    assert (trained_artifacts / "metrics.json").exists()
    assert (trained_artifacts / "training_summary.json").exists()


def test_metrics_json_contains_required_keys(trained_artifacts):
    metrics = load_json(trained_artifacts / "metrics.json")
    assert {"validation", "test", "operational"} <= set(metrics.keys())
    for section in ("validation", "test"):
        assert "precision" in metrics[section]
        assert "recall" in metrics[section]
        assert "f1" in metrics[section]
    assert "pr_auc" in metrics["test"]
    assert "roc_auc" in metrics["test"]
    assert "confusion_matrix" in metrics["test"]
    assert metrics["validation"]["selection_strategy"] == "balanced_f1"
    assert "artifact_size_bytes" in metrics["operational"]
    assert "single_row_latency_ms_p50" in metrics["operational"]


def test_feature_schema_matches_training_output(trained_artifacts):
    schema = load_json(trained_artifacts / "feature_schema.json")
    assert schema["feature_count"] == len(schema["feature_names"])
    assert "Label" not in schema["feature_names"]
    assert all(isinstance(name, str) for name in schema["feature_names"])


def test_training_summary_includes_feature_selection_and_experiments(trained_artifacts):
    summary = load_json(trained_artifacts / "training_summary.json")
    assert summary["selected_feature_count"] == len(summary["selected_features"])
    assert summary["experiment_count"] >= 1
    assert "feature_selection" in summary
    assert len(summary["top_experiments"]) >= 1
    assert "preprocessor_config" in summary
