"""HOLD gates: the lines a free phone service must never fake.

ConnectionX is a service-layer model. Anything that would touch a real
carrier, real spectrum, or a real person's safety stops at HOLD.
"""
from __future__ import annotations

HOLD_GATES = {
    "live_carrier_activation": "activating a real line on a real carrier",
    "real_spectrum_transmission": "transmitting on licensed spectrum without a carrier",
    "emergency_call_routing": "routing 911 / emergency calls (always use a real carrier line)",
    "real_number_port_in": "porting a real person's number without their verified consent",
    "sim_swap": "moving a number to a new SIM/eSIM without owner verification",
    "wiretap_interception": "listening to or recording another person's calls",
    "location_tracking_other": "tracking another person's phone or location",
    "spam_calling": "bulk or robocalling",
    "spam_texting": "bulk unsolicited texting",
    "caller_id_spoofing": "showing a number you do not own",
    "charging_money": "billing a subscriber (the core service is $0)",
    "selling_subscriber_data": "selling call, text, or location data",
    "live_sample_detonation": "executing a real sample outside the static chamber",
    "live_honeypot_listener": "opening a live honeypot listener",
    "live_video_generation": "rendering video live through Google Flow",
    "live_gemini_api_call": "calling the Gemini / Argon API live",
    "live_cloud_sync": "deploying or syncing to a live Google Cloud project",
    "google_drive_access": "reading or writing the owner's real Google Drive",
}


def check_gate(action: str, live: bool) -> str:
    """Return HOLD for a live attempt at a gated action, else ALLOW-SIM."""
    if action not in HOLD_GATES:
        raise ValueError(f"unknown gated action: {action!r}")
    return "HOLD" if live else "ALLOW-SIM"


def gate_report() -> dict:
    return {"gate_count": len(HOLD_GATES), "gates": HOLD_GATES}
