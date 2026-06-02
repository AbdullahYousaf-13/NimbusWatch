from __future__ import annotations

from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent
ARTIFACTS_DIR = ROOT_DIR / "artifacts" / "generated"
DEFAULT_MODEL_PATH = ARTIFACTS_DIR / "model.joblib"
DEFAULT_SCHEMA_PATH = ARTIFACTS_DIR / "feature_schema.json"
DEFAULT_METRICS_PATH = ARTIFACTS_DIR / "metrics.json"
DEFAULT_SUMMARY_PATH = ARTIFACTS_DIR / "training_summary.json"

DEFAULT_TARGET_COLUMN = "Label"
DEFAULT_BENIGN_LABEL = "BENIGN"
DEFAULT_RANDOM_STATE = 42

# CICIDS2017 columns that are identifiers or easy leakage candidates.
DROP_COLUMNS = {
    "Flow ID",
    "Source IP",
    "Source Port",
    "Destination IP",
    "Destination Port",
    "Timestamp",
    "SimillarHTTP",
}
