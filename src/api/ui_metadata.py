from __future__ import annotations


def describe_feature(name: str) -> str:
    if "Flag Count" in name:
        flag = name.replace(" Flag Count", "")
        return f"How many {flag} TCP flags appeared in this flow."
    if "Bytes/s" in name:
        return "Average byte rate observed during the flow."
    if "Packets/s" in name:
        return "Average packet rate observed during the flow."
    if "Flow Duration" in name:
        return "Total lifetime of the connection or flow."
    if "IAT" in name:
        direction = "forward" if "Fwd" in name else "backward" if "Bwd" in name else "overall"
        metric = name.split()[-1].lower()
        return f"{metric.capitalize()} gap between {direction} packets in the flow."
    if "Idle" in name:
        metric = name.split()[-1].lower()
        return f"{metric.capitalize()} idle period between bursts of activity."
    if "Active" in name:
        metric = name.split()[-1].lower()
        return f"{metric.capitalize()} active period while the flow was transmitting."
    if "Packet Length" in name:
        metric = name.replace("Packet Length ", "").replace("Packet Length", "").strip().lower() or "value"
        return f"Packet-size {metric} measured within the flow."
    if "Average Packet Size" in name:
        return "Mean packet size across the full flow."
    if "Segment Size" in name:
        return "Average TCP segment size seen in this direction."
    if "Header Length" in name:
        return "Total header bytes observed in this direction."
    if "Total Length" in name or "Subflow" in name:
        return "Cumulative bytes transferred for this part of the flow."
    if "Init_Win_bytes" in name:
        return "Initial TCP receive window advertised at connection start."
    if "Min Packet Length" in name or "Max Packet Length" in name:
        return "Smallest or largest packet size seen in the flow."
    if "Down/Up Ratio" in name:
        return "Traffic ratio between download and upload directions."
    return "Numeric flow feature extracted before prediction."


def group_feature(name: str) -> str:
    if "Flag Count" in name:
        return "TCP Flags"
    if "IAT" in name or "Idle" in name or "Active" in name or "Duration" in name:
        return "Timing"
    if "Bytes/s" in name or "Packets/s" in name or "Subflow" in name or "Total Length" in name:
        return "Rates and Volume"
    if "Packet" in name or "Segment Size" in name or "Header Length" in name or "Win_bytes" in name:
        return "Packet Sizes"
    return "Other"


def build_field_groups(feature_names: list[str]) -> list[dict[str, object]]:
    groups: dict[str, list[dict[str, str]]] = {}
    for name in feature_names:
        group = group_feature(name)
        groups.setdefault(group, []).append({"name": name, "description": describe_feature(name)})
    return [{"name": group, "fields": fields} for group, fields in groups.items()]
