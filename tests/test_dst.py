import pytest
import pandas as pd
from src.adapters.csv_ingester import CSVIngester

@pytest.fixture
def dst_csv(tmp_path):
    file_path = tmp_path / "dst_readings.csv"
    # Simulating DST fallback (clocks go back at 2am)
    # 01:30 occurs twice. First is DST (UTC+1), second is STD (UTC+0)
    # Note: In reality, file order matters for 'ambiguous="infer"'
    content = """MPRN,Meter Serial Number,Read Value,Read Type,Read Date and End Time
10307857139,000000000032272765,1.0,Active Import Interval (kWh),30-10-2022 01:30
10307857139,000000000032272765,0.0,Active Export Interval (kWh),30-10-2022 01:30
10307857139,000000000032272765,2.0,Active Import Interval (kWh),30-10-2022 01:30
10307857139,000000000032272765,0.0,Active Export Interval (kWh),30-10-2022 01:30
"""
    file_path.write_text(content)
    return str(file_path)

def test_parse_dst_transition(dst_csv):
    # Europe/Dublin DST end 2022: Oct 30 02:00 -> 01:00
    ingester = CSVIngester(timezone="Europe/Dublin")
    series = ingester.parse(dst_csv)
    
    assert len(series.readings) == 2
    
    # Sort by timestamp
    series.readings.sort(key=lambda x: x.timestamp)
    
    r1 = series.readings[0]
    r2 = series.readings[1]
    
    # Both have local time 01:30, but different UTC times
    # First 01:30 is IST (UTC+1) -> 00:30 UTC
    # Second 01:30 is GMT (UTC+0) -> 01:30 UTC
    
    # Check if they are distinct
    assert r1.timestamp != r2.timestamp
    
    # Check values to ensure correct mapping (assuming file order is preserved)
    # First in file = First in time (usually)
    assert r1.import_energy == 1.0
    assert r2.import_energy == 2.0
