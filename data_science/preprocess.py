import pandas as pd
import numpy as np
from collections import Counter
from typing import Dict, List, Tuple, Union, Optional, Literal
from pandas.core.frame import DataFrame
from pandas.core.series import Series
from data_science.core import DataScience
from imblearn.over_sampling import SMOTENC
from sklearn.preprocessing import LabelEncoder, MinMaxScaler, StandardScaler


class Preprocess(DataScience):

    def __init__(self, dataframe: DataFrame) -> None:
        super().__init__(dataframe)

    def data_null_check(self) -> Dict[str, int]:
        df = self.dataframe.copy()
        total_null_for_each_column = dict(df.isnull().sum())

        return total_null_for_each_column

    def data_null_handler(self, columns: List[str]=None) -> DataFrame:
        df = self.dataframe.copy()

        if columns != None:
            df.dropna(subset=columns, inplace=True)
        else:
            df.dropna(inplace=True)
            
        self.dataframe = df

        return df

    def data_duplication_check(self) -> int:
        df = self.dataframe.copy()
        total_duplicate = df.duplicated().sum()

        return total_duplicate

    def data_duplication_handler(self, columns: List[str]=None) -> DataFrame:
        df = self.dataframe.copy()

        if columns != None:
            df.drop_duplicates(subset=columns, inplace=True)
        else:
            df.drop_duplicates(inplace=True)

        self.dataframe = df

        return df

    def data_outlier_check(self) -> Dict[str, int]:
        """
        https://machinelearningmastery.com/how-to-use-statistics-to-identify-outliers-in-data/
        """
        df = self.dataframe.copy()
        total_outlier_for_each_column = dict()
        for col in df.columns:
            if df[col].dtype in ["int64", "float64"]:
                df_col_target = df[col]
                ul, ll = self._get_upper_lower_level(df_col_target)

                # get outliers only
                outliers = df_col_target[(df_col_target < ll) | (df_col_target > ul)]
                total_outlier_for_each_column[col] = len(outliers)

        return total_outlier_for_each_column

    def data_outlier_handler(self) -> DataFrame:
        df = self.dataframe.copy()

        all_outlier_rows_index = set()
        for col in df.columns:
            if df[col].dtype in ["int64", "float64"]:
                df_col_target = df[col]
                ul, ll = self._get_upper_lower_level(df_col_target)
                
                # exclude outliers from the data
                all_outlier_rows_index |= set(df_col_target[(df_col_target < ll) | (df_col_target > ul)].index)

        df = df.drop(list(all_outlier_rows_index), axis=0)
        self.dataframe = df

        return df

    def data_imbalance_handler(self, target_column: str) -> Optional[DataFrame]:
        """
        Making a synthetic data using SMOTE. `target_column` should contain binary categorical data.
        """

        df = self.dataframe.copy()
        le = LabelEncoder()

        x = df.drop(columns=target_column, axis=1)
        y = df[target_column]
        
        # process can not be continued if target column is non binary categorical data
        if len(y.unique()) > 2:
            return None

        x_columns = x.columns
        cat_features = []
        for idx in range(len(x_columns)):
            if x.iloc[:, idx].dtype == 'object':
                cat_features.append(idx)

        x = np.array(x)
        y = np.array(le.fit_transform(y))

        sm = SMOTENC(categorical_features=cat_features, random_state=42)
        x_oversampled, y_oversampled = sm.fit_resample(x, y)

        balanced_df = pd.DataFrame(data=x_oversampled, columns=x_columns)
        balanced_df[target_column] = y_oversampled

        return balanced_df

    def data_normalization_handler(
        self,
        target_columns: List[str],
        method: Literal['min-max', 'z-score'] = 'min-max'
    ) -> Optional[DataFrame]:
        """
        Normalize numeric data on `target_columns` only.
        `method` = `min-max` if MinMaxScaler is needed.
        `method` = `z-score` if StandardScaler is needed
        """

        df = self.dataframe.copy()
        df_sliced = df[target_columns]    

        # Check if the selected columns are for numerical data only
        for idx in range(len(df_sliced.columns)):
            if df_sliced.iloc[:, idx].dtype == 'object':
                return None   

        scalers = {
            'min-max': MinMaxScaler(),
            'z-score': StandardScaler()
        }
        scaler = scalers[method]

        df[target_columns] = scaler.fit_transform(df_sliced)
        self.dataframe = df

        return df

    @staticmethod
    def _get_upper_lower_level(df_col: Series) -> Tuple[float, float]:
        """
        This functions is used for handling outlier with IQR method
        """
        q1 = df_col.quantile(.25)
        q3 = df_col.quantile(.75)
        IQR = q3 - q1
        ll = q1 - (1.5*IQR)
        ul = q3 + (1.5*IQR)

        return ul, ll
                