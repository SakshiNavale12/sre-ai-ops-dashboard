"""
detect_anomaly.py
Uses Isolation Forest (scikit-learn) to detect anomalies in system logs.
Saves a detailed anomaly report to the reports/ folder.
"""

import pandas as pd
import numpy as np
import os
import json
from datetime import datetime
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

LOG_PATH = os.path.join(os.path.dirname(__file__), "..", "logs", "system_logs.csv")
REPORT_PATH = os.path.join(os.path.dirname(__file__), "..", "reports", "anomaly_report.json")

# Features used for anomaly detection
FEATURES = [
    "cpu_usage_pct",
    "memory_usage_pct",
    "disk_usage_pct",
    "network_latency_ms",
    "error_count",
    "response_time_ms",
]

CONTAMINATION = 0.04   # Expected proportion of anomalies (~4%)
RANDOM_STATE = 42


def load_logs(path: str) -> pd.DataFrame:
    if not os.path.exists(path):
        raise FileNotFoundError(f"Log file not found: {path}\nRun data/generate_logs.py first.")
    df = pd.read_csv(path, parse_dates=["timestamp"])
    print(f"[OK] Loaded {len(df)} records from {path}")
    return df


def run_isolation_forest(df: pd.DataFrame) -> pd.DataFrame:
    X = df[FEATURES].copy()
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    model = IsolationForest(
        n_estimators=200,
        contamination=CONTAMINATION,
        random_state=RANDOM_STATE,
        max_features=len(FEATURES),
    )
    predictions = model.fit_predict(X_scaled)   # -1 = anomaly, 1 = normal
    scores = model.score_samples(X_scaled)       # lower = more anomalous

    df = df.copy()
    df["anomaly_flag"] = (predictions == -1).astype(int)
    df["anomaly_score"] = np.round(scores, 4)
    return df


def build_report(df: pd.DataFrame) -> dict:
    anomalies = df[df["anomaly_flag"] == 1].copy()
    anomalies_sorted = anomalies.sort_values("anomaly_score")

    records = []
    for _, row in anomalies_sorted.iterrows():
        reasons = []
        if row["cpu_usage_pct"] > 90:
            reasons.append(f"CPU spike: {row['cpu_usage_pct']}%")
        if row["memory_usage_pct"] > 90:
            reasons.append(f"Memory spike: {row['memory_usage_pct']}%")
        if row["disk_usage_pct"] > 90:
            reasons.append(f"Disk spike: {row['disk_usage_pct']}%")
        if row["network_latency_ms"] > 200:
            reasons.append(f"High latency: {row['network_latency_ms']} ms")
        if row["error_count"] > 10:
            reasons.append(f"Error burst: {row['error_count']} errors")
        if row["response_time_ms"] > 1000:
            reasons.append(f"Slow response: {row['response_time_ms']} ms")
        if not reasons:
            reasons.append("Multi-metric deviation detected")

        records.append({
            "timestamp": str(row["timestamp"]),
            "cpu_usage_pct": row["cpu_usage_pct"],
            "memory_usage_pct": row["memory_usage_pct"],
            "disk_usage_pct": row["disk_usage_pct"],
            "network_latency_ms": row["network_latency_ms"],
            "error_count": int(row["error_count"]),
            "response_time_ms": row["response_time_ms"],
            "anomaly_score": row["anomaly_score"],
            "reasons": reasons,
        })

    report = {
        "generated_at": datetime.now().isoformat(),
        "total_records": len(df),
        "total_anomalies": len(anomalies),
        "anomaly_rate_pct": round(len(anomalies) / len(df) * 100, 2),
        "anomalies": records,
    }
    return report


def save_report(report: dict, path: str):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(report, f, indent=2)
    print(f"[OK] Anomaly report saved -> {os.path.abspath(path)}")


def main() -> dict:
    df = load_logs(LOG_PATH)
    df_result = run_isolation_forest(df)

    total = len(df_result)
    flagged = df_result["anomaly_flag"].sum()
    print(f"[INFO] Anomalies detected: {flagged} / {total} ({flagged/total*100:.1f}%)")

    report = build_report(df_result)
    save_report(report, REPORT_PATH)

    # Also save the enriched CSV
    enriched_path = os.path.join(os.path.dirname(__file__), "..", "logs", "system_logs_annotated.csv")
    df_result.to_csv(enriched_path, index=False)
    print(f"[OK] Annotated logs saved -> {os.path.abspath(enriched_path)}")

    return report


if __name__ == "__main__":
    main()
