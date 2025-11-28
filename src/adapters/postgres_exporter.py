from src.interfaces import ISQLGenerator
from src.domain.models import EnergySeries

class PostgresExporter(ISQLGenerator):
    def __init__(self, table_name: str = "readings"):
        self.table_name = table_name

    def generate_sql(self, series: EnergySeries) -> str:
        if not series.readings:
            return ""
        
        values = []
        for r in series.readings:
            # Format timestamp as YYYY-MM-DD HH:MM:SS
            ts_str = r.timestamp.strftime('%Y-%m-%d %H:%M:%S')
            values.append(f"('{ts_str}', {r.import_energy}, {r.export_energy})")
        
        values_str = ",\n".join(values)
        return f"INSERT INTO {self.table_name} (timestamp, import_kwh, export_kwh) VALUES\n{values_str};"
