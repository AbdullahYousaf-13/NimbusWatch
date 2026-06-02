from __future__ import annotations

import json
from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from src.config import DEFAULT_BENIGN_LABEL, DEFAULT_TARGET_COLUMN, DROP_COLUMNS


@dataclass
class PreparedDataset:
    features: pd.DataFrame
    labels: pd.Series
    feature_names: list[str]


def normalize_label(value: object) -> int:
    return 0 if str(value).strip().upper() == DEFAULT_BENIGN_LABEL else 1


def load_dataset(csv_paths: list[str], target_column: str = DEFAULT_TARGET_COLUMN) -> pd.DataFrame:
    frames = []
    for csv_path in csv_paths:
        frame = pd.read_csv(csv_path, low_memory=False, skipinitialspace=True)
        frame.columns = [str(column).strip() for column in frame.columns]
        frames.append(frame)
    merged = pd.concat(frames, ignore_index=True)
    if target_column not in merged.columns:
        raise ValueError(f"Target column '{target_column}' not found in dataset.")
    return merged


def select_feature_columns(dataframe: pd.DataFrame, target_column: str = DEFAULT_TARGET_COLUMN) -> list[str]:
    columns = []
    for column in dataframe.columns:
        if column == target_column or column in DROP_COLUMNS:
            continue
        if dataframe[column].dtype == object:
            continue
        if dataframe[column].isna().all():
            continue
        columns.append(column)
    if not columns:
        raise ValueError("No numeric feature columns remain after preprocessing.")
    return columns


def prepare_dataset(dataframe: pd.DataFrame, target_column: str = DEFAULT_TARGET_COLUMN) -> PreparedDataset:
    labels = dataframe[target_column].map(normalize_label).astype(int)
    feature_names = select_feature_columns(dataframe, target_column=target_column)
    features = dataframe[feature_names].replace([np.inf, -np.inf], np.nan)
    features = features.apply(pd.to_numeric, errors="coerce")
    return PreparedDataset(features=features, labels=labels, feature_names=feature_names)


def build_preprocessing_pipeline() -> Pipeline:
    return Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )


def write_schema(path: str, feature_names: list[str]) -> None:
    schema = {
        "feature_names": feature_names,
        "feature_count": len(feature_names),
    }
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(schema, handle, indent=2)
