"""Data ledger: what makes mobile data $0, and where $0 honestly ends.

Free forever: talk, text, and 1,024 MB/month of essential-app data on
cellular, plus unlimited data on Wi-Fi. Non-essential cellular data is
where a paid pass would start in a live service, so the ledger marks
it needs-data-pass instead of pretending it is free.
"""
from __future__ import annotations

from dataclasses import dataclass, field

FREE_ESSENTIAL_MB = 1024
ESSENTIAL_APPS = {"email", "maps", "rideshare", "finance", "messaging", "health"}
# Modelled comparison value of cellular data, for the savings report only.
MODELLED_CELL_VALUE_USD_PER_GB = 10.0


@dataclass(frozen=True)
class DataUse:
    app: str
    mb: float
    status: str       # free-wifi, free-essential, needs-data-pass
    cost_usd: float


@dataclass
class DataLedger:
    essential_used_mb: float = 0.0
    wifi_mb: float = 0.0
    uses: list[DataUse] = field(default_factory=list)

    def use(self, app: str, mb: float, on_wifi: bool) -> DataUse:
        if mb < 0:
            raise ValueError("data use cannot be negative")
        if on_wifi:
            self.wifi_mb += mb
            record = DataUse(app, mb, "free-wifi", 0.0)
        elif app in ESSENTIAL_APPS and self.essential_used_mb + mb <= FREE_ESSENTIAL_MB:
            self.essential_used_mb += mb
            record = DataUse(app, mb, "free-essential", 0.0)
        else:
            record = DataUse(app, mb, "needs-data-pass", 0.0)
        self.uses.append(record)
        return record

    def essential_remaining_mb(self) -> float:
        return FREE_ESSENTIAL_MB - self.essential_used_mb

    def wifi_offload_percent(self) -> float:
        total = self.wifi_mb + self.essential_used_mb
        if total == 0:
            return 0.0
        return round(100.0 * self.wifi_mb / total, 1)

    def modelled_savings_usd(self) -> float:
        """What the Wi-Fi offload would have cost as cellular data (modelled)."""
        gb = self.wifi_mb / 1024.0
        return round(gb * MODELLED_CELL_VALUE_USD_PER_GB, 2)
