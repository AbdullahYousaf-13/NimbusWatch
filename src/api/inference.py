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
    demo_scenarios: dict
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
        scenarios_path = base_dir / "demo_scenarios.json"
        if not scenarios_path.exists():
            fallback_path = Path("artifacts/generated/demo_scenarios.json")
            scenarios_path = fallback_path if fallback_path.exists() else scenarios_path
        demo_scenarios = load_json(scenarios_path) if scenarios_path.exists() else {"scenarios": []}
        return LoadedArtifacts(
            model_bundle=model_bundle,
            schema=schema,
            metrics=metrics,
            summary=summary,
            demo_scenarios=demo_scenarios,
            temp_dir=temp_dir,
        )

    @property
    def feature_names(self) -> list[str]:
        return list(self._loaded.schema["feature_names"])

    @property
    def threshold(self) -> float:
        return float(self._loaded.model_bundle["threshold"])

    @property
    def score_label(self) -> str:
        return str(self._loaded.model_bundle.get("score_label", "anomaly_score"))

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

    def normalize_payload(self, payload: dict[str, object]) -> dict[str, float]:
        return {key: float(value) for key, value in payload.items()}

    def validate_csv_frame(self, frame: pd.DataFrame) -> dict[str, float]:
        normalized_columns = [str(column).strip() for column in frame.columns]
        frame = frame.copy()
        frame.columns = normalized_columns
        if frame.shape[0] != 1:
            raise ValueError(
                json.dumps(
                    {
                        "message": "Upload exactly one CSV data row for prediction.",
                        "row_count": int(frame.shape[0]),
                    }
                )
            )

        payload = frame.iloc[0].to_dict()
        self.validate_payload(payload)
        return self.normalize_payload(payload)

    def predict(self, payload: dict[str, float]) -> dict:
        self.validate_payload(payload)
        row = pd.DataFrame([[payload[name] for name in self.feature_names]], columns=self.feature_names)
        transformed = self._loaded.model_bundle["preprocessor"].transform(row)
        model = self._loaded.model_bundle["model"]
        model_kind = self._loaded.model_bundle.get("model_kind", "anomaly_detector")
        if model_kind == "classifier":
            score = float(model.predict_proba(transformed)[0, 1])
        else:
            score = float(-model.score_samples(transformed)[0])
        prediction = "attack" if score >= self.threshold else "benign"
        return {
            "prediction": prediction,
            "anomaly_score": score,
            "score": score,
            "score_label": self.score_label,
            "threshold": self.threshold,
            "model_name": self._loaded.model_bundle["model_name"],
        }

    def demo_scenarios(self) -> dict:
        valid = []
        for scenario in self._loaded.demo_scenarios.get("scenarios", []):
            payload = scenario.get("payload", {})
            try:
                normalized = self.normalize_payload(payload)
                self.validate_payload(normalized)
            except (TypeError, ValueError):
                continue
            valid.append({**scenario, "payload": normalized})
        return {"scenarios": valid}

    def csv_template(self) -> str:
        header = ",".join(self.feature_names)
        values = ",".join("" for _ in self.feature_names)
        return f"{header}\n{values}\n"

    def model_info(self) -> dict:
        return {
            "model_name": self._loaded.model_bundle["model_name"],
            "threshold": self.threshold,
            "feature_count": len(self.feature_names),
            "feature_names": self.feature_names,
            "score_label": self.score_label,
            "selected_params": self._loaded.model_bundle["selected_params"],
            "metrics": self._loaded.metrics,
            "training_summary": self._loaded.summary,
        }

    def close(self) -> None:
        cleanup_dir(self._loaded.temp_dir)
