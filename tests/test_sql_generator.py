import pytest
from datetime import datetime
from src.domain.models import EnergyReading, EnergySeries
from src.adapters.postgres_exporter import PostgresExporter

@pytest.fixture
def sample_series():
    readings = [
        EnergyReading(datetime(2023, 1, 1, 12, 0), 10.5, 5.2),
        EnergyReading(datetime(2023, 1, 1, 13, 0), 20.0, 10.0)
    ]
    return EnergySeries(readings)

def test_generate_sql(sample_series):
    exporter = PostgresExporter(table_name="energy_readings")
    sql = exporter.generate_sql(sample_series)
    
    expected_lines = [
        "INSERT INTO energy_readings (timestamp, import_kwh, export_kwh) VALUES",
        "('2023-01-01 12:00:00', 10.5, 5.2),",
        "('2023-01-01 13:00:00', 20.0, 10.0);"
    ]
    
    # Normalize whitespace/newlines for comparison
    generated_lines = [line.strip() for line in sql.strip().split('\n')]
    assert generated_lines == expected_lines
