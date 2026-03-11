"""
dashboard.py
Generates a multi-panel matplotlib dashboard visualizing system health metrics
and highlighting detected anomalies.
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.patches as mpatches
import numpy as np

ANNOTATED_LOG_PATH = os.path.join(
    os.path.dirname(__file__), "..", "logs", "system_logs_annotated.csv"
)
DASHBOARD_OUTPUT = os.path.join(
    os.path.dirname(__file__), "..", "reports", "dashboard.png"
)

NORMAL_COLOR = "#4C72B0"
ANOMALY_COLOR = "#DD4444"
THRESHOLD_COLOR = "#FFA500"

STYLE = "seaborn-v0_8-darkgrid"


def load_data(path: str) -> pd.DataFrame:
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Annotated logs not found: {path}\n"
            "Run scripts/detect_anomaly.py first."
        )
    df = pd.read_csv(path, parse_dates=["timestamp"])
    print(f"[OK] Loaded {len(df)} records for dashboard")
    return df


def plot_metric(
    ax,
    df: pd.DataFrame,
    column: str,
    title: str,
    ylabel: str,
    threshold: float = None,
):
    normal = df[df["anomaly_flag"] == 0]
    anomalous = df[df["anomaly_flag"] == 1]

    ax.plot(
        normal["timestamp"], normal[column],
        color=NORMAL_COLOR, linewidth=1.2, alpha=0.8, label="Normal"
    )
    ax.scatter(
        anomalous["timestamp"], anomalous[column],
        color=ANOMALY_COLOR, s=60, zorder=5, label="Anomaly", marker="x", linewidths=2
    )

    if threshold is not None:
        ax.axhline(y=threshold, color=THRESHOLD_COLOR, linestyle="--",
                   linewidth=1, alpha=0.8, label=f"Threshold ({threshold})")

    ax.set_title(title, fontsize=11, fontweight="bold", pad=8)
    ax.set_ylabel(ylabel, fontsize=9)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%m/%d\n%H:%M"))
    ax.xaxis.set_major_locator(mdates.AutoDateLocator(maxticks=6))
    ax.tick_params(axis="both", labelsize=8)
    ax.legend(fontsize=8, loc="upper right")


def plot_error_bars(ax, df: pd.DataFrame):
    normal = df[df["anomaly_flag"] == 0]
    anomalous = df[df["anomaly_flag"] == 1]

    ax.bar(normal["timestamp"], normal["error_count"],
           color=NORMAL_COLOR, alpha=0.6, width=0.003, label="Normal")
    ax.bar(anomalous["timestamp"], anomalous["error_count"],
           color=ANOMALY_COLOR, alpha=0.9, width=0.003, label="Anomaly")

    ax.set_title("Error Count per 5-min Window", fontsize=11, fontweight="bold", pad=8)
    ax.set_ylabel("Error Count", fontsize=9)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%m/%d\n%H:%M"))
    ax.xaxis.set_major_locator(mdates.AutoDateLocator(maxticks=6))
    ax.tick_params(axis="both", labelsize=8)
    ax.legend(fontsize=8)


def plot_anomaly_score(ax, df: pd.DataFrame):
    ax.fill_between(df["timestamp"], df["anomaly_score"],
                    color=NORMAL_COLOR, alpha=0.4, label="Anomaly Score")
    ax.scatter(
        df[df["anomaly_flag"] == 1]["timestamp"],
        df[df["anomaly_flag"] == 1]["anomaly_score"],
        color=ANOMALY_COLOR, s=60, zorder=5, marker="x", linewidths=2, label="Anomaly"
    )
    ax.set_title("Isolation Forest Anomaly Score (lower = more anomalous)",
                 fontsize=11, fontweight="bold", pad=8)
    ax.set_ylabel("Score", fontsize=9)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%m/%d\n%H:%M"))
    ax.xaxis.set_major_locator(mdates.AutoDateLocator(maxticks=6))
    ax.tick_params(axis="both", labelsize=8)
    ax.legend(fontsize=8)


def build_dashboard(df: pd.DataFrame):
    try:
        plt.style.use(STYLE)
    except OSError:
        plt.style.use("ggplot")

    fig, axes = plt.subplots(3, 2, figsize=(18, 14))
    fig.suptitle(
        "AI-Assisted IT Operations Dashboard\nSystem Health & Anomaly Detection",
        fontsize=16, fontweight="bold", y=0.98
    )

    plot_metric(axes[0, 0], df, "cpu_usage_pct",
                "CPU Usage (%)", "CPU %", threshold=90)
    plot_metric(axes[0, 1], df, "memory_usage_pct",
                "Memory Usage (%)", "Memory %", threshold=90)
    plot_metric(axes[1, 0], df, "disk_usage_pct",
                "Disk Usage (%)", "Disk %", threshold=85)
    plot_metric(axes[1, 1], df, "network_latency_ms",
                "Network Latency (ms)", "Latency (ms)", threshold=200)
    plot_error_bars(axes[2, 0], df)
    plot_anomaly_score(axes[2, 1], df)

    # Summary stats box
    total = len(df)
    anomaly_count = df["anomaly_flag"].sum()
    stats_text = (
        f"Total Records: {total}  |  "
        f"Anomalies: {anomaly_count} ({anomaly_count/total*100:.1f}%)  |  "
        f"Avg CPU: {df['cpu_usage_pct'].mean():.1f}%  |  "
        f"Avg Memory: {df['memory_usage_pct'].mean():.1f}%"
    )
    fig.text(0.5, 0.01, stats_text, ha="center", fontsize=10,
             bbox=dict(boxstyle="round,pad=0.4", facecolor="#f0f0f0", edgecolor="gray"))

    plt.tight_layout(rect=[0, 0.03, 1, 0.96])

    os.makedirs(os.path.dirname(DASHBOARD_OUTPUT), exist_ok=True)
    plt.savefig(DASHBOARD_OUTPUT, dpi=150, bbox_inches="tight")
    print(f"[OK] Dashboard saved -> {os.path.abspath(DASHBOARD_OUTPUT)}")
    plt.show()


def main():
    df = load_data(ANNOTATED_LOG_PATH)
    build_dashboard(df)


if __name__ == "__main__":
    main()
