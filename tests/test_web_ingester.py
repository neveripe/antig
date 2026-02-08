"""
Tests for web-specific CSV ingester.
Tests the WebCSVIngester class that adapts CSV ingestion for browser environment.

NOTE: These tests are marked with @pytest.mark.browser because they import
web/energy_processor_web.py which requires PyScript modules (js, pyodide, pyscript)
that are only available in browser environments. They are skipped in CI/CD.
"""

import pytest
from datetime import datetime
import pandas as pd

# Try to import web module, skip all tests if not available (non-browser environment)
try:
    from web.energy_processor_web import WebCSVIngester
    from src.domain.models import EnergySeries
    BROWSER_AVAILABLE = True
except (ImportError, ModuleNotFoundError):
    BROWSER_AVAILABLE = False
    WebCSVIngester = None  # type: ignore
    EnergySeries = None  # type: ignore

# Skip entire module if browser dependencies not available
pytestmark = pytest.mark.skipif(
    not BROWSER_AVAILABLE,
    reason="Requires PyScript modules (js, pyodide, pyscript) - browser environment only"
)


@pytest.mark.browser
class TestWebCSVIngester:
    """Test suite for WebCSVIngester class."""
    
    @pytest.fixture
    def sample_csv_content(self):
        """Sample CSV content as string (simulating paste)."""
        return """MPRN,Meter Serial Number,Read Value,Read Type,Read Date and End Time
10307857139,000000000032272765,0.8590,Active Import Interval (kWh),25-11-2025 01:30
10307857139,000000000032272765,0.1200,Active Export Interval (kWh),25-11-2025 01:30
10307857139,000000000032272765,0.8990,Active Import Interval (kWh),25-11-2025 01:00
10307857139,000000000032272765,0.0500,Active Export Interval (kWh),25-11-2025 01:00"""
    
    @pytest.fixture
    def reverse_csv_content(self):
        """CSV content in reverse chronological order."""
        return """MPRN,Meter Serial Number,Read Value,Read Type,Read Date and End Time
10307857139,000000000032272765,0.8590,Active Import Interval (kWh),25-11-2025 02:00
10307857139,000000000032272765,0.1200,Active Export Interval (kWh),25-11-2025 02:00
10307857139,000000000032272765,0.8990,Active Import Interval (kWh),25-11-2025 01:00
10307857139,000000000032272765,0.0500,Active Export Interval (kWh),25-11-2025 01:00"""
    
    def test_ingester_initialization(self):
        """Test WebCSVIngester can be initialized."""
        ingester = WebCSVIngester()
        assert ingester.timezone == "Europe/Dublin"
        
        ingester_custom = WebCSVIngester(timezone="UTC")
        assert ingester_custom.timezone == "UTC"
    
    def test_parse_csv_from_string(self, sample_csv_content):
        """Test parsing CSV content from string."""
        ingester = WebCSVIngester()
        series = ingester.parse(sample_csv_content)
        
        assert isinstance(series, EnergySeries)
        assert len(series.readings) == 2  # Two unique timestamps
    
    def test_parse_creates_correct_readings(self, sample_csv_content):
        """Test that parsed readings have correct values."""
        ingester = WebCSVIngester()
        series = ingester.parse(sample_csv_content)
        
        # Sort by timestamp
        series.readings.sort(key=lambda x: x.timestamp)
        
        # First reading (01:00)
        r1 = series.readings[0]
        assert r1.import_energy == 0.8990
        assert r1.export_energy == 0.0500
        
        # Second reading (01:30)
        r2 = series.readings[1]
        assert r2.import_energy == 0.8590
        assert r2.export_energy == 0.1200
    
    def test_parse_handles_reverse_chronological(self, reverse_csv_content):
        """Test that reverse chronological data is corrected."""
        ingester = WebCSVIngester()
        series = ingester.parse(reverse_csv_content)
        
        # Should still create proper series
        assert len(series.readings) == 2
        
        # Verify timestamps are in order (should be sorted by ingester)
        series.readings.sort(key=lambda x: x.timestamp)
        assert series.readings[0].timestamp < series.readings[1].timestamp
    
    def test_parse_timezone_conversion(self, sample_csv_content):
        """Test that timestamps are converted to UTC."""
        ingester = WebCSVIngester()
        series = ingester.parse(sample_csv_content)
        
        # All timestamps should be timezone-aware (UTC)
        for reading in series.readings:
            assert reading.timestamp.tzinfo is not None
    
    def test_parse_empty_csv_fails(self):
        """Test that empty CSV content raises error."""
        ingester = WebCSVIngester()
        
        with pytest.raises(Exception):
            ingester.parse("")
    
    def test_parse_malformed_csv_fails(self):
        """Test that malformed CSV raises appropriate error."""
        ingester = WebCSVIngester()
        
        malformed = "This is not CSV data"
        
        with pytest.raises(Exception):
            ingester.parse(malformed)
    
    def test_parse_missing_columns_fails(self):
        """Test that CSV missing required columns fails."""
        ingester = WebCSVIngester()
        
        incomplete = """Column1,Column2,Column3
value1,value2,value3"""
        
        with pytest.raises(Exception):
            ingester.parse(incomplete)
    
    def test_parse_combines_import_export(self, sample_csv_content):
        """Test that import and export values are combined correctly."""
        ingester = WebCSVIngester()
        series = ingester.parse(sample_csv_content)
        
        # Each reading should have both import and export
        for reading in series.readings:
            assert reading.import_energy >= 0
            assert reading.export_energy >= 0
    
    def test_parse_large_dataset_performance(self):
        """Test that ingester can handle large datasets (1000 rows)."""
        # Generate large CSV
        rows = ["MPRN,Meter Serial Number,Read Value,Read Type,Read Date and End Time"]
        base_date = datetime(2025, 1, 1, 0, 0)
        
        for i in range(500):  # 500 timestamps * 2 rows each = 1000 rows
            timestamp = base_date.replace(minute=i % 60, hour=i // 60)
            date_str = timestamp.strftime("%d-%m-%Y %H:%M")
            rows.append(f"12345,12345,1.0,Active Import Interval (kWh),{date_str}")
            rows.append(f"12345,12345,0.5,Active Export Interval (kWh),{date_str}")
        
        large_csv = "\n".join(rows)
        
        ingester = WebCSVIngester()
        series = ingester.parse(large_csv)
        
        assert len(series.readings) == 500
    
    def test_parse_preserves_domain_model_behavior(self, sample_csv_content):
        """Test that parsed series works with domain model methods."""
        ingester = WebCSVIngester()
        series = ingester.parse(sample_csv_content)
        
        # Should be able to use EnergySeries methods
        net_consumption = series.calculate_net_consumption()
        assert isinstance(net_consumption, float)
        
        # Should have valid dataframe
        assert series.df is not None
        assert not series.df.empty


@pytest.mark.browser
class TestWebIntegration:
    """Integration tests for web-specific functionality."""
    
    def test_pasted_csv_matches_file_upload(self, sample_csv_content):
        """Test that pasted CSV produces same result as file upload."""
        from src.adapters.csv_ingester import CSVIngester
        import tempfile
        import os
        
        # Create temp file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
            f.write(sample_csv_content)
            temp_path = f.name
        
        try:
            # Parse from file (CLI method)
            cli_ingester = CSVIngester()
            cli_series = cli_ingester.parse(temp_path)
            
            # Parse from string (web method)
            web_ingester = WebCSVIngester()
            web_series = web_ingester.parse(sample_csv_content)
            
            # Results should be identical
            assert len(cli_series.readings) == len(web_series.readings)
            
            # Sort both for comparison
            cli_series.readings.sort(key=lambda x: x.timestamp)
            web_series.readings.sort(key=lambda x: x.timestamp)
            
            for cli_r, web_r in zip(cli_series.readings, web_series.readings):
                assert cli_r.timestamp == web_r.timestamp
                assert cli_r.import_energy == web_r.import_energy
                assert cli_r.export_energy == web_r.export_energy
        
        finally:
            os.unlink(temp_path)
    
    @pytest.fixture
    def sample_csv_content(self):
        """Fixture for sample CSV data."""
        return """MPRN,Meter Serial Number,Read Value,Read Type,Read Date and End Time
10307857139,000000000032272765,0.8590,Active Import Interval (kWh),25-11-2025 01:30
10307857139,000000000032272765,0.1200,Active Export Interval (kWh),25-11-2025 01:30
10307857139,000000000032272765,0.8990,Active Import Interval (kWh),25-11-2025 01:00
10307857139,000000000032272765,0.0500,Active Export Interval (kWh),25-11-2025 01:00"""
