from __future__ import annotations

import json
import os
import shutil
import tempfile
from pathlib import Path
from typing import Iterable

def is_gcs_path(path: str | os.PathLike[str]) -> bool:
    return str(path).startswith("gs://")


def split_gcs_path(uri: str) -> tuple[str, str]:
    stripped = uri.removeprefix("gs://")
    bucket, _, blob = stripped.partition("/")
    if not bucket:
        raise ValueError(f"Invalid GCS URI: {uri}")
    return bucket, blob


def ensure_local_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def upload_file(local_path: Path, destination_uri: str) -> None:
    from google.cloud import storage

    bucket_name, blob_name = split_gcs_path(destination_uri)
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    bucket.blob(blob_name).upload_from_filename(str(local_path))


def download_file(source_uri: str, local_path: Path) -> None:
    from google.cloud import storage

    bucket_name, blob_name = split_gcs_path(source_uri)
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    ensure_local_dir(local_path.parent)
    bucket.blob(blob_name).download_to_filename(str(local_path))


def upload_directory(local_dir: Path, destination_uri: str, file_names: Iterable[str]) -> None:
    destination_root = destination_uri.rstrip("/")
    for file_name in file_names:
        upload_file(local_dir / file_name, f"{destination_root}/{file_name}")


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def prepare_local_artifact_dir(source_uri: str | None) -> Path:
    temp_dir = Path(tempfile.mkdtemp(prefix="nimbuswatch-artifacts-"))
    if not source_uri:
        return temp_dir

    required_files = ("model.joblib", "feature_schema.json", "metrics.json", "training_summary.json")
    optional_files = ("demo_scenarios.json",)

    for file_name in required_files:
        download_file(f"{source_uri.rstrip('/')}/{file_name}", temp_dir / file_name)

    for file_name in optional_files:
        try:
            download_file(f"{source_uri.rstrip('/')}/{file_name}", temp_dir / file_name)
        except Exception:
            continue
    return temp_dir


def cleanup_dir(path: Path | None) -> None:
    if path and path.exists():
        shutil.rmtree(path, ignore_errors=True)
