"""Voice: upgraded codecs and a deterministic call log."""
from __future__ import annotations

from dataclasses import dataclass, field

from .routing import Route

# Every call is upgraded to the best codec its bearer supports.
CODEC_BY_BEARER = {
    "VoWiFi": "EVS Fullband",
    "Vo5G": "EVS Fullband",
    "VoLTE": "AMR-WB (HD Voice)",
    "none": "none",
}
OLD_TO_NEW_CODEC = {"AMR-NB": "AMR-WB (HD Voice)", "AMR-WB (HD Voice)": "EVS Fullband"}


@dataclass(frozen=True)
class Call:
    caller: str
    callee: str
    seconds: int
    bearer: str
    codec: str
    cost_usd: float


@dataclass
class CallLog:
    calls: list[Call] = field(default_factory=list)

    def place(self, caller: str, callee: str, seconds: int, route: Route) -> Call:
        if seconds < 0:
            raise ValueError("call length cannot be negative")
        call = Call(caller, callee, seconds, route.bearer,
                    CODEC_BY_BEARER.get(route.bearer, "none"), route.cost_usd)
        self.calls.append(call)
        return call

    def total_seconds(self) -> int:
        return sum(c.seconds for c in self.calls)

    def total_cost(self) -> float:
        return round(sum(c.cost_usd for c in self.calls), 2)
