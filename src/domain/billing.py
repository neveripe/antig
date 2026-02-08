from datetime import datetime, time, timedelta
from typing import List, Optional, Union
import pytz
from src.domain.models import EnergySeries, EnergyReading
from src.domain.tariff import Tariff, TariffRate, Bill

class CostCalculator:
    """
    Calculates the cost of energy usage based on a specific tariff or schedule of tariffs.
    """
    
    def calculate_cost(self, series: EnergySeries, tariff_or_schedule: Union[Tariff, List[Tariff]]) -> Bill:
        """
        Calculates the bill for the given energy series and tariff(s).

        Args:
            series (EnergySeries): The energy data.
            tariff_or_schedule (Union[Tariff, List[Tariff]]): A single Tariff or a list of Tariffs (schedule).

        Returns:
            Bill: The calculated bill details.
        
        Raises:
            ValueError: If no applicable tariff is found for a reading.
        """
        if series.df.empty:
            return Bill(datetime.now(), datetime.now())

        period_start = series.df['timestamp'].min().to_pydatetime()
        period_end = series.df['timestamp'].max().to_pydatetime()
        
        bill = Bill(period_start=period_start, period_end=period_end)
        
        # Normalize input to a list
        if isinstance(tariff_or_schedule, Tariff):
            tariffs = [tariff_or_schedule]
        else:
            tariffs = tariff_or_schedule

        # Helper to find applicable tariff
        def get_tariff(ts: datetime) -> Tariff:
            for t in tariffs:
                # Check validity
                if t.valid_from and ts < t.valid_from:
                    continue
                if t.valid_to and ts > t.valid_to:
                    continue
                return t
            raise ValueError(f"No applicable tariff found for timestamp {ts}")

        # Calculate energy costs
        for _, row in series.df.iterrows():
            ts = row['timestamp'].to_pydatetime()  # UTC timestamp
            
            tariff = get_tariff(ts)
            
            # Convert UTC timestamp to tariff's local timezone
            # Tariff rates are defined in local time (e.g., Night starts at 23:00 Irish time)
            tz = pytz.timezone(tariff.timezone)
            local_ts = ts.astimezone(tz)
            
            t = local_ts.time()  # Extract time in local timezone
            weekday = local_ts.weekday()  # Weekday in local timezone
            
            # Import Cost
            import_kwh = row['import_energy']
            if import_kwh > 0:
                rate = self._find_rate(tariff.import_rates, t, weekday)
                if rate:
                    cost = import_kwh * rate.price_per_kwh
                    bill.total_import_cost += cost
                    bill.breakdown[rate.name] = bill.breakdown.get(rate.name, 0.0) + cost
            
            # Export Credit
            export_kwh = row['export_energy']
            if export_kwh > 0:
                rate = self._find_rate(tariff.export_rates, t, weekday)
                if rate:
                    credit = export_kwh * rate.price_per_kwh
                    bill.total_export_credit += credit
                    key = f"Export: {rate.name}"
                    bill.breakdown[key] = bill.breakdown.get(key, 0.0) + credit

        # Calculate standing charge
        # We need to iterate day by day to apply the correct standing charge
        # Or just iterate through the range
        current_date = period_start.date()
        end_date = period_end.date()
        
        while current_date <= end_date:
            # Find tariff for the start of this day (00:00)
            # Or should we check if tariff changes mid-day? Usually SC is daily.
            # Let's check at 12:00 of that day to be safe? Or 00:00?
            # Let's check 00:00.
            check_ts = datetime.combine(current_date, time(0, 0))
            
            # If check_ts is before the first tariff valid_from, we might fail.
            # But we are iterating through the SERIES range.
            # So there SHOULD be a tariff.
            try:
                tariff = get_tariff(check_ts)
                bill.standing_charge_cost += tariff.standing_charge
            except ValueError:
                # If no tariff found for this day (maybe gap in schedule?), skip or raise?
                # The test expects error if no tariff.
                # But maybe we should try checking end of day?
                # Let's re-raise for now.
                raise
            
            current_date += timedelta(days=1)
        
        # Net Cost
        bill.net_cost = bill.total_import_cost + bill.standing_charge_cost - bill.total_export_credit
        
        return bill

    def _find_rate(self, rates: List[TariffRate], t: time, weekday: int) -> Optional[TariffRate]:
        """
        Finds the applicable rate for a given time and day.
        """
        for rate in rates:
            if weekday in rate.days_of_week:
                # Handle overnight ranges (e.g. 23:00 to 08:00)
                if rate.start_time <= rate.end_time:
                    # Standard range (e.g. 08:00 to 23:00)
                    if rate.start_time <= t <= rate.end_time:
                        return rate
                else:
                    # Overnight range (e.g. 23:00 to 08:00)
                    # Time is valid if it's >= 23:00 OR <= 08:00
                    if t >= rate.start_time or t <= rate.end_time:
                        return rate
        return None
