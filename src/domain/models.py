from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict

import pandas as pd

@dataclass
class EnergyReading:
    timestamp: datetime
    import_energy: float
    export_energy: float

class EnergySeries:
    def __init__(self, readings: List[EnergyReading]):
        self.readings = readings
        # Create a DataFrame for easier manipulation
        data = [
            {
                "timestamp": r.timestamp,
                "import_energy": r.import_energy,
                "export_energy": r.export_energy
            }
            for r in readings
        ]
        if data:
            self.df = pd.DataFrame(data)
            self.df['timestamp'] = pd.to_datetime(self.df['timestamp'])
        else:
            self.df = pd.DataFrame(columns=["timestamp", "import_energy", "export_energy"])

    def get_daily_stats(self) -> Dict[str, Dict[str, float]]:
        """
        Returns a dictionary where key is date (YYYY-MM-DD) and value is a dict of stats:
        {'import_sum': float, 'export_sum': float, 'net': float}
        """
        if self.df.empty:
            return {}
        
        daily = self.df.groupby(self.df['timestamp'].dt.date).agg({
            'import_energy': 'sum',
            'export_energy': 'sum'
        })
        daily['net'] = daily['import_energy'] - daily['export_energy']
        
        # Convert to dictionary format
        result = {}
        for date, row in daily.iterrows():
            result[str(date)] = {
                'import_sum': float(row['import_energy']),
                'export_sum': float(row['export_energy']),
                'net': float(row['net'])
            }
        return result

    def get_monthly_stats(self) -> Dict[str, Dict[str, float]]:
        """
        Returns a dictionary where key is month (YYYY-MM) and value is a dict of stats.
        """
        if self.df.empty:
            return {}

        # Group by month period
        monthly = self.df.groupby(self.df['timestamp'].dt.to_period('M')).agg({
            'import_energy': 'sum',
            'export_energy': 'sum'
        })
        monthly['net'] = monthly['import_energy'] - monthly['export_energy']

        result = {}
        for period, row in monthly.iterrows():
            result[str(period)] = {
                'import_sum': float(row['import_energy']),
                'export_sum': float(row['export_energy']),
                'net': float(row['net'])
            }
        return result

    def calculate_net_consumption(self) -> float:
        """
        Total Import - Total Export
        """
        if self.df.empty:
            return 0.0
        return float(self.df['import_energy'].sum() - self.df['export_energy'].sum())

    def filter_by_date(self, start: datetime = None, end: datetime = None) -> 'EnergySeries':
        """
        Returns a new EnergySeries filtered by the given start and end dates (inclusive).
        Timestamps in the series are assumed to be timezone-aware if start/end are.
        If start/end are naive, they are assumed to be in the same timezone as the series (or UTC if series is UTC).
        """
        if self.df.empty:
            return EnergySeries([])
            
        mask = pd.Series([True] * len(self.df), index=self.df.index)
        
        if start:
            # Ensure start has timezone if df has timezone
            if self.df['timestamp'].dt.tz is not None and start.tzinfo is None:
                # Assume UTC if not specified, or match series? 
                # Let's assume the user passes naive dates as "local" or "UTC" depending on context.
                # But here we are comparing against the internal dataframe which is likely UTC.
                # Ideally, the caller should handle timezone conversion.
                # For now, let's just compare. Pandas handles comparison if both are tz-aware or both naive.
                # If mismatch, we might need to localize.
                # Let's assume start/end are passed as they should be compared.
                mask &= (self.df['timestamp'] >= start)
            else:
                 mask &= (self.df['timestamp'] >= start)
                 
        if end:
            mask &= (self.df['timestamp'] <= end)
            
        filtered_df = self.df[mask]
        
        # Reconstruct readings from filtered DF
        readings = []
        for _, row in filtered_df.iterrows():
            readings.append(EnergyReading(
                timestamp=row['timestamp'],
                import_energy=row['import_energy'],
                export_energy=row['export_energy']
            ))
            
        return EnergySeries(readings)
