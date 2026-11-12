"""Messaging: RCS first (upgraded), SMS as the honest fallback."""
from __future__ import annotations

import math
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Message:
    sender: str
    recipient: str
    body: str
    protocol: str            # RCS or SMS
    media: bool
    group: bool
    segments: int            # SMS segments; RCS is always 1
    features: tuple[str, ...]
    cost_usd: float


@dataclass
class MessageLog:
    messages: list[Message] = field(default_factory=list)

    def send(self, sender: str, recipient: str, body: str, media: bool = False,
             group: bool = False, rcs_available: bool = True) -> Message:
        if not body and not media:
            raise ValueError("empty message")
        if rcs_available:
            feats = ["read-receipt", "typing-indicator"]
            if media:
                feats.append("full-res-media")
            if group:
                feats.append("group-chat")
            msg = Message(sender, recipient, body, "RCS", media, group, 1,
                          tuple(feats), 0.0)
        else:
            if media:
                raise ValueError("SMS cannot carry media in this model; use RCS")
            segments = max(1, math.ceil(len(body) / 160))
            msg = Message(sender, recipient, body, "SMS", False, group,
                          segments, (), 0.0)
        self.messages.append(msg)
        return msg

    def total_cost(self) -> float:
        return round(sum(m.cost_usd for m in self.messages), 2)
