from abc import ABC, abstractmethod
from typing import List
from src.domain.models import EnergySeries, EnergyReading

class IDataSource(ABC):
    """
    Interface for data ingestion sources.
    """
    @abstractmethod
    def parse(self, source: str) -> EnergySeries:
        """
        Parses the input source and returns an EnergySeries.

        Args:
            source (str): The path or identifier of the data source (e.g., file path).

        Returns:
            EnergySeries: The parsed energy data series.
        """
        pass

class ISQLGenerator(ABC):
    """
    Interface for generating SQL statements from energy data.
    """
    @abstractmethod
    def generate_sql(self, series: EnergySeries) -> str:
        """
        Generates SQL INSERT statements for the given energy series.

        Args:
            series (EnergySeries): The energy data to generate SQL for.

        Returns:
            str: A string containing the SQL statements.
        """
        pass

class IGraphGenerator(ABC):
    """
    Interface for generating visualizations from energy data.
    """
    @abstractmethod
    def generate_graphs(self, series: EnergySeries, output_dir: str, output_file: str = None, 
                       smoothing_method: str = None, smoothing_param: float = None) -> List[str]:
        """
        Generates graphs and saves them to the specified directory.

        Args:
            series (EnergySeries): The energy data to visualize.
            output_dir (str): The directory to save the generated graphs.
            output_file (str, optional): The filename for the output graph. Defaults to None.
            smoothing_method (str, optional): The smoothing method to apply ('rolling' or 'spline'). Defaults to None.
            smoothing_param (float, optional): Parameter for the smoothing method (e.g., window size). Defaults to None.

        Returns:
            List[str]: A list of file paths to the generated graphs.
        """
        pass
