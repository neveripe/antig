import pandas as pd
import numpy as np
from src.interfaces import IDataSource
from src.domain.models import EnergySeries, EnergyReading

class CSVIngester(IDataSource):
    """
    Ingests energy data from CSV files with specific formatting and timezone handling.

    Attributes:
        timezone (str): The timezone of the input data (default: "Europe/Dublin").
    """
    def __init__(self, timezone: str = "Europe/Dublin"):
        """
        Initializes the CSVIngester.

        Args:
            timezone (str, optional): The timezone of the input data. Defaults to "Europe/Dublin".
        """
        self.timezone = timezone

    def parse(self, source: str) -> EnergySeries:
        """
        Parses a CSV file containing energy readings.

        Handles:
            - Column renaming.
            - Naive timestamp parsing.
            - Reverse chronological order detection and correction.
            - Timezone localization and UTC conversion.
            - Robust DST handling (ambiguous times) using custom inference.

        Args:
            source (str): The path to the CSV file.

        Returns:
            EnergySeries: The parsed energy series with UTC timestamps.

        Raises:
            ValueError: If timestamp localization fails.
        """
        df = pd.read_csv(source)
        
        # Rename columns to standard names
        df = df.rename(columns={
            "Read Date and End Time": "timestamp",
            "Read Value": "value",
            "Read Type": "type"
        })
        
        # Parse timestamp
        # 1. Parse string to datetime (naive)
        df['timestamp'] = pd.to_datetime(df['timestamp'], format='%d-%m-%Y %H:%M')
        
        # Check if data is reverse chronological
        # We assume the file is either fully chronological or fully reverse chronological.
        # We check the first and last timestamp.
        if len(df) > 1 and df['timestamp'].iloc[0] > df['timestamp'].iloc[-1]:
            df = df.iloc[::-1].reset_index(drop=True)
        
        # 2. Localize to specified timezone, handling ambiguous times (DST)
        # We need to handle the fact that we have duplicate rows for import/export first?
        # No, we should probably localize BEFORE pivoting to ensure unique index if possible.
        # But wait, 'Active Import' and 'Active Export' share the same timestamp string.
        # If we localize the whole column 'ambiguous="infer"', pandas needs to see the sequence.
        # The CSV has interleaved rows (Import, Export) for the same time.
        # This breaks 'ambiguous="infer"' because it expects a monotonic time series.
        
        # Strategy:
        # 1. Split into Import and Export DataFrames.
        # 2. Localize each separately (assuming they are sequential).
        # 3. Combine.
        
        import_mask = df['type'] == 'Active Import Interval (kWh)'
        export_mask = df['type'] == 'Active Export Interval (kWh)'
        
        df_import = df[import_mask].copy()
        df_export = df[export_mask].copy()
        
        # Localize
        def localize_series(s):
            try:
                # Try default inference first
                return s.dt.tz_localize(self.timezone, ambiguous='infer').dt.tz_convert('UTC')
            except Exception:
                # Fallback: Custom inference based on chronological order
                # We assume the data is chronological (with a potential fallback jump).
                # We look for the point where time goes backwards.
                # Everything before is DST (True), everything after is STD (False).
                
                # Note: This assumes only ONE fallback per file (valid for 1 year data usually)
                # If there are multiple years, we might need to reset the flag?
                # But usually files are processed in chunks or we can detect multiple drops.
                # Actually, for multiple years, we will have multiple drops.
                # 2022 Fallback -> Drop
                # 2023 Spring -> Gap (No drop)
                # 2023 Fallback -> Drop
                
                # So we need to toggle? No, Spring forward is a gap, not a drop.
                # So every time we see a drop, it MUST be a DST fallback.
                # So we are in DST until the drop, then STD.
                # Then Spring happens (gap), we are back in DST.
                # But naive time doesn't show the gap as a drop. It just skips an hour.
                # So we can't easily detect the start of DST just by looking at naive times unless we check against expected transition dates.
                
                # However, 'ambiguous' argument is only used for AMBIGUOUS times.
                # For non-ambiguous times, the flag is ignored.
                # So we can just construct a flag array that is True (DST) until the drop, then False (STD).
                # But wait, after the fallback, we are in STD. When do we go back to DST?
                # Next Spring.
                # So we need to detect when we enter DST again.
                # But we don't need to detect it for 'ambiguous' handling, because Spring transition is NOT ambiguous (it's non-existent or gap).
                # The only ambiguous time is the Fallback.
                
                # So, effectively:
                # If we are in an ambiguous period:
                #   If we haven't seen a drop yet, it's DST.
                #   If we have seen a drop, it's STD.
                
                # Let's try to construct an array of booleans.
                # We can iterate and detect drops.
                # But this is slow in Python.
                # Vectorized approach:
                # Calculate diff.
                # Find indices where diff < 0.
                # These are the transition points.
                
                # But wait, what if the file spans multiple years?
                # We might have multiple fallbacks.
                # Fallback 1: Drop. DST -> STD.
                # ... Winter ...
                # ... Spring (Gap) ... STD -> DST.
                # ... Summer ...
                # Fallback 2: Drop. DST -> STD.
                
                # So the logic "DST until drop" is only valid for the *current* ambiguous block.
                # But since 'ambiguous' flag is ignored for non-ambiguous times, maybe we can just say:
                # "If we are in a sequence of ambiguous times, the first half is DST, second is STD".
                
                # Let's use a simpler heuristic that solves the immediate "2 dst switches" error.
                # If 'infer' fails, we assume it's because of the fallback structure.
                # We can try to force the first occurrence of ambiguous times to be DST.
                
                # Let's implement the "Drop detection" for the ambiguous flags.
                # We need an array of booleans matching the length of the series.
                # True = DST, False = STD.
                
                # We can use `tz_localize(..., ambiguous='NaT')` to find WHICH are ambiguous.
                ambiguous_mask = s.dt.tz_localize(self.timezone, ambiguous='NaT').isna()
                
                if not ambiguous_mask.any():
                    # Should not happen if 'infer' failed, unless it failed for other reasons
                    raise
                
                flags = np.array([True] * len(s))
                
                # Identify drops
                # We iterate manually to be safe and handle state
                current_dst = True
                for i in range(1, len(s)):
                    if s.iloc[i] < s.iloc[i-1]:
                        # Drop detected -> Fallback -> Switch to STD
                        current_dst = False
                    elif s.iloc[i] > s.iloc[i-1] + pd.Timedelta(hours=1):
                         # Large jump -> Spring Forward? -> Switch to DST
                         current_dst = True
                    
                    # If we are in an ambiguous time, apply the state
                    if ambiguous_mask.iloc[i]:
                        flags[i] = current_dst
                
                return s.dt.tz_localize(self.timezone, ambiguous=flags).dt.tz_convert('UTC')

        try:
            df_import['timestamp'] = localize_series(df_import['timestamp'])
            df_export['timestamp'] = localize_series(df_export['timestamp'])
        except Exception as e:
            # Fallback or re-raise with clearer message
            raise ValueError(f"Error localizing timestamps: {e}")

        imports = df_import.set_index('timestamp')['value']
        exports = df_export.set_index('timestamp')['value']
        
        # Combine into a single DataFrame
        # Now the index is UTC, so it should be unique
        combined = pd.DataFrame({
            'import_energy': imports,
            'export_energy': exports
        }).fillna(0.0)
        
        readings = []
        for ts, row in combined.iterrows():
            readings.append(EnergyReading(
                timestamp=ts,
                import_energy=float(row['import_energy']),
                export_energy=float(row['export_energy'])
            ))
            
        return EnergySeries(readings)
