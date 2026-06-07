from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.models.artifact_store import load_json
from src.models.demo_scenarios import build_demo_scenarios, write_demo_scenarios
from src.models.preprocessing import load_dataset


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate guided demo scenarios aligned to a trained feature schema.")
    parser.add_argument("--csv-path", required=True, help="Path to the curated dataset CSV.")
    parser.add_argument("--schema-path", required=True, help="Path to feature_schema.json.")
    parser.add_argument("--output-path", required=True, help="Destination for demo_scenarios.json.")
    parser.add_argument("--target-column", default="Label")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    dataset = load_dataset([args.csv_path], target_column=args.target_column)
    schema = load_json(Path(args.schema_path))
    feature_names = list(schema["feature_names"])
    scenarios = build_demo_scenarios(dataset[feature_names], dataset[args.target_column], feature_names)
    write_demo_scenarios(args.output_path, scenarios)


if __name__ == "__main__":
    main()
