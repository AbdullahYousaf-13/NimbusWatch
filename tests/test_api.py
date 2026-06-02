from __future__ import annotations

import importlib

from fastapi.testclient import TestClient


def load_test_client(monkeypatch, trained_artifacts):
    monkeypatch.setenv("ARTIFACT_DIR", str(trained_artifacts))
    import src.api.app as app_module

    app_module = importlib.reload(app_module)
    return TestClient(app_module.app)


def test_health_endpoint(monkeypatch, trained_artifacts):
    with load_test_client(monkeypatch, trained_artifacts) as client:
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"


def test_predict_accepts_exact_schema(monkeypatch, trained_artifacts):
    with load_test_client(monkeypatch, trained_artifacts) as client:
        info = client.get("/model-info").json()
        payload = {name: 0.0 for name in info["feature_names"]}
        response = client.post("/predict", json=payload)
        assert response.status_code == 200
        body = response.json()
        assert body["prediction"] in {"benign", "attack"}
        assert "anomaly_score" in body
        assert "threshold" in body


def test_predict_rejects_missing_or_extra_features(monkeypatch, trained_artifacts):
    with load_test_client(monkeypatch, trained_artifacts) as client:
        info = client.get("/model-info").json()
        payload = {name: 0.0 for name in info["feature_names"]}
        first_feature = info["feature_names"][0]
        payload.pop(first_feature)
        payload["unexpected_feature"] = 1.0

        response = client.post("/predict", json=payload)
        assert response.status_code == 422
        detail = response.json()["detail"]
        assert first_feature in detail["missing_features"]
        assert "unexpected_feature" in detail["extra_features"]
