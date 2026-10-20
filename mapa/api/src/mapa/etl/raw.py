from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class RawObservation:
    """Una cifra tal como sale de la fuente, antes de tocar la base."""

    jurisdiction: str  # slug
    indicator: str  # slug
    period: str
    value: Decimal
    cv: Decimal | None = None
    reliability: str | None = None  # ok | caution | unreliable | None (no evaluada)
