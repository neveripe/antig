from src.interfaces import ISQLGenerator
from src.domain.models import EnergySeries

class PostgresExporter(ISQLGenerator):
    """
    Generates PostgreSQL INSERT statements for energy data.

    Attributes:
        table_name (str): The name of the database table to insert into.
    """
    def __init__(self, table_name: str = "readings"):
        """
        Initializes the PostgresExporter.

        Args:
            table_name (str, optional): The target table name. Defaults to "readings".
        """
        self.table_name = table_name

    def generate_sql(self, series: EnergySeries) -> str:
        """
        Generates a SQL INSERT statement for all readings in the series.

        Args:
            series (EnergySeries): The energy data series.

        Returns:
            str: A string containing the SQL INSERT statement. Returns empty string if series is empty.
        """
        if not series.readings:
            return ""
        
        values = []
        for r in series.readings:
            # Format timestamp as YYYY-MM-DD HH:MM:SS
            ts_str = r.timestamp.strftime('%Y-%m-%d %H:%M:%S')
            values.append(f"('{ts_str}', {r.import_energy}, {r.export_energy})")
        
        values_str = ",\n".join(values)
        return f"INSERT INTO {self.table_name} (timestamp, import_kwh, export_kwh) VALUES\n{values_str};"
