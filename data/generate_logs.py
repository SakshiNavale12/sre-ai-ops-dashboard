"""
generate_logs.py
Generates synthetic system monitoring logs (CPU, Memory, Disk, Errors)
simulating a real-world server environment for SRE analysis.
"""

import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta

RANDOM_SEED = 42
np.random.seed(RANDOM_SEED)

NUM_RECORDS = 500
START_TIME = datetime(2024, 1, 1, 0, 0, 0)
ANOMALY_INDICES = [50, 120, 200, 310, 420]  # rows that will be injected as anomalies

OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "..", "logs", "system_logs.csv")


def generate_timestamps(n: int) -> list:
    return [START_TIME + timedelta(minutes=5 * i) for i in range(n)]


def inject_anomalies(series: np.ndarray, indices: list, spike_value: float) -> np.ndarray:
    result = series.copy()
    for idx in indices:
        result[idx] = spike_value
    return result


def build_dataframe() -> pd.DataFrame:
    timestamps = generate_timestamps(NUM_RECORDS)

    cpu_usage = np.random.normal(loc=45, scale=10, size=NUM_RECORDS).clip(5, 95)
    cpu_usage = inject_anomalies(cpu_usage, ANOMALY_INDICES, spike_value=98.5)

    memory_usage = np.random.normal(loc=60, scale=8, size=NUM_RECORDS).clip(20, 95)
    memory_usage = inject_anomalies(memory_usage, [120, 200, 420], spike_value=97.2)

    disk_usage = np.random.normal(loc=55, scale=5, size=NUM_RECORDS).clip(30, 90)
    disk_usage = inject_anomalies(disk_usage, [310], spike_value=96.0)

    # Network latency in ms
    network_latency = np.random.normal(loc=20, scale=5, size=NUM_RECORDS).clip(5, 100)
    network_latency = inject_anomalies(network_latency, [50, 310], spike_value=350.0)

    # Error counts per 5-minute window
    error_count = np.random.poisson(lam=1, size=NUM_RECORDS)
    for idx in ANOMALY_INDICES:
        error_count[idx] = np.random.randint(15, 30)

    # Response time in ms
    response_time = np.random.normal(loc=150, scale=30, size=NUM_RECORDS).clip(50, 400)
    response_time = inject_anomalies(response_time, [50, 200, 420], spike_value=2500.0)

    df = pd.DataFrame({
        "timestamp": timestamps,
        "cpu_usage_pct": np.round(cpu_usage, 2),
        "memory_usage_pct": np.round(memory_usage, 2),
        "disk_usage_pct": np.round(disk_usage, 2),
        "network_latency_ms": np.round(network_latency, 2),
        "error_count": error_count,
        "response_time_ms": np.round(response_time, 2),
    })

    return df


def main():
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    df = build_dataframe()
    df.to_csv(OUTPUT_PATH, index=False)
    print(f"[OK] Generated {len(df)} log records -> {os.path.abspath(OUTPUT_PATH)}")
    print(df.describe().round(2))


if __name__ == "__main__":
    main()
