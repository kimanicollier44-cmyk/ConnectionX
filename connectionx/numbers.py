"""Phone numbers: normalize, format, and allocate free synthetic numbers.

Free numbers come from the fictional 555-01XX range, the range reserved
for safe, non-real use, so a demo number can never dial a real person.
"""
from __future__ import annotations

from dataclasses import dataclass, field


def normalize_number(raw: str) -> str:
    """Return digits only, with a leading US country code stripped."""
    digits = "".join(ch for ch in raw if ch.isdigit())
    if len(digits) == 11 and digits.startswith("1"):
        digits = digits[1:]
    if len(digits) != 10:
        raise ValueError(f"not a 10-digit NANP number: {raw!r}")
    return digits


def format_number(raw: str) -> str:
    d = normalize_number(raw)
    return f"({d[0:3]}) {d[3:6]}-{d[6:10]}"


def is_synthetic(raw: str) -> bool:
    """True for the fictional 555-01XX range (exchange 555, line 0100-0199)."""
    d = normalize_number(raw)
    return d[3:6] == "555" and d[6:8] == "01"


@dataclass
class NumberPool:
    """Deterministic allocator for free synthetic numbers."""

    area_code: str = "415"
    next_line: int = 100
    used: set[str] = field(default_factory=set)

    def allocate(self) -> str:
        while True:
            candidate = f"{self.area_code}555{self.next_line:04d}"
            self.next_line += 1
            if candidate not in self.used:
                self.used.add(candidate)
                return format_number(candidate)

    def release(self, number: str) -> None:
        self.used.discard(normalize_number(number))

    def allocated_count(self) -> int:
        return len(self.used)
