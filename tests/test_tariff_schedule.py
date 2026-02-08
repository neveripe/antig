import pytest
from datetime import datetime, time, timedelta
from src.domain.models import EnergySeries, EnergyReading
from src.domain.tariff import Tariff, TariffRate
from src.domain.billing import CostCalculator

class TestTariffSchedule:
    
    @pytest.fixture
    def tariff_2023(self):
        # 2023 Rate: 0.10 per kWh
        rate = TariffRate("Flat 2023", 0.10, time(0,0), time(23,59))
        return Tariff(
            name="2023 Tariff",
            import_rates=[rate],
            export_rates=[],
            standing_charge=0.50,
            valid_from=datetime(2023, 1, 1),
            valid_to=datetime(2023, 12, 31, 23, 59, 59)
        )

    @pytest.fixture
    def tariff_2024(self):
        # 2024 Rate: 0.20 per kWh (Price hike!)
        rate = TariffRate("Flat 2024", 0.20, time(0,0), time(23,59))
        return Tariff(
            name="2024 Tariff",
            import_rates=[rate],
            export_rates=[],
            standing_charge=0.60,
            valid_from=datetime(2024, 1, 1),
            valid_to=None # Indefinite
        )

    def test_tariff_switch_over_year(self, tariff_2023, tariff_2024):
        # Readings crossing the new year boundary
        readings = [
            # Dec 31st 2023 (Should be 0.10)
            EnergyReading(datetime(2023, 12, 31, 23, 0), 10.0, 0.0),
            # Jan 1st 2024 (Should be 0.20)
            EnergyReading(datetime(2024, 1, 1, 1, 0), 10.0, 0.0)
        ]
        series = EnergySeries(readings)
        
        calculator = CostCalculator()
        
        # We pass a LIST of tariffs (the schedule)
        bill = calculator.calculate_cost(series, [tariff_2023, tariff_2024])
        
        # Expected Cost:
        # 2023: 10 kWh * 0.10 = 1.00
        # 2024: 10 kWh * 0.20 = 2.00
        # Total Import: 3.00
        
        assert bill.total_import_cost == pytest.approx(3.00)
        
        # Breakdown check
        assert bill.breakdown["Flat 2023"] == pytest.approx(1.00)
        assert bill.breakdown["Flat 2024"] == pytest.approx(2.00)

    def test_standing_charge_switch(self, tariff_2023, tariff_2024):
        # 1 reading in 2023, 1 reading in 2024.
        # But standing charge is daily.
        # How do we calculate standing charge for the gap?
        # For simplicity, let's assume we calculate standing charge based on the days present in the series range,
        # applying the tariff active at the start of that day?
        # Or pro-rata?
        # Let's assume:
        # Day 1 (2023-12-31): Uses 2023 SC (0.50)
        # Day 2 (2024-01-01): Uses 2024 SC (0.60)
        
        readings = [
            EnergyReading(datetime(2023, 12, 31, 12, 0), 0.0, 0.0),
            EnergyReading(datetime(2024, 1, 1, 12, 0), 0.0, 0.0)
        ]
        series = EnergySeries(readings)
        
        calculator = CostCalculator()
        bill = calculator.calculate_cost(series, [tariff_2023, tariff_2024])
        
        # Total SC: 0.50 + 0.60 = 1.10
        assert bill.standing_charge_cost == pytest.approx(1.10)

    def test_no_matching_tariff(self, tariff_2024):
        # Reading in 2023, but only 2024 tariff provided
        readings = [
            EnergyReading(datetime(2023, 12, 31, 12, 0), 10.0, 0.0)
        ]
        series = EnergySeries(readings)
        calculator = CostCalculator()
        
        # Should raise error or ignore?
        # Raising error is safer.
        with pytest.raises(ValueError, match="No applicable tariff found"):
            calculator.calculate_cost(series, [tariff_2024])
