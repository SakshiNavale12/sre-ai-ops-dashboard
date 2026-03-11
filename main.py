"""
main.py
Entry point for the AI-Assisted IT Operations Dashboard.
Orchestrates: log generation -> anomaly detection -> AI summarization -> dashboard.
"""

import sys
import os
import time
import argparse


def banner():
    print("""
╔══════════════════════════════════════════════════════════╗
║      AI-Assisted IT Operations Dashboard                 ║
║      SRE Anomaly Detection & Incident Summarizer         ║
║      Author: SakshiNavale12                              ║
╚══════════════════════════════════════════════════════════╝
    """)


def step(n: int, title: str):
    print(f"\n{'─'*60}")
    print(f"  STEP {n}: {title}")
    print(f"{'─'*60}")


def run_generate_logs():
    step(1, "Generating Synthetic System Logs")
    from data.generate_logs import main as generate
    generate()


def run_anomaly_detection():
    step(2, "Running Isolation Forest Anomaly Detection")
    from scripts.detect_anomaly import main as detect
    return detect()


def run_ai_summary():
    step(3, "Generating AI Incident Summary (Google Gemini)")
    try:
        from scripts.ai_summary import main as summarize
        summarize()
    except ValueError as e:
        print(f"[WARN] Skipping AI summary: {e}")
        print("[INFO] Set GEMINI_API_KEY in .env to enable AI summaries.")
    except Exception as e:
        print(f"[WARN] AI summary failed: {e}")
        print("[INFO] Check your GEMINI_API_KEY and internet connection.")


def run_dashboard():
    step(4, "Rendering Matplotlib Dashboard")
    from scripts.dashboard import main as dashboard
    dashboard()


def parse_args():
    parser = argparse.ArgumentParser(
        description="AI-Assisted IT Operations Dashboard",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                  # Run all steps
  python main.py --skip-ai        # Skip Gemini AI step (no API key needed)
  python main.py --only-dashboard # Only regenerate the dashboard
        """,
    )
    parser.add_argument(
        "--skip-ai",
        action="store_true",
        help="Skip the Gemini AI summarization step",
    )
    parser.add_argument(
        "--only-dashboard",
        action="store_true",
        help="Only regenerate the dashboard (logs must already exist)",
    )
    return parser.parse_args()


def main():
    banner()
    args = parse_args()
    start = time.time()

    try:
        if args.only_dashboard:
            run_dashboard()
        else:
            run_generate_logs()
            run_anomaly_detection()
            if not args.skip_ai:
                run_ai_summary()
            else:
                print("\n[INFO] Skipping AI summary (--skip-ai flag used)")
            run_dashboard()

        elapsed = time.time() - start
        print(f"\n{'═'*60}")
        print(f"  Pipeline complete in {elapsed:.1f}s")
        print(f"  Reports saved in: reports/")
        print(f"  Logs saved in:    logs/")
        print(f"{'═'*60}\n")

    except FileNotFoundError as e:
        print(f"\n[ERROR] {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n[INFO] Interrupted by user.")
        sys.exit(0)


if __name__ == "__main__":
    main()
