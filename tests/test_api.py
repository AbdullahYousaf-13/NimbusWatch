from __future__ import annotations

import importlib
import io

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


def test_demo_scenarios_endpoint_returns_schema_valid_payloads(monkeypatch, trained_artifacts):
    with load_test_client(monkeypatch, trained_artifacts) as client:
        info = client.get("/model-info").json()
        expected = set(info["feature_names"])

        response = client.get("/demo-scenarios")
        assert response.status_code == 200
        scenarios = response.json()["scenarios"]
        assert scenarios
        for scenario in scenarios:
            assert set(scenario["payload"].keys()) == expected


def test_predict_csv_accepts_single_row_template(monkeypatch, trained_artifacts):
    with load_test_client(monkeypatch, trained_artifacts) as client:
        info = client.get("/model-info").json()
        header = ",".join(info["feature_names"])
        values = ",".join("0" for _ in info["feature_names"])
        response = client.post(
            "/predict-csv",
            files={"file": ("sample.csv", io.BytesIO(f"{header}\n{values}\n".encode("utf-8")), "text/csv")},
        )
        assert response.status_code == 200
        assert response.json()["prediction"] in {"benign", "attack"}


def test_predict_csv_reports_schema_mismatch(monkeypatch, trained_artifacts):
    with load_test_client(monkeypatch, trained_artifacts) as client:
        info = client.get("/model-info").json()
        valid_names = list(info["feature_names"])
        header = ",".join(valid_names[1:] + ["unexpected_feature"])
        values = ",".join("0" for _ in valid_names)
        response = client.post(
            "/predict-csv",
            files={"file": ("bad.csv", io.BytesIO(f"{header}\n{values}\n".encode("utf-8")), "text/csv")},
        )
        assert response.status_code == 422
        detail = response.json()["detail"]
        assert valid_names[0] in detail["missing_features"]
        assert "unexpected_feature" in detail["extra_features"]


def test_index_defaults_to_guided_demo(monkeypatch, trained_artifacts):
    with load_test_client(monkeypatch, trained_artifacts) as client:
        response = client.get("/")
        assert response.status_code == 200
        assert "Guided Demo" in response.text
        assert "Advanced Mode" in response.text
        assert "Try your own template" in response.text
