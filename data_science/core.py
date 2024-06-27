import pandas as pd
from typing import Tuple, Dict
from pandas.core.frame import DataFrame


class DataScience:
    
    dataframe = None

    def __init__(self, dataframe: DataFrame) -> None:
        self.dataframe = dataframe

    def get_dataframe_shape(self) -> Tuple[int, int]:
        return self.dataframe.shape

    def get_all_column_type(self) -> Dict[str, str]:
        column_data_type = self.dataframe.dtypes
        key = column_data_type.index.to_list()
        value = ['Numerical' if v in ['int64', 'float64'] else 'Non-Numerical' for v in map(str,list(column_data_type.values))]

        return dict(zip(key, value))
