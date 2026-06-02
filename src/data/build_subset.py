from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from src.config import DEFAULT_BENIGN_LABEL, DEFAULT_RANDOM_STATE, DEFAULT_TARGET_COLUMN


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a curated CICIDS2017 subset.")
    parser.add_argument("--csv-paths", required=True, help="Comma-separated source CSV paths.")
    parser.add_argument("--output-path", required=True, help="Output CSV path.")
    parser.add_argument("--target-column", default=DEFAULT_TARGET_COLUMN)
    parser.add_argument("--benign-per-file", type=int, default=50000)
    parser.add_argument("--random-state", type=int, default=DEFAULT_RANDOM_STATE)
    return parser.parse_args()


def build_subset(
    csv_paths: list[str],
    output_path: Path,
    target_column: str,
    benign_per_file: int,
    random_state: int,
) -> dict:
    frames = []
    summary = {"files": [], "total_rows": 0, "benign_rows": 0, "attack_rows": 0}

    for csv_path in csv_paths:
        frame = pd.read_csv(csv_path, low_memory=False, skipinitialspace=True)
        frame.columns = [str(column).strip() for column in frame.columns]
        labels = frame[target_column].astype(str).str.strip()

        benign = frame.loc[labels.str.upper() == DEFAULT_BENIGN_LABEL]
        attack = frame.loc[labels.str.upper() != DEFAULT_BENIGN_LABEL]

        if benign_per_file > 0 and len(benign) > benign_per_file:
            benign = benign.sample(n=benign_per_file, random_state=random_state)

        curated = pd.concat([benign, attack], ignore_index=True)
        frames.append(curated)

        summary["files"].append(
            {
                "source": csv_path,
                "rows_used": int(len(curated)),
                "benign_rows": int(len(benign)),
                "attack_rows": int(len(attack)),
            }
        )
        summary["total_rows"] += int(len(curated))
        summary["benign_rows"] += int(len(benign))
        summary["attack_rows"] += int(len(attack))

    merged = pd.concat(frames, ignore_index=True)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    merged.to_csv(output_path, index=False)
    return summary


def main() -> None:
    args = parse_args()
    csv_paths = [item.strip() for item in args.csv_paths.split(",") if item.strip()]
    summary = build_subset(
        csv_paths=csv_paths,
        output_path=Path(args.output_path),
        target_column=args.target_column,
        benign_per_file=args.benign_per_file,
        random_state=args.random_state,
    )
    print(summary)


if __name__ == "__main__":
    main()
