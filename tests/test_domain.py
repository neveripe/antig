import pytest
from datetime import datetime, timedelta
from src.domain.models import EnergyReading, EnergySeries

@pytest.fixture
def sample_readings():
    base_time = datetime(2023, 1, 1, 12, 0)
    readings = []
    # Day 1: 10 readings, 10 import each, 5 export each
    for i in range(10):
        readings.append(EnergyReading(
            timestamp=base_time + timedelta(hours=i),
            import_energy=10.0,
            export_energy=5.0
        ))
    # Day 2: 10 readings, 20 import each, 10 export each
    base_time_day2 = datetime(2023, 1, 2, 12, 0)
    for i in range(10):
        readings.append(EnergyReading(
            timestamp=base_time_day2 + timedelta(hours=i),
            import_energy=20.0,
            export_energy=10.0
        ))
    return readings

def test_calculate_net_consumption(sample_readings):
    series = EnergySeries(sample_readings)
    # Day 1: 10 * (10 - 5) = 50
    # Day 2: 10 * (20 - 10) = 100
    # Total: 150
    assert series.calculate_net_consumption() == 150.0

def test_get_daily_stats(sample_readings):
    series = EnergySeries(sample_readings)
    stats = series.get_daily_stats()
    
    assert "2023-01-01" in stats
    assert stats["2023-01-01"]["import_sum"] == 100.0
    assert stats["2023-01-01"]["export_sum"] == 50.0
    assert stats["2023-01-01"]["net"] == 50.0

    assert "2023-01-02" in stats
    assert stats["2023-01-02"]["import_sum"] == 200.0
    assert stats["2023-01-02"]["export_sum"] == 100.0
    assert stats["2023-01-02"]["net"] == 100.0

def test_get_monthly_stats(sample_readings):
    series = EnergySeries(sample_readings)
    stats = series.get_monthly_stats()
    
    assert "2023-01" in stats
    assert stats["2023-01"]["import_sum"] == 300.0
    assert stats["2023-01"]["export_sum"] == 150.0
    assert stats["2023-01"]["net"] == 150.0

def test_filter_by_date(sample_readings):
    series = EnergySeries(sample_readings)
    
    # Filter for Day 1 only
    start = datetime(2023, 1, 1)
    end = datetime(2023, 1, 1, 23, 59, 59)
    
    filtered = series.filter_by_date(start, end)
    assert len(filtered.readings) == 10
    assert filtered.readings[0].timestamp.day == 1
    
    # Filter for Day 2 only
    start = datetime(2023, 1, 2)
    filtered_day2 = series.filter_by_date(start, None)
    assert len(filtered_day2.readings) == 10
    assert filtered_day2.readings[0].timestamp.day == 2
