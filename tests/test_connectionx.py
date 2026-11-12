import pytest

from connectionx.council import apply_advice, decide
from connectionx.data import DataLedger
from connectionx.esim import make_profile, upgrade_from_sim
from connectionx.gates import check_gate
from connectionx.messaging import MessageLog
from connectionx.numbers import NumberPool, format_number, is_synthetic, normalize_number
from connectionx.routing import choose_route
from connectionx.service import ConnectionXService
from connectionx.upgrade import upgrade_report
from connectionx.voice import CallLog


def test_format_and_synthetic():
    assert format_number("14155550100") == "(415) 555-0100"
    assert is_synthetic("(415) 555-0100")
    assert not is_synthetic("(415) 867-5309")


def test_normalize_rejects_short():
    with pytest.raises(ValueError):
        normalize_number("555-0100")


def test_pool_allocates_unique_synthetic():
    pool = NumberPool()
    a, b = pool.allocate(), pool.allocate()
    assert a != b and is_synthetic(a) and is_synthetic(b)
    assert pool.allocated_count() == 2


def test_wifi_first_call():
    r = choose_route("call", wifi_available=True)
    assert (r.bearer, r.cost_usd) == ("VoWiFi", 0.0)


def test_cell_call_bearers():
    assert choose_route("call", wifi_available=False, cell_gen="5g").bearer == "Vo5G"
    assert choose_route("call", wifi_available=False, cell_gen="lte").bearer == "VoLTE"


def test_text_rcs_and_sms_fallback():
    assert choose_route("text", rcs_available=True).bearer == "RCS"
    assert choose_route("text", rcs_available=False).bearer == "SMS"


def test_call_log_codec_and_zero_cost():
    log = CallLog()
    call = log.place("a", "b", 60, choose_route("call", wifi_available=False))
    assert call.codec == "EVS Fullband"
    assert log.total_cost() == 0.0 and log.total_seconds() == 60


def test_rcs_message_features():
    log = MessageLog()
    msg = log.send("a", "b", "hi", media=True, group=True)
    assert msg.protocol == "RCS" and "group-chat" in msg.features


def test_sms_segments_and_media_rejected():
    log = MessageLog()
    msg = log.send("a", "b", "x" * 200, rcs_available=False)
    assert msg.protocol == "SMS" and msg.segments == 2
    with pytest.raises(ValueError):
        log.send("a", "b", "", media=True, rcs_available=False)


def test_esim_lifecycle():
    p = make_profile("user-1")
    assert ".invalid" in p.activation_code
    assert p.enable() == "enabled"
    plan = upgrade_from_sim("SIM-9")
    assert plan["cost_usd"] == 0.0 and plan["new"] == "eSIM"


def test_data_ledger_free_paths():
    led = DataLedger()
    assert led.use("maps", 100, on_wifi=False).status == "free-essential"
    assert led.use("video", 500, on_wifi=True).status == "free-wifi"
    assert led.use("video", 10, on_wifi=False).status == "needs-data-pass"
    assert led.essential_remaining_mb() == 924
    assert led.wifi_offload_percent() > 80


def test_data_ledger_essential_cap():
    led = DataLedger()
    led.use("email", 1000, on_wifi=False)
    assert led.use("email", 100, on_wifi=False).status == "needs-data-pass"


def test_gates():
    assert check_gate("live_carrier_activation", live=True) == "HOLD"
    assert check_gate("live_carrier_activation", live=False) == "ALLOW-SIM"
    with pytest.raises(ValueError):
        check_gate("not_a_gate", live=True)


def test_council_tighten_only():
    assert decide().verdict == "ALLOW"
    assert decide(wants_emergency_routing=True).verdict == "HOLD"
    assert apply_advice(decide(), True).verdict == "HOLD"
    assert apply_advice(decide(wants_live_carrier=True), False).verdict == "HOLD"


def test_service_end_to_end_zero_bill():
    svc = ConnectionXService()
    sub = svc.activate("Test User")
    assert is_synthetic(sub.number) and sub.esim.state == "enabled"
    svc.call(sub, "(415) 555-0142", 30)
    svc.text(sub, "(415) 555-0142", "hello")
    svc.use_data("maps", 50, on_wifi=False)
    report = svc.report()
    assert report["bill"]["total_usd"] == 0.0
    assert report["subscribers"] == 1


def test_upgrade_report():
    rep = upgrade_report()
    assert rep["everything_upgraded_or_modelled"]
    assert rep["modelled_not_measured"] is True


def test_argon4_decider_seat():
    from connectionx.council import DECIDER, council_status
    assert DECIDER["name"] == "Gemini Argon 4 Extended Thinking"
    assert DECIDER["also_known_as"] == "Gemini Carbon 4 Extended Thinking"
    assert DECIDER["thinking_tiers"] == (2048, 8192, 32768)
    assert council_status()["live_calls"] == 0


def test_google_flow_all_four_plan_only():
    from connectionx.google_flow import merged_plan
    plan = merged_plan()
    assert plan["all_flows_used"] is True
    assert plan["flow_names"] == ["FlowX", "Workspace Studio",
                                   "Flow Filmmaking", "DataX google_flow"]
    assert plan["total_live_calls"] == 0
    assert plan["anything_rendered"] is False


def test_chamber_triage_never_executes():
    from connectionx.payloads import run_chamber
    result = run_chamber()
    assert (result["total"], result["allowed"], result["held"]) == (7, 4, 3)
    assert result["all_executed"] is False
    assert result["total_network_attempts"] == 0


def test_honeypotx_log_analysis_only():
    from connectionx.honeypotx import honeypotx_summary
    summary = honeypotx_summary()
    assert summary["attempts"] == 12
    assert summary["listener_open"] is False
    assert summary["access_granted"] is False
    assert summary["top_threat_score"] == 100
    assert summary["by_class"] == {"scanner": 4, "env_harvest": 3,
                                    "lfi_probe": 2, "sqli_probe": 2,
                                    "upload_attempt": 1}


def test_new_hold_gates():
    for gate in ("live_sample_detonation", "live_honeypot_listener",
                 "live_video_generation", "live_gemini_api_call"):
        assert check_gate(gate, live=True) == "HOLD"
        assert check_gate(gate, live=False) == "ALLOW-SIM"


def test_google_cloud_plan_only():
    from connectionx.google_cloud import cloud_status
    status = cloud_status()
    assert status["deployed"] is False
    assert status["live_connections"] == 0
    assert status["planned_services"] == 5


def test_google_drive_registry_one_name_one_hash():
    from connectionx.google_drive import DriveRegistry, folder_for
    assert folder_for("main.py") == "code"
    assert folder_for("bill.csv") == "exports"
    reg = DriveRegistry()
    first = reg.register("report.md", b"v1")
    assert first["status"] == "registered-local" and first["uploaded"] is False
    same = reg.register("report.md", b"v1")
    assert same["sha256"] == first["sha256"]
    conflict = reg.register("report.md", b"v2-different")
    assert conflict["status"] == "HOLD-CONFLICT"
    summary = reg.summary()
    assert summary["registered"] == 1 and summary["conflicts_held"] == 1
    assert summary["live_connections"] == 0


def test_cloud_drive_gates():
    for gate in ("live_cloud_sync", "google_drive_access"):
        assert check_gate(gate, live=True) == "HOLD"
        assert check_gate(gate, live=False) == "ALLOW-SIM"


def test_service_report_includes_new_seats():
    svc = ConnectionXService()
    svc.activate("Seat User")
    report = svc.report()
    assert report["chamber"]["held"] == 3
    assert report["honeypotx"]["attempts"] == 12
    assert report["google_flow"]["all_flows_used"] is True
    assert report["google_cloud"]["live_connections"] == 0
    assert report["google_drive"]["uploaded"] == 0
