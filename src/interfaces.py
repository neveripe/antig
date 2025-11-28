from abc import ABC, abstractmethod
from typing import List
from src.domain.models import EnergySeries, EnergyReading

class IDataSource(ABC):
    @abstractmethod
    def parse(self, source: str) -> EnergySeries:
        pass

class ISQLGenerator(ABC):
    @abstractmethod
    def generate_sql(self, series: EnergySeries) -> str:
        pass

class IGraphGenerator(ABC):
    @abstractmethod
    def generate_graphs(self, series: EnergySeries, output_dir: str, output_file: str = None, 
                       smoothing_method: str = None, smoothing_param: float = None) -> List[str]:
        """
        Generates graphs and returns list of file paths.
        """
        pass
