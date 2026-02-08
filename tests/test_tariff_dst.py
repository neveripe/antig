import pytest
from datetime import datetime, time
import pytz
from src.domain.models import EnergySeries, EnergyReading
from src.domain.tariff import Tariff, TariffRate
from src.domain.billing import CostCalculator

class TestTariffDST:
    
    @pytest.fixture
    def irish_tariff(self):
        # Night rate starts at 23:00 Local Time
        # Day rate starts at 08:00 Local Time
        day_rate = TariffRate("Day", 0.40, time(8, 0), time(23, 0))
        night_rate = TariffRate("Night", 0.20, time(23, 0), time(8, 0))
        
        return Tariff(
            name="Irish Day/Night",
            import_rates=[day_rate, night_rate],
            export_rates=[],
            standing_charge=0.0,
            timezone="Europe/Dublin"  # Explicit timezone for rate schedules
        )

    def test_summer_dst_boundary(self, irish_tariff):
        # Date: June 21st (Summer Solstice) - DST is Active (UTC+1)
        # We want to test 23:30 Local Time.
        # 23:30 Local = 22:30 UTC.
        
        # If logic uses UTC: 22:30 is < 23:00, so it thinks it's DAY.
        # If logic uses Local: 23:30 is > 23:00, so it knows it's NIGHT.
        
        timestamp_utc = datetime(2023, 6, 21, 22, 30, tzinfo=pytz.UTC)
        
        readings = [
            EnergyReading(timestamp_utc, 1.0, 0.0)
        ]
        series = EnergySeries(readings)
        
        calculator = CostCalculator()
        
        # We expect this to be NIGHT rate (0.20)
        # But without TZ logic, it will likely be DAY rate (0.40)
        bill = calculator.calculate_cost(series, irish_tariff)
        
        # Check breakdown
        # If it fails, it will show Day: 0.40
        assert bill.breakdown.get("Night", 0.0) == pytest.approx(0.20)
        assert bill.breakdown.get("Day", 0.0) == pytest.approx(0.0)
