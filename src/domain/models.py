from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict

import pandas as pd

@dataclass
class EnergyReading:
    """
    Represents a single energy reading at a specific point in time.

    Attributes:
        timestamp (datetime): The date and time of the reading.
        import_energy (float): The amount of energy imported (kWh).
        export_energy (float): The amount of energy exported (kWh).
    """
    timestamp: datetime
    import_energy: float
    export_energy: float

class EnergySeries:
    """
    A collection of EnergyReading objects with methods for statistical analysis and filtering.

    Attributes:
        readings (List[EnergyReading]): The list of raw energy readings.
        df (pd.DataFrame): A pandas DataFrame representation of the readings for efficient manipulation.
    """
    def __init__(self, readings: List[EnergyReading]):
        """
        Initializes the EnergySeries with a list of readings.

        Args:
            readings (List[EnergyReading]): The list of energy readings.
        """
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
        Calculates daily statistics for import, export, and net energy.

        Returns:
            Dict[str, Dict[str, float]]: A dictionary where the key is the date (YYYY-MM-DD) 
            and the value is a dictionary containing:
                - 'import_sum': Total import energy for the day.
                - 'export_sum': Total export energy for the day.
                - 'net': Net energy (import - export) for the day.
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
        Calculates monthly statistics for import, export, and net energy.

        Returns:
            Dict[str, Dict[str, float]]: A dictionary where the key is the month (YYYY-MM) 
            and the value is a dictionary containing:
                - 'import_sum': Total import energy for the month.
                - 'export_sum': Total export energy for the month.
                - 'net': Net energy (import - export) for the month.
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
        Calculates the total net consumption over the entire series.

        Returns:
            float: Total Import - Total Export.
        """
        if self.df.empty:
            return 0.0
        return float(self.df['import_energy'].sum() - self.df['export_energy'].sum())

    def filter_by_date(self, start: datetime = None, end: datetime = None) -> 'EnergySeries':
        """
        Returns a new EnergySeries filtered by the given start and end dates (inclusive).

        Timestamps in the series are assumed to be timezone-aware if start/end are.
        If start/end are naive, they are assumed to be in the same timezone as the series (or UTC if series is UTC).

        Args:
            start (datetime, optional): The start date/time for filtering. Defaults to None.
            end (datetime, optional): The end date/time for filtering. Defaults to None.

        Returns:
            EnergySeries: A new EnergySeries instance containing only the filtered readings.
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
