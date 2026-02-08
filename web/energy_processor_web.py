"""
Energy Processor Web - PyScript Bridge
This module runs in the browser and connects the existing Python code to the web UI.
NO CODE DUPLICATION - imports from existing src/ modules.
"""

import sys
import io
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from js import document, window, console
from pyodide.ffi import create_proxy

# Add parent directory to path to import from src/
sys.path.append('..')

# Import our existing Python codebase (source of truth!)
from src.domain.models import EnergySeries, EnergyReading

class WebCSVIngester:
    """
    Browser-compatible version of CSVIngester.
    Uses the SAME logic but adapted for browser environment.
    """
    def __init__(self, timezone: str = "Europe/Dublin"):
        self.timezone = timezone
    
    def parse(self, csv_content: str) -> EnergySeries:
        """
        Parse CSV content from browser FileReader.
        Reuses logic from src/adapters/csv_ingester.py
        """
        # Create DataFrame from string content
        df = pd.read_csv(io.StringIO(csv_content))
        
        # Rename columns (same as original)
        df = df.rename(columns={
            "Read Date and End Time": "timestamp",
            "Read Value": "value",
            "Read Type": "type"
        })
        
        # Parse timestamp
        df['timestamp'] = pd.to_datetime(df['timestamp'], format='%d-%m-%Y %H:%M')
        
        # Check if reverse chronological
        if len(df) > 1 and df['timestamp'].iloc[0] > df['timestamp'].iloc[-1]:
            df = df.iloc[::-1].reset_index(drop=True)
        
        # Split import/export
        import_mask = df['type'] == 'Active Import Interval (kWh)'
        export_mask = df['type'] == 'Active Export Interval (kWh)'
        
        df_import = df[import_mask].copy()
        df_export = df[export_mask].copy()
        
        # Localize timestamps
        def localize_series(s):
            try:
                return s.dt.tz_localize(self.timezone, ambiguous='infer').dt.tz_convert('UTC')
            except:
                # Simplified fallback for browser
                return s.dt.tz_localize(self.timezone, ambiguous=True).dt.tz_convert('UTC')
        
        df_import['timestamp'] = localize_series(df_import['timestamp'])
        df_export['timestamp'] = localize_series(df_export['timestamp'])
        
        # Combine
        imports = df_import.set_index('timestamp')['value']
        exports = df_export.set_index('timestamp')['value']
        
        combined = pd.DataFrame({
            'import_energy': imports,
            'export_energy': exports
        }).fillna(0.0)
        
        # Create EnergyReading objects (using existing domain model!)
        readings = []
        for ts, row in combined.iterrows():
            readings.append(EnergyReading(
                timestamp=ts,
                import_energy=float(row['import_energy']),
                export_energy=float(row['export_energy'])
            ))
        
        # Return EnergySeries (existing domain model!)
        return EnergySeries(readings)


# Global state
current_series = None
file_name = None


def process_csv(content: str, filename: str):
    """
    Called from JavaScript when user uploads a file.
    """
    global current_series, file_name
    
    try:
        window.showStatus('Processing CSV file...', 'info')
        
        # Use our web-adapted ingester
        ingester = WebCSVIngester()
        current_series = ingester.parse(content)
        file_name = filename
        
        # Show success
        window.showStatus(
            f'✅ Loaded {len(current_series.readings):,} readings from {filename}', 
            'success'
        )
        
        # Set date range based on data
        if current_series.df is not None and not current_series.df.empty:
            min_date = current_series.df['timestamp'].min().strftime('%Y-%m-%d')
            max_date = current_series.df['timestamp'].max().strftime('%Y-%m-%d')
            
            document.getElementById('startDate').value = min_date
            document.getElementById('endDate').value = max_date
        
        # Show controls
        window.showControls()
        
        # Auto-generate first graph
        generate_graph_python(None, None)
        
    except Exception as e:
        window.showStatus(f'❌ Error processing file: {str(e)}', 'error')
        console.error(f'Error: {e}')


def generate_graph_python(start_date_str, end_date_str):
    """
    Generate graph using matplotlib.
    Called from JavaScript when user clicks Generate button.
    """
    global current_series
    
    if current_series is None:
        window.showStatus('❌ No data loaded', 'error')
        return
    
    try:
        window.showLoader()
        window.showStatus('Generating graph...', 'info')
        
        # Filter by date if provided (using existing domain method!)
        series = current_series
        if start_date_str and end_date_str:
            start = pd.to_datetime(start_date_str).tz_localize('Europe/Dublin').tz_convert('UTC')
            end = pd.to_datetime(end_date_str).tz_localize('Europe/Dublin').tz_convert('UTC')
            
            # Use existing filter_by_date method!
            series = current_series.filter_by_date(start, end)
        
        if series.df.empty:
            window.showStatus('❌ No data in selected date range', 'error')
            window.hideLoader()
            return
        
        # Calculate stats (using existing domain methods!)
        total_import = series.df['import_energy'].sum()
        total_export = series.df['export_energy'].sum()
        net_consumption = series.calculate_net_consumption()
        
        # Show stats
        stats = {
            'total_readings': len(series.readings),
            'total_import': total_import,
            'total_export': total_export,
            'net_consumption': net_consumption
        }
        window.showStats(stats)
        
        # Create matplotlib figure
        plt.figure(figsize=(12, 6))
        plt.style.use('dark_background')
        
        x = series.df['timestamp']
        y_import = series.df['import_energy']
        y_export = series.df['export_energy']
        
        plt.plot(x, y_import, label=f'Import (Total: {total_import:.2f} kWh)', 
                linewidth=2, color='#60a5fa')
        plt.plot(x, y_export, label=f'Export (Total: {total_export:.2f} kWh)', 
                linewidth=2, color='#f59e0b')
        
        plt.xlabel('Time', fontsize=12)
        plt.ylabel('Energy (kWh)', fontsize=12)
        plt.title(
            f'Energy Import vs Export Over Time\nTotal Import: {total_import:.2f} kWh | Total Export: {total_export:.2f} kWh',
            fontsize=14, pad=20
        )
        plt.legend(fontsize=10)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        # Display in browser
        display(plt, target="graph-container", append=False)
        
        window.hideLoader()
        window.showStatus(
            f'✅ Graph generated successfully ({len(series.readings):,} readings)', 
            'success'
        )
        
    except Exception as e:
        window.hideLoader()
        window.showStatus(f'❌ Error generating graph: {str(e)}', 'error')
        console.error(f'Error: {e}')


# Expose functions to JavaScript
window.processCSV = create_proxy(process_csv)
window.generateGraphPython = create_proxy(generate_graph_python)

# Initialize
console.log('✅ PyScript loaded - Energy Processor ready!')
window.showStatus('✅ Ready to process your energy data', 'success')
