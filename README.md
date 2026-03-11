# AI-Assisted IT Operations Dashboard

> An end-to-end SRE (Site Reliability Engineering) tool that generates system logs, detects anomalies using Machine Learning, auto-summarizes incidents using Google Gemini AI, and visualizes system health trends.

---

## Dashboard Preview

![Dashboard](reports/dashboard.png)

---

## What This Project Does

| Step | Component | Technology |
|------|-----------|------------|
| 1 | Generate synthetic system logs (CPU, Memory, Disk, Errors) | Python, Pandas, NumPy |
| 2 | Detect anomalies using unsupervised ML | scikit-learn Isolation Forest |
| 3 | Auto-summarize incidents & suggest fixes | Google Gemini 1.5 Flash (Free API) |
| 4 | Visualize trends with anomaly highlighting | Matplotlib |

---

## SRE Context

In real-world Site Reliability Engineering:
- Systems generate thousands of metrics every minute
- On-call engineers must triage incidents fast
- AI reduces **Mean Time to Detect (MTTD)** and **Mean Time to Resolve (MTTR)**

This project demonstrates a lightweight, AI-augmented observability pipeline — the kind of tooling that underpins production reliability at scale.

---

## Project Structure

```
sre-ai-ops-dashboard/
├── data/
│   └── generate_logs.py        # Generates synthetic CSV logs with injected anomalies
├── scripts/
│   ├── detect_anomaly.py       # Isolation Forest ML anomaly detection
│   ├── ai_summary.py           # Google Gemini AI incident summarizer
│   └── dashboard.py            # Matplotlib multi-panel dashboard
├── logs/
│   ├── system_logs.csv         # Raw generated logs
│   └── system_logs_annotated.csv  # Logs with anomaly labels
├── reports/
│   ├── anomaly_report.json     # Structured anomaly report
│   ├── ai_incident_summary.txt # AI-generated incident summary
│   └── dashboard.png           # Dashboard screenshot
├── main.py                     # Orchestrator — runs all steps
├── requirements.txt
├── .env.example                # Template for API key
└── README.md
```

---

## Quick Start

### 1. Clone the repository
```bash
git clone https://github.com/SakshiNavale12/sre-ai-ops-dashboard.git
cd sre-ai-ops-dashboard
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Set up Gemini API key (free)
1. Get a free key at [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Copy `.env.example` to `.env`
3. Paste your key:
```
GEMINI_API_KEY=your_key_here
```

### 4. Run the full pipeline
```bash
python main.py
```

### 5. Run without AI (no API key needed)
```bash
python main.py --skip-ai
```

---

## ML Approach: Isolation Forest

**Isolation Forest** is an unsupervised anomaly detection algorithm that:
- Builds random decision trees to "isolate" data points
- Anomalies are isolated faster (shorter tree paths) than normal points
- No labeled training data required — perfect for infrastructure monitoring
- Configured with `contamination=0.04` (expects ~4% anomaly rate)

**Features used:**
- `cpu_usage_pct` — CPU utilization %
- `memory_usage_pct` — RAM utilization %
- `disk_usage_pct` — Disk utilization %
- `network_latency_ms` — Network round-trip latency
- `error_count` — Application errors per 5-min window
- `response_time_ms` — Service response time

---

## AI Summarization

Google Gemini 1.5 Flash analyzes the top anomalies and returns:
- Executive Summary
- Root Cause Analysis
- Impact Assessment
- Immediate Remediation Steps
- Long-term Recommendations
- Severity Rating (P1–P4)

---

## Sample AI Output

```
SEVERITY: P2 - High

EXECUTIVE SUMMARY:
Multiple correlated spikes detected across CPU (98.5%), memory (97.2%),
and response time (2500ms) suggest a resource exhaustion event, likely
caused by a runaway process or sudden traffic surge.

IMMEDIATE REMEDIATION:
1. Check top processes: `top` / `htop` — identify memory hog
2. Restart offending service: `systemctl restart <service>`
3. Scale horizontally if load-based: trigger auto-scaling group
...
```

---

## Technologies Used

- **Python 3.10+**
- **Pandas / NumPy** — data manipulation
- **scikit-learn** — Isolation Forest ML model
- **Matplotlib** — dashboard visualization
- **Google Generative AI SDK** — Gemini 1.5 Flash
- **python-dotenv** — secure API key management

---

## Author

**Sakshi Navale** — [@SakshiNavale12](https://github.com/SakshiNavale12)

---

## License

MIT License — free to use and modify.
