import pytest
from datetime import datetime, time, timedelta
from src.domain.models import EnergySeries, EnergyReading
from src.domain.tariff import Tariff, TariffRate, Bill
# We will implement this next
# from src.domain.billing import CostCalculator 

class TestTariffEngine:
    
    @pytest.fixture
    def simple_tariff(self):
        # Flat rate: 0.30 import, 0.10 export
        import_rate = TariffRate(
            name="Standard",
            price_per_kwh=0.30,
            start_time=time(0, 0),
            end_time=time(23, 59),
            days_of_week=[0, 1, 2, 3, 4, 5, 6]
        )
        export_rate = TariffRate(
            name="Feed-in",
            price_per_kwh=0.10,
            start_time=time(0, 0),
            end_time=time(23, 59),
            days_of_week=[0, 1, 2, 3, 4, 5, 6]
        )
        return Tariff(
            name="Simple Flat",
            import_rates=[import_rate],
            export_rates=[export_rate],
            standing_charge=0.50,
            currency="EUR"
        )

    @pytest.fixture
    def day_night_tariff(self):
        # Day: 08:00-23:00 @ 0.40
        # Night: 23:00-08:00 @ 0.20
        day_rate = TariffRate(
            name="Day",
            price_per_kwh=0.40,
            start_time=time(8, 0),
            end_time=time(23, 0),
            days_of_week=[0, 1, 2, 3, 4, 5, 6]
        )
        night_rate = TariffRate(
            name="Night",
            price_per_kwh=0.20,
            start_time=time(23, 0),
            end_time=time(8, 0),
            days_of_week=[0, 1, 2, 3, 4, 5, 6]
        )
        return Tariff(
            name="Day/Night",
            import_rates=[day_rate, night_rate],
            export_rates=[],
            standing_charge=0.0,
            currency="EUR"
        )

    def test_calculate_simple_cost(self, simple_tariff):
        # 24 hours of 1 kWh import each = 24 kWh total
        start = datetime(2023, 1, 1, 0, 0)
        readings = []
        for i in range(24):
            readings.append(EnergyReading(
                timestamp=start + timedelta(hours=i),
                import_energy=1.0,
                export_energy=0.0
            ))
        series = EnergySeries(readings)
        
        # We need to import CostCalculator here to avoid ImportError before it exists
        from src.domain.billing import CostCalculator
        calculator = CostCalculator()
        bill = calculator.calculate_cost(series, simple_tariff)
        
        # Expected:
        # Import: 24 kWh * 0.30 = 7.20
        # Standing charge: 1 day * 0.50 = 0.50
        # Total: 7.70
        
        assert bill.total_import_cost == pytest.approx(7.20)
        assert bill.standing_charge_cost == pytest.approx(0.50)
        assert bill.net_cost == pytest.approx(7.70)
        assert bill.breakdown["Standard"] == pytest.approx(7.20)

    def test_calculate_export_credit(self, simple_tariff):
        # 10 kWh export
        readings = [
            EnergyReading(
                timestamp=datetime(2023, 1, 1, 12, 0),
                import_energy=0.0,
                export_energy=10.0
            )
        ]
        series = EnergySeries(readings)
        
        from src.domain.billing import CostCalculator
        calculator = CostCalculator()
        bill = calculator.calculate_cost(series, simple_tariff)
        
        # Expected:
        # Export: 10 * 0.10 = 1.00
        # Standing charge: 1 day (even for partial data, usually daily charge applies)
        # Let's assume standing charge applies for the duration of the series (1 day here)
        
        assert bill.total_export_credit == pytest.approx(1.00)
        assert bill.net_cost == pytest.approx(0.50 - 1.00) # Standing - Credit

    def test_day_night_split(self, day_night_tariff):
        # 1 kWh at 12:00 (Day)
        # 1 kWh at 04:00 (Night)
        readings = [
            EnergyReading(datetime(2023, 1, 1, 12, 0), 1.0, 0.0),
            EnergyReading(datetime(2023, 1, 1, 4, 0), 1.0, 0.0)
        ]
        series = EnergySeries(readings)
        
        from src.domain.billing import CostCalculator
        calculator = CostCalculator()
        bill = calculator.calculate_cost(series, day_night_tariff)
        
        # Day: 1 * 0.40 = 0.40
        # Night: 1 * 0.20 = 0.20
        # Total: 0.60
        
        assert bill.breakdown["Day"] == pytest.approx(0.40)
        assert bill.breakdown["Night"] == pytest.approx(0.20)
        assert bill.total_import_cost == pytest.approx(0.60)
