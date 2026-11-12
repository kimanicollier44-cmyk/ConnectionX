"""eSIM: free, instant, no plastic card and no store visit.

Activation codes use the reserved .invalid domain on purpose: they are
synthetic profiles for the service model, never a real carrier profile.
Live carrier activation stays behind a HOLD gate.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass

STATES = ("downloaded", "installed", "enabled", "disabled")
_NEXT = {"downloaded": "installed", "installed": "enabled",
         "enabled": "disabled", "disabled": "enabled"}


@dataclass
class ESIMProfile:
    profile_id: str
    iccid: str
    state: str = "downloaded"

    @property
    def activation_code(self) -> str:
        token = hashlib.sha256(self.iccid.encode()).hexdigest()[:16].upper()
        return f"LPA:1$smdp.connectionx.invalid${token}"

    def advance(self) -> str:
        self.state = _NEXT[self.state]
        return self.state

    def enable(self) -> str:
        while self.state != "enabled":
            self.advance()
        return self.state


def make_profile(profile_id: str) -> ESIMProfile:
    digest = hashlib.sha256(profile_id.encode()).hexdigest()
    iccid = "8901" + "".join(str(int(ch, 16) % 10) for ch in digest[:15])
    return ESIMProfile(profile_id=profile_id, iccid=iccid)


def upgrade_from_sim(sim_id: str) -> dict:
    """The plastic-SIM to eSIM upgrade plan."""
    profile = make_profile(sim_id)
    return {
        "old": f"plastic SIM {sim_id}",
        "new": "eSIM",
        "iccid": profile.iccid,
        "activation_code": profile.activation_code,
        "cost_usd": 0.0,
        "steps": [
            "keep the same number",
            "download the eSIM profile over Wi-Fi",
            "install the profile",
            "enable the profile and disable the plastic SIM",
            "recycle the plastic SIM",
        ],
    }
