from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import time, datetime

@dataclass
class TariffRate:
    """
    Represents a specific price for a specific time window.
    """
    name: str
    price_per_kwh: float
    start_time: time
    end_time: time
    days_of_week: List[int] = field(default_factory=lambda: [0, 1, 2, 3, 4, 5, 6]) # 0=Mon, 6=Sun

@dataclass
class Tariff:
    """
    A collection of rates and standing charges.
    """
    name: str
    import_rates: List[TariffRate]
    export_rates: List[TariffRate]
    standing_charge: float
    currency: str = "EUR"
    valid_from: Optional[datetime] = None
    valid_to: Optional[datetime] = None
    timezone: str = "Europe/Dublin"  # Timezone for rate schedules (local time)


@dataclass
class Bill:
    """
    The result of a cost calculation.
    """
    period_start: datetime
    period_end: datetime
    total_import_cost: float = 0.0
    total_export_credit: float = 0.0
    standing_charge_cost: float = 0.0
    net_cost: float = 0.0
    breakdown: Dict[str, float] = field(default_factory=dict)
