"""Command line for ConnectionX. Run: python main.py demo"""
from __future__ import annotations

import argparse
import json

from .council import council_status, decide
from .gates import gate_report
from .google_cloud import cloud_status
from .google_drive import DriveRegistry
from .google_flow import merged_plan
from .honeypotx import honeypotx_summary
from .payloads import run_chamber
from .service import ConnectionXService
from .upgrade import upgrade_report


def demo() -> dict:
    svc = ConnectionXService()
    sub = svc.activate("Demo User")
    call = svc.call(sub, "(415) 555-0142", 180, wifi_available=True)
    text = svc.text(sub, "(415) 555-0142", "Free call, free text.", media=True)
    svc.use_data("maps", 120, on_wifi=False)
    svc.use_data("video", 800, on_wifi=True)
    return {
        "subscriber": {"name": sub.name, "number": sub.number,
                       "esim_state": sub.esim.state,
                       "activation_code": sub.esim.activation_code},
        "call": {"bearer": call.bearer, "codec": call.codec, "cost_usd": call.cost_usd},
        "text": {"protocol": text.protocol, "features": list(text.features),
                 "cost_usd": text.cost_usd},
        "report": svc.report(),
        "council": decide(),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="connectionx")
    parser.add_argument("command", nargs="?", default="demo",
                        choices=["demo", "upgrade", "gates", "council",
                                 "flow", "chamber", "honeypot", "cloud", "drive"])
    args = parser.parse_args(argv)
    if args.command == "demo":
        out = demo()
    elif args.command == "upgrade":
        out = upgrade_report()
    elif args.command == "gates":
        out = gate_report()
    elif args.command == "flow":
        out = merged_plan()
    elif args.command == "chamber":
        out = run_chamber()
    elif args.command == "honeypot":
        out = honeypotx_summary()
    elif args.command == "cloud":
        out = cloud_status()
    elif args.command == "drive":
        out = DriveRegistry().summary()
    else:
        out = council_status()
    print(json.dumps(out, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
