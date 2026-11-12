"""Everything upgraded: the old stack and its ConnectionX replacement.

Radio speeds are modelled planning figures, labelled as such, never
measured claims. 6G is a simulation profile, like the LTE-6G project.
"""
from __future__ import annotations

COMPONENTS = [
    {"name": "voice", "old": "circuit calls / AMR-NB", "upgraded": "Vo5G + VoWiFi, EVS Fullband",
     "status": "upgraded"},
    {"name": "text", "old": "SMS only", "upgraded": "RCS first, SMS fallback",
     "status": "upgraded"},
    {"name": "sim", "old": "plastic SIM card", "upgraded": "free eSIM, instant activation",
     "status": "upgraded"},
    {"name": "routing", "old": "tower only", "upgraded": "Wi-Fi first, tower second",
     "status": "upgraded"},
    {"name": "number", "old": "carrier-assigned, paid line", "upgraded": "free number in the app",
     "status": "upgraded"},
    {"name": "voicemail", "old": "call-in voicemail", "upgraded": "visual voicemail + transcript (modelled)",
     "status": "modelled"},
    {"name": "security", "old": "no spam filter", "upgraded": "spam filter + verified caller ID (modelled)",
     "status": "modelled"},
    {"name": "radio", "old": "4G LTE", "upgraded": "5G live profile, 6G simulation profile",
     "status": "modelled"},
]

RADIO_PROFILES = {
    "lte": {"down_mbps_modelled": 100, "latency_ms_modelled": 30, "measured": False},
    "5g": {"down_mbps_modelled": 1000, "latency_ms_modelled": 10, "measured": False},
    "6g-sim": {"down_mbps_modelled": 10000, "latency_ms_modelled": 1, "measured": False},
}


def upgrade_report() -> dict:
    upgraded = [c["name"] for c in COMPONENTS if c["status"] == "upgraded"]
    modelled = [c["name"] for c in COMPONENTS if c["status"] == "modelled"]
    return {
        "components": COMPONENTS,
        "upgraded": upgraded,
        "modelled": modelled,
        "everything_upgraded_or_modelled": len(upgraded) + len(modelled) == len(COMPONENTS),
        "modelled_not_measured": True,
    }
