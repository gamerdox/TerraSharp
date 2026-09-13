"""
Command-Line Interface (CLI) for running the SH-304 Pipeline Standalone.
Usage:
  python scripts/run_pipeline_cli.py --aoi wayanad --mode demo
"""
import argparse
import json
from pathlib import Path
import sys

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from backend.app.pipeline import PipelineOrchestrator, pipeline_state
from backend.app.config import settings


def main():
    parser = argparse.ArgumentParser(description="SH-304 Early Warning System Pipeline CLI")
    parser.add_argument("--aoi", type=str, default="wayanad", choices=["wayanad", "chamoli"], help="Area of Interest")
    parser.add_argument("--mode", type=str, default="demo", choices=["demo", "live"], help="Execution mode")
    parser.add_argument("--export-json", action="store_true", help="Export summary results to JSON")

    args = parser.parse_args()

    print("=" * 65)
    print("SH-304: Hyper-Local Landslide & Flash-Flood Early Warning System")
    print(f"Target AOI: {args.aoi.upper()} | Mode: {args.mode.upper()}")
    print("=" * 65)

    orchestrator = PipelineOrchestrator(mode=args.mode)
    res = orchestrator.run(args.aoi)

    print("\n Pipeline Execution Succeeded:")
    print(f"  - AOI: {res['aoi']}")
    print(f"  - Processed At: {res['processed_at']}")
    print(f"  - Grid Dimensions: {res['grid_info']['rows']} rows x {res['grid_info']['cols']} cols (~{res['grid_info']['resolution_deg']} deg)")
    print(f"  - Settlements Analyzed: {res['villages_analyzed']}")
    print(f"  - Critical Alerts: {res['critical_alerts_count']}")
    print(f"  - Warning Alerts: {res['warning_alerts_count']}")
    print(f"  - Lead-Time Status: {res['lead_time_status']} (~{res['estimated_lead_time_hours']} hrs)")
    print(f"  - Back-Test Full Weighted Model ROC-AUC: {res['backtest_full_auc']:.3f}")
    print(f"  - Back-Test Rain-Only Baseline ROC-AUC: {res['backtest_rain_auc']:.3f}")

    print("\n Top Settlement Alerts:")
    for a in pipeline_state.alerts[:5]:
        print(f"  [{a.alert_state.value}] {a.location_name}: Risk={a.risk_score:.2f} ({a.hazard_type.value}) - Dominant: {a.contributing_factors.dominant_factor}")

    if args.export_json:
        out_file = BASE_DIR / "data" / "processed" / f"{args.aoi}_cli_output.json"
        out_file.parent.mkdir(parents=True, exist_ok=True)
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(res, f, indent=2)
        print(f"\n Exported summary to {out_file}")

    print("=" * 65)


if __name__ == "__main__":
    main()
