from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.models.train import train_model


@pytest.fixture()
def trained_artifacts(tmp_path: Path) -> Path:
    rng = np.random.default_rng(42)
    benign_rows = 80
    attack_rows = 20

    benign = pd.DataFrame(
        {
            "Flow Duration": rng.normal(1000, 50, benign_rows),
            "Total Fwd Packets": rng.normal(20, 3, benign_rows),
            "Total Backward Packets": rng.normal(18, 3, benign_rows),
            "Flow Bytes/s": rng.normal(400, 40, benign_rows),
            "SYN Flag Count": rng.integers(0, 2, benign_rows),
            "ACK Flag Count": rng.integers(10, 14, benign_rows),
            "Average Packet Size": rng.normal(150, 8, benign_rows),
            "Idle Mean": rng.normal(200, 15, benign_rows),
            "Label": ["BENIGN"] * benign_rows,
        }
    )
    attack = pd.DataFrame(
        {
            "Flow Duration": rng.normal(7000, 500, attack_rows),
            "Total Fwd Packets": rng.normal(120, 12, attack_rows),
            "Total Backward Packets": rng.normal(4, 2, attack_rows),
            "Flow Bytes/s": rng.normal(2800, 220, attack_rows),
            "SYN Flag Count": rng.integers(4, 8, attack_rows),
            "ACK Flag Count": rng.integers(0, 3, attack_rows),
            "Average Packet Size": rng.normal(520, 30, attack_rows),
            "Idle Mean": rng.normal(18, 6, attack_rows),
            "Label": ["DoS Hulk"] * attack_rows,
        }
    )

    dataset = pd.concat([benign, attack], ignore_index=True)
    dataset.loc[0, "Flow Bytes/s"] = np.inf
    dataset.loc[1, "Idle Mean"] = np.nan

    csv_path = tmp_path / "subset.csv"
    output_dir = tmp_path / "artifacts"
    dataset.to_csv(csv_path, index=False)
    train_model([str(csv_path)], "Label", output_dir, random_state=42, max_benign_train_rows=120000)
    return output_dir
