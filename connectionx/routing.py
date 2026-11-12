"""Wi-Fi-first routing: the engine that keeps the service $0.

Every action (call, text, data) is routed over the cheapest working
transport first: free Wi-Fi, then the free cellular plan, never a
paid bearer for core talk and text.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Route:
    action: str
    bearer: str          # VoWiFi, Vo5G, VoLTE, RCS, SMS, Wi-Fi data, 5G data
    transport: str       # wifi, 5g, lte
    cost_usd: float
    reason: str


def choose_route(action: str, wifi_available: bool = True,
                 cell_available: bool = True, cell_gen: str = "5g",
                 rcs_available: bool = True) -> Route:
    if action not in ("call", "text", "data"):
        raise ValueError(f"unknown action: {action!r}")
    if not wifi_available and not cell_available:
        return Route(action, "none", "none", 0.0, "no network available")

    if action == "call":
        if wifi_available:
            return Route(action, "VoWiFi", "wifi", 0.0,
                         "Wi-Fi first: free, upgraded voice codec")
        bearer = "Vo5G" if cell_gen == "5g" else "VoLTE"
        return Route(action, bearer, cell_gen, 0.0,
                     "cellular voice, free on the core plan")

    if action == "text":
        if rcs_available:
            transport = "wifi" if wifi_available else cell_gen
            return Route(action, "RCS", transport, 0.0,
                         "RCS: media, receipts, group chat, $0")
        return Route(action, "SMS", cell_gen, 0.0,
                     "SMS fallback when RCS is unavailable")

    # data
    if wifi_available:
        return Route(action, "Wi-Fi data", "wifi", 0.0,
                     "Wi-Fi offload: full data costs $0")
    return Route(action, f"{cell_gen.upper()} data", cell_gen, 0.0,
                 "cellular data: essential apps free, other apps need a pass")
