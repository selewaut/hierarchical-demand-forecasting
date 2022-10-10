from abc import ABC, abstractmethod
import pandas as pd
from pathlib import Path


class TSDataset(ABC):
    """
    Abstrac  class that defines dataset interface for time series hierarchical forecasting
    """
    source_url = None
    name = 'abstract_dataset'

    @staticmethod
    @abstractmethod
    def load(directory: str, **kwargs)  -> pd.DataFrame:
        """
        Method used to load dataset data
        :param directory:
        :param kwargs:
        :return:
        """

    @staticmethod
    @abstractmethod
    def download_data(directory: str) -> None:
        """
        Downloads data set intor directory
        :param directory:
        :return:
        """


