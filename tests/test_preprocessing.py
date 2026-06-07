from __future__ import annotations

import numpy as np
import pandas as pd

from src.models.preprocessing import build_preprocessing_pipeline, prepare_dataset


def test_prepare_dataset_cleans_invalid_values():
    frame = pd.DataFrame(
        {
            "Flow Duration": [1.0, np.inf, 3.0],
            "Flow Bytes/s": [np.nan, 2.0, -np.inf],
            "Label": ["BENIGN", "DoS Hulk", "BENIGN"],
        }
    )

    prepared = prepare_dataset(frame)
    assert prepared.feature_names == ["Flow Duration", "Flow Bytes/s"]

    preprocessor = build_preprocessing_pipeline(scaler_kind="robust")
    transformed = preprocessor.fit_transform(prepared.features)
    assert transformed.shape == (3, 2)
    assert np.isfinite(transformed).all()
    assert preprocessor.get_config()["scaler_kind"] == "robust"
