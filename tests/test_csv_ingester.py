import pytest
import os
from src.adapters.csv_ingester import CSVIngester

@pytest.fixture
def sample_csv(tmp_path):
    file_path = tmp_path / "readings.csv"
    content = """MPRN,Meter Serial Number,Read Value,Read Type,Read Date and End Time
10307857139,000000000032272765,0.8590,Active Import Interval (kWh),25-11-2025 01:30
10307857139,000000000032272765,0.1200,Active Export Interval (kWh),25-11-2025 01:30
10307857139,000000000032272765,0.8990,Active Import Interval (kWh),25-11-2025 01:00
10307857139,000000000032272765,0.0500,Active Export Interval (kWh),25-11-2025 01:00
"""
    file_path.write_text(content)
    return str(file_path)

def test_parse_csv(sample_csv):
    ingester = CSVIngester()
    series = ingester.parse(sample_csv)
    
    assert len(series.readings) == 2
    
    # Sort by timestamp to ensure order
    series.readings.sort(key=lambda x: x.timestamp)
    
    # 01:00 reading
    r1 = series.readings[0]
    assert r1.timestamp.hour == 1
    assert r1.timestamp.minute == 0
    assert r1.import_energy == 0.8990
    assert r1.export_energy == 0.0500
    
    # 01:30 reading
    r2 = series.readings[1]
    assert r2.timestamp.hour == 1
    assert r2.timestamp.minute == 30
    assert r2.import_energy == 0.8590
    assert r2.export_energy == 0.1200
