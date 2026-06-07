from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


def _scenario_blueprints() -> list[dict[str, str]]:
    return [
        {
            "id": "normal-browsing",
            "match": "BENIGN",
            "title": "Normal browsing",
            "description": "A typical non-malicious flow with steady packet behavior and normal acknowledgement traffic.",
            "expected_label": "benign",
            "notes": "This example represents ordinary client-server activity rather than an attack burst.",
        },
        {
            "id": "ddos-like",
            "match": "DDOS",
            "title": "DDoS-like traffic",
            "description": "A high-volume flow pattern that resembles denial-of-service behavior with aggressive packet rates.",
            "expected_label": "attack",
            "notes": "This row comes from the curated attack subset and is useful for showing obvious abnormal traffic.",
        },
        {
            "id": "ftp-bruteforce",
            "match": "FTP-PATATOR",
            "title": "Brute-force login attempt",
            "description": "Repeated login attempts can create bursty traffic and unusual session timing compared with normal use.",
            "expected_label": "attack",
            "notes": "This scenario demonstrates suspicious authentication-style traffic rather than a volume attack.",
        },
        {
            "id": "web-attack",
            "match": "WEB ATTACK",
            "title": "Web attack sample",
            "description": "This flow resembles a web application attack pattern and is included as a more targeted malicious example.",
            "expected_label": "attack",
            "notes": "Web-attack rows are rarer in the curated subset, so the exact source label may vary slightly.",
        },
    ]


def build_demo_scenarios(
    features: pd.DataFrame,
    labels: pd.Series,
    feature_names: list[str],
    limit: int = 4,
) -> dict[str, list[dict[str, object]]]:
    dataset = features.loc[:, feature_names].copy()
    dataset = dataset.apply(pd.to_numeric, errors="coerce")
    dataset = dataset.replace([float("inf"), float("-inf")], pd.NA)
    dataset = dataset.fillna(dataset.median(numeric_only=True))
    dataset["__label__"] = labels.astype(str)
    dataset["__label_upper__"] = dataset["__label__"].str.upper()

    scenarios: list[dict[str, object]] = []
    used_indices: set[int] = set()

    for blueprint in _scenario_blueprints():
        if len(scenarios) >= limit:
            break
        matches = dataset[dataset["__label_upper__"].str.contains(blueprint["match"], na=False)]
        if matches.empty:
            continue
        index = int(matches.index[0])
        used_indices.add(index)
        row = matches.iloc[0]
        payload = {name: float(row[name]) for name in feature_names}
        scenarios.append(
            {
                "id": blueprint["id"],
                "title": blueprint["title"],
                "description": blueprint["description"],
                "expected_label": blueprint["expected_label"],
                "source_label": str(row["__label__"]),
                "notes": [
                    blueprint["notes"],
                    "NimbusWatch scores extracted network-flow features, not raw packet captures.",
                ],
                "payload": payload,
            }
        )

    if not scenarios:
        for idx, row in dataset.head(limit).iterrows():
            payload = {name: float(row[name]) for name in feature_names}
            scenarios.append(
                {
                    "id": f"sample-{idx}",
                    "title": f"Sample flow {len(scenarios) + 1}",
                    "description": "Representative row from the curated dataset.",
                    "expected_label": "attack" if str(row["__label__"]).strip().upper() != "BENIGN" else "benign",
                    "source_label": str(row["__label__"]),
                    "notes": [
                        "Fallback sample because no named demo blueprint matched the available labels.",
                    ],
                    "payload": payload,
                }
            )

    if len(scenarios) < limit:
        remaining = dataset.loc[~dataset.index.isin(used_indices)]
        for idx, row in remaining.iterrows():
            if len(scenarios) >= limit:
                break
            payload = {name: float(row[name]) for name in feature_names}
            scenarios.append(
                {
                    "id": f"sample-{idx}",
                    "title": f"Additional sample {len(scenarios) + 1}",
                    "description": "Extra representative row from the curated dataset.",
                    "expected_label": "attack" if str(row["__label__"]).strip().upper() != "BENIGN" else "benign",
                    "source_label": str(row["__label__"]),
                    "notes": [
                        "Supplemental example added to keep the guided demo populated.",
                    ],
                    "payload": payload,
                }
            )

    return {"scenarios": scenarios[:limit]}


def write_demo_scenarios(path: str | Path, scenarios: dict[str, list[dict[str, object]]]) -> None:
    destination = Path(path)
    destination.write_text(json.dumps(scenarios, indent=2), encoding="utf-8")
