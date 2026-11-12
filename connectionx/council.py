"""The council: Gemini Carbon 4 decides, Muse advises, neither calls live.

Offline and deterministic. The Decider runs MAP, MODEL, STRESS, DECIDE.
The Muse advisor can only tighten a decision (ALLOW to HOLD), never
loosen one. API keys are presence-only and are never read for a value
here; there are no live calls in this module.
"""
from __future__ import annotations

import os
from dataclasses import dataclass

DECIDER = {
    "name": "Gemini Argon 4 Extended Thinking",
    "also_known_as": "Gemini Carbon 4 Extended Thinking",
    "model": "gemini-2.5-pro",
    "route": "google/gemini-carbon-4-extended-pro-thinking",
    "thinking_tiers": (2048, 8192, 32768),
    "default_tier": 32768,
    "role": "DECIDER",
}
ADVISOR = {
    "name": "Muse",
    "models": ("muse-spark-1.1", "muse-wonder-1.0"),
    "role": "advisor",
    "authority": "none - tighten-only",
}


@dataclass(frozen=True)
class Decision:
    verdict: str            # ALLOW or HOLD
    trace: tuple[str, ...]
    advisor_notes: tuple[str, ...]


def _key_present(env_name: str) -> bool:
    value = os.environ.get(env_name)
    return bool(value)


def council_status() -> dict:
    return {
        "decider": DECIDER,
        "advisor": ADVISOR,
        "gemini_key_present": _key_present("GEMINI_API_KEY"),
        "model_key_present": _key_present("MODEL_API_KEY"),
        "live_calls": 0,
    }


def decide(wants_live_carrier: bool = False, wants_emergency_routing: bool = False,
           wants_other_person_data: bool = False) -> Decision:
    trace = [
        "MAP: route the request through the upgraded stack",
        "MODEL: Wi-Fi first keeps core talk and text at $0",
        "STRESS: check carrier, spectrum, emergency, and privacy gates",
    ]
    risky = wants_live_carrier or wants_emergency_routing or wants_other_person_data
    verdict = "HOLD" if risky else "ALLOW"
    trace.append(f"DECIDE: {verdict}")
    notes = (
        "keep the $0 core bill absolute",
        "prefer Wi-Fi offload before cellular",
        "never model an emergency call as routed",
        "a HOLD from any seat is final",
    )
    return Decision(verdict, tuple(trace), notes)


def apply_advice(decision: Decision, advisor_wants_hold: bool) -> Decision:
    """Tighten-only: advice may turn ALLOW into HOLD, never the reverse."""
    if advisor_wants_hold and decision.verdict == "ALLOW":
        return Decision("HOLD", decision.trace + ("ADVISOR: tighten to HOLD",),
                        decision.advisor_notes)
    return decision
