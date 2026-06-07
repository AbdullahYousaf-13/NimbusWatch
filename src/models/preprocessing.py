from __future__ import annotations

import json
from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.preprocessing import RobustScaler, StandardScaler

from src.config import DEFAULT_BENIGN_LABEL, DEFAULT_TARGET_COLUMN, DROP_COLUMNS


@dataclass
class PreparedDataset:
    features: pd.DataFrame
    labels: pd.Series
    feature_names: list[str]


class FeaturePreprocessor(BaseEstimator, TransformerMixin):
    def __init__(
        self,
        scaler_kind: str = "standard",
        clip_quantile: float = 0.01,
        skew_threshold: float = 1.0,
    ) -> None:
        self.scaler_kind = scaler_kind
        self.clip_quantile = clip_quantile
        self.skew_threshold = skew_threshold

    def fit(self, x: pd.DataFrame, y: pd.Series | None = None) -> "FeaturePreprocessor":
        frame = self._coerce_frame(x)
        self.feature_names_in_ = list(frame.columns)
        self.medians_ = frame.median()
        imputed = frame.fillna(self.medians_)

        lower_q = self.clip_quantile
        upper_q = 1.0 - self.clip_quantile
        self.lower_bounds_ = imputed.quantile(lower_q)
        self.upper_bounds_ = imputed.quantile(upper_q)

        clipped = imputed.clip(lower=self.lower_bounds_, upper=self.upper_bounds_, axis=1)
        skew = clipped.skew(numeric_only=True).fillna(0.0)
        self.log_columns_ = [
            column
            for column in self.feature_names_in_
            if float(self.lower_bounds_[column]) >= 0.0 and float(skew[column]) >= self.skew_threshold
        ]

        transformed = clipped.copy()
        if self.log_columns_:
            transformed.loc[:, self.log_columns_] = np.log1p(transformed[self.log_columns_])

        scaler = self._build_scaler()
        scaler.fit(transformed.to_numpy())
        self.scaler_ = scaler
        return self

    def transform(self, x: pd.DataFrame) -> np.ndarray:
        frame = self._coerce_frame(x)
        transformed = frame.fillna(self.medians_)
        transformed = transformed.clip(lower=self.lower_bounds_, upper=self.upper_bounds_, axis=1)
        if self.log_columns_:
            transformed.loc[:, self.log_columns_] = np.log1p(transformed[self.log_columns_])
        return self.scaler_.transform(transformed.to_numpy())

    def get_config(self) -> dict:
        return {
            "scaler_kind": self.scaler_kind,
            "clip_quantile": self.clip_quantile,
            "skew_threshold": self.skew_threshold,
            "log_feature_count": len(getattr(self, "log_columns_", [])),
            "log_features": list(getattr(self, "log_columns_", [])),
        }

    def _build_scaler(self) -> StandardScaler | RobustScaler:
        if self.scaler_kind == "robust":
            return RobustScaler()
        if self.scaler_kind != "standard":
            raise ValueError(f"Unsupported scaler_kind: {self.scaler_kind}")
        return StandardScaler()

    def _coerce_frame(self, x: pd.DataFrame) -> pd.DataFrame:
        frame = pd.DataFrame(x).copy()
        if hasattr(self, "feature_names_in_"):
            frame = frame.loc[:, self.feature_names_in_]
        frame = frame.apply(pd.to_numeric, errors="coerce")
        return frame.replace([np.inf, -np.inf], np.nan)


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


def build_preprocessing_pipeline(
    scaler_kind: str = "standard",
    clip_quantile: float = 0.01,
    skew_threshold: float = 1.0,
) -> FeaturePreprocessor:
    return FeaturePreprocessor(
        scaler_kind=scaler_kind,
        clip_quantile=clip_quantile,
        skew_threshold=skew_threshold,
    )


def write_schema(path: str, feature_names: list[str]) -> None:
    schema = {
        "feature_names": feature_names,
        "feature_count": len(feature_names),
    }
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(schema, handle, indent=2)
