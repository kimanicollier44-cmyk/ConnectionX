#!/usr/bin/env python3
"""ConnectionX self-checks: python checks.py prints CHECKS n/n."""
import sys

sys.path.insert(0, ".")
from connectionx.cli import demo
from connectionx.council import DECIDER, apply_advice, council_status, decide
from connectionx.google_cloud import cloud_status
from connectionx.google_drive import DriveRegistry
from connectionx.google_flow import merged_plan
from connectionx.honeypotx import honeypotx_summary
from connectionx.payloads import run_chamber
from connectionx.data import ESSENTIAL_APPS, FREE_ESSENTIAL_MB
from connectionx.esim import make_profile, upgrade_from_sim
from connectionx.gates import HOLD_GATES, check_gate
from connectionx.numbers import format_number, is_synthetic
from connectionx.routing import choose_route
from connectionx.upgrade import RADIO_PROFILES, upgrade_report

results = []


def check(name, ok):
    results.append((name, bool(ok)))
    print(("PASS" if ok else "FAIL"), name)


d = demo()
check("demo subscriber gets a synthetic free number", is_synthetic(d["subscriber"]["number"]))
check("demo eSIM enabled", d["subscriber"]["esim_state"] == "enabled")
check("demo call on VoWiFi with EVS", d["call"]["bearer"] == "VoWiFi" and "EVS" in d["call"]["codec"])
check("demo text uses RCS", d["text"]["protocol"] == "RCS")
check("demo bill total is $0", d["report"]["bill"]["total_usd"] == 0.0)
check("format_number", format_number("4155550100") == "(415) 555-0100")
check("wifi-first call route", choose_route("call", wifi_available=True).bearer == "VoWiFi")
check("cell call route is Vo5G", choose_route("call", wifi_available=False).bearer == "Vo5G")
check("lte call route is VoLTE", choose_route("call", wifi_available=False, cell_gen="lte").bearer == "VoLTE")
check("text falls back to SMS", choose_route("text", rcs_available=False).bearer == "SMS")
check("no-network route", choose_route("data", wifi_available=False, cell_available=False).bearer == "none")
check("essential apps include maps", "maps" in ESSENTIAL_APPS and FREE_ESSENTIAL_MB == 1024)
p = make_profile("test")
check("eSIM activation code is synthetic (.invalid)", ".invalid" in p.activation_code)
check("eSIM enables", p.enable() == "enabled")
check("SIM upgrade plan is $0", upgrade_from_sim("SIM-1")["cost_usd"] == 0.0)
check("18 HOLD gates", len(HOLD_GATES) == 18)
check("live carrier activation HOLDs", check_gate("live_carrier_activation", live=True) == "HOLD")
check("simulated activation allowed", check_gate("live_carrier_activation", live=False) == "ALLOW-SIM")
check("emergency routing HOLDs live", check_gate("emergency_call_routing", live=True) == "HOLD")
check("council allows normal use", decide().verdict == "ALLOW")
check("council HOLDs live carrier", decide(wants_live_carrier=True).verdict == "HOLD")
check("advisor tighten-only", apply_advice(decide(), advisor_wants_hold=True).verdict == "HOLD")
check("advisor cannot loosen a HOLD", apply_advice(decide(wants_live_carrier=True), advisor_wants_hold=False).verdict == "HOLD")
check("council makes no live calls", council_status()["live_calls"] == 0)
check("decider is Gemini Argon 4 Extended Thinking", DECIDER["name"] == "Gemini Argon 4 Extended Thinking")
check("argon 4 tiers", DECIDER["thinking_tiers"] == (2048, 8192, 32768))
flow = merged_plan()
check("all 4 Google flows used", flow["all_flows_used"] and len(flow["flow_names"]) == 4)
check("google flow plan-only", flow["total_live_calls"] == 0 and not flow["anything_rendered"])
ch = run_chamber()
check("sandbox chamber 7 payloads 4 allowed 3 held", (ch["total"], ch["allowed"], ch["held"]) == (7, 4, 3))
check("chamber never executes, no network", ch["all_executed"] is False and ch["total_network_attempts"] == 0)
hp = honeypotx_summary()
check("honeypotx 12 synthetic attempts, top threat 100", hp["attempts"] == 12 and hp["top_threat_score"] == 100)
check("honeypotx no listener, no access", hp["listener_open"] is False and hp["access_granted"] is False)
check("live detonation HOLDs", check_gate("live_sample_detonation", live=True) == "HOLD")
check("live honeypot listener HOLDs", check_gate("live_honeypot_listener", live=True) == "HOLD")
check("live video generation HOLDs", check_gate("live_video_generation", live=True) == "HOLD")
check("live gemini call HOLDs", check_gate("live_gemini_api_call", live=True) == "HOLD")
cs = cloud_status()
check("google cloud plan-only, 0 live connections", cs["deployed"] is False and cs["live_connections"] == 0)
check("google cloud plan has 5 services", cs["planned_services"] == 5)
reg = DriveRegistry()
reg.register("ledger.csv", b"a,b,c")
conflict = reg.register("ledger.csv", b"different")
check("drive one-name-one-hash conflict HOLDs", conflict["status"] == "HOLD-CONFLICT")
check("drive summary: nothing uploaded, 0 live", reg.summary()["uploaded"] == 0 and reg.summary()["live_connections"] == 0)
check("live cloud sync HOLDs", check_gate("live_cloud_sync", live=True) == "HOLD")
check("google drive access HOLDs live", check_gate("google_drive_access", live=True) == "HOLD")
rep = upgrade_report()
check("everything upgraded or modelled", rep["everything_upgraded_or_modelled"])
check("radio profiles labelled not measured", all(not v["measured"] for v in RADIO_PROFILES.values()))

passed = sum(1 for _, ok in results if ok)
print(f"CHECKS {passed}/{len(results)} ALL PASSED" if passed == len(results) else f"CHECKS {passed}/{len(results)} FAILED")
sys.exit(0 if passed == len(results) else 1)
