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
    assert set(metrics.keys()) == {"validation", "test"}
    for section in ("validation", "test"):
        assert "precision" in metrics[section]
        assert "recall" in metrics[section]
        assert "f1" in metrics[section]
    assert "pr_auc" in metrics["test"]
    assert "roc_auc" in metrics["test"]
    assert "confusion_matrix" in metrics["test"]


def test_feature_schema_matches_training_output(trained_artifacts):
    schema = load_json(trained_artifacts / "feature_schema.json")
    assert schema["feature_count"] == len(schema["feature_names"])
    assert "Label" not in schema["feature_names"]
    assert all(isinstance(name, str) for name in schema["feature_names"])
