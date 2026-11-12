"""ConnectionXService: one face for the whole free phone service."""
from __future__ import annotations

from dataclasses import dataclass, field

from .data import DataLedger
from .esim import ESIMProfile, make_profile
from .google_cloud import cloud_status
from .google_drive import DriveRegistry
from .google_flow import merged_plan
from .honeypotx import honeypotx_summary
from .payloads import run_chamber
from .messaging import MessageLog
from .numbers import NumberPool
from .routing import choose_route
from .upgrade import upgrade_report
from .voice import CallLog


@dataclass
class Subscriber:
    name: str
    number: str
    esim: ESIMProfile


@dataclass
class ConnectionXService:
    pool: NumberPool = field(default_factory=NumberPool)
    calls: CallLog = field(default_factory=CallLog)
    messages: MessageLog = field(default_factory=MessageLog)
    data: DataLedger = field(default_factory=DataLedger)
    subscribers: dict[str, Subscriber] = field(default_factory=dict)

    def activate(self, name: str) -> Subscriber:
        number = self.pool.allocate()
        profile = make_profile(number)
        profile.enable()
        sub = Subscriber(name=name, number=number, esim=profile)
        self.subscribers[number] = sub
        return sub

    def call(self, sub: Subscriber, to: str, seconds: int,
             wifi_available: bool = True, cell_gen: str = "5g"):
        route = choose_route("call", wifi_available=wifi_available, cell_gen=cell_gen)
        return self.calls.place(sub.number, to, seconds, route)

    def text(self, sub: Subscriber, to: str, body: str, media: bool = False,
             group: bool = False, rcs_available: bool = True):
        return self.messages.send(sub.number, to, body, media=media,
                                  group=group, rcs_available=rcs_available)

    def use_data(self, app: str, mb: float, on_wifi: bool):
        return self.data.use(app, mb, on_wifi)

    def bill(self) -> dict:
        """The core bill is $0. That is the whole point of the service."""
        return {
            "currency": "USD",
            "talk_usd": self.calls.total_cost(),
            "text_usd": self.messages.total_cost(),
            "essential_data_usd": 0.0,
            "esim_usd": 0.0,
            "total_usd": round(self.calls.total_cost() + self.messages.total_cost(), 2),
            "note": "core service is $0; non-essential cellular data would need a pass in a live service",
        }

    def report(self) -> dict:
        return {
            "subscribers": len(self.subscribers),
            "calls": len(self.calls.calls),
            "call_seconds": self.calls.total_seconds(),
            "messages": len(self.messages.messages),
            "essential_remaining_mb": self.data.essential_remaining_mb(),
            "wifi_offload_percent": self.data.wifi_offload_percent(),
            "modelled_savings_usd": self.data.modelled_savings_usd(),
            "bill": self.bill(),
            "upgrade": upgrade_report(),
            "chamber": run_chamber(),
            "honeypotx": honeypotx_summary(),
            "google_flow": merged_plan(),
            "google_cloud": cloud_status(),
            "google_drive": DriveRegistry().summary(),
        }
