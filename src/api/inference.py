from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path

import joblib
import pandas as pd

from src.models.artifact_store import cleanup_dir, load_json, prepare_local_artifact_dir


@dataclass
class LoadedArtifacts:
    model_bundle: dict
    schema: dict
    metrics: dict
    summary: dict
    temp_dir: Path | None = None


class InferenceService:
    def __init__(self, artifact_uri: str | None = None, local_dir: str | None = None) -> None:
        self.artifact_uri = artifact_uri or os.getenv("ARTIFACT_GCS_URI", "").strip()
        self.local_dir = local_dir or os.getenv("ARTIFACT_DIR", "artifacts/generated")
        self._loaded = self._load_artifacts()

    def _load_artifacts(self) -> LoadedArtifacts:
        if self.artifact_uri:
            base_dir = prepare_local_artifact_dir(self.artifact_uri)
            temp_dir = base_dir
        else:
            base_dir = Path(self.local_dir)
            temp_dir = None

        model_bundle = joblib.load(base_dir / "model.joblib")
        schema = load_json(base_dir / "feature_schema.json")
        metrics = load_json(base_dir / "metrics.json")
        summary = load_json(base_dir / "training_summary.json")
        return LoadedArtifacts(model_bundle=model_bundle, schema=schema, metrics=metrics, summary=summary, temp_dir=temp_dir)

    @property
    def feature_names(self) -> list[str]:
        return list(self._loaded.schema["feature_names"])

    @property
    def threshold(self) -> float:
        return float(self._loaded.model_bundle["threshold"])

    def validate_payload(self, payload: dict[str, float]) -> None:
        expected = set(self.feature_names)
        received = set(payload.keys())
        missing = sorted(expected - received)
        extra = sorted(received - expected)
        if missing or extra:
            raise ValueError(
                json.dumps(
                    {
                        "missing_features": missing,
                        "extra_features": extra,
                    }
                )
            )

    def predict(self, payload: dict[str, float]) -> dict:
        self.validate_payload(payload)
        row = pd.DataFrame([[payload[name] for name in self.feature_names]], columns=self.feature_names)
        transformed = self._loaded.model_bundle["preprocessor"].transform(row)
        anomaly_score = float(-self._loaded.model_bundle["model"].score_samples(transformed)[0])
        prediction = "attack" if anomaly_score >= self.threshold else "benign"
        return {
            "prediction": prediction,
            "anomaly_score": anomaly_score,
            "threshold": self.threshold,
            "model_name": self._loaded.model_bundle["model_name"],
        }

    def model_info(self) -> dict:
        return {
            "model_name": self._loaded.model_bundle["model_name"],
            "threshold": self.threshold,
            "feature_count": len(self.feature_names),
            "feature_names": self.feature_names,
            "selected_params": self._loaded.model_bundle["selected_params"],
            "metrics": self._loaded.metrics,
            "training_summary": self._loaded.summary,
        }

    def close(self) -> None:
        cleanup_dir(self._loaded.temp_dir)
