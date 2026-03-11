"""
ai_summary.py
Uses Google Gemini API (free tier) to auto-summarize detected anomalies
and suggest actionable SRE remediation steps.
"""

import os
import json
import textwrap
from datetime import datetime

import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

REPORT_PATH = os.path.join(os.path.dirname(__file__), "..", "reports", "anomaly_report.json")
SUMMARY_PATH = os.path.join(os.path.dirname(__file__), "..", "reports", "ai_incident_summary.txt")

GEMINI_MODEL = "gemini-1.5-flash"   # Free tier model


def load_report(path: str) -> dict:
    if not os.path.exists(path):
        raise FileNotFoundError(f"Anomaly report not found: {path}\nRun scripts/detect_anomaly.py first.")
    with open(path) as f:
        return json.load(f)


def build_prompt(report: dict) -> str:
    top_anomalies = report["anomalies"][:5]  # Top 5 worst anomalies

    anomaly_lines = []
    for i, a in enumerate(top_anomalies, 1):
        reasons_str = "; ".join(a["reasons"])
        anomaly_lines.append(
            f"  {i}. [{a['timestamp']}] "
            f"CPU={a['cpu_usage_pct']}% MEM={a['memory_usage_pct']}% "
            f"DISK={a['disk_usage_pct']}% LATENCY={a['network_latency_ms']}ms "
            f"ERRORS={a['error_count']} RESP={a['response_time_ms']}ms | "
            f"Reasons: {reasons_str}"
        )

    anomaly_block = "\n".join(anomaly_lines)

    prompt = textwrap.dedent(f"""
        You are an expert Site Reliability Engineer (SRE) AI assistant.
        Analyze the following system anomaly report and provide:

        1. **Executive Summary** (2-3 sentences): What happened overall?
        2. **Root Cause Analysis**: Most likely causes for the top anomalies.
        3. **Impact Assessment**: What services/users could be affected?
        4. **Immediate Remediation Steps** (numbered list): What should the on-call engineer do right now?
        5. **Long-term Recommendations** (numbered list): How to prevent recurrence?
        6. **Severity Rating**: Rate the overall incident (P1/P2/P3/P4) with justification.

        --- ANOMALY REPORT ---
        Total Records Analyzed: {report['total_records']}
        Total Anomalies Found: {report['total_anomalies']} ({report['anomaly_rate_pct']}% anomaly rate)
        Report Generated: {report['generated_at']}

        Top {len(top_anomalies)} Most Severe Anomalies:
{anomaly_block}
        --- END REPORT ---

        Provide a clear, actionable incident report suitable for an SRE runbook.
    """).strip()

    return prompt


def call_gemini(prompt: str) -> str:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY not found.\n"
            "Please create a .env file with: GEMINI_API_KEY=your_key_here\n"
            "Get a free key at: https://aistudio.google.com/app/apikey"
        )

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(GEMINI_MODEL)

    print(f"[INFO] Calling Gemini ({GEMINI_MODEL})...")
    response = model.generate_content(prompt)
    return response.text


def save_summary(summary: str, path: str, report: dict):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    header = (
        "=" * 70 + "\n"
        "   AI-GENERATED INCIDENT SUMMARY\n"
        f"   Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"   Anomalies: {report['total_anomalies']} / {report['total_records']} records\n"
        "=" * 70 + "\n\n"
    )
    with open(path, "w", encoding="utf-8") as f:
        f.write(header + summary)
    print(f"[OK] AI incident summary saved -> {os.path.abspath(path)}")


def main() -> str:
    report = load_report(REPORT_PATH)

    if report["total_anomalies"] == 0:
        print("[INFO] No anomalies found. No AI summary needed.")
        return "No anomalies detected."

    prompt = build_prompt(report)
    summary = call_gemini(prompt)

    print("\n" + "=" * 60)
    print("AI INCIDENT SUMMARY (preview)")
    print("=" * 60)
    print(summary[:800] + "..." if len(summary) > 800 else summary)
    print("=" * 60 + "\n")

    save_summary(summary, SUMMARY_PATH, report)
    return summary


if __name__ == "__main__":
    main()
