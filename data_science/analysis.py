from typing import List
from pandas.core.frame import DataFrame
from data_science.core import DataScience
import json

class Analysis(DataScience):

    def __init__(self, dataframe: DataFrame) -> None:
        super().__init__(dataframe)

    def get_data_describe(self, columns: List[str]=None) -> str:
        """
        Generate descriptive statistics.
        """

        df = self.dataframe.copy()

        describe_json: str 
        if columns != None:
            tmp_dict = df.describe().to_dict()
            dict_for_describe = {col: tmp_dict[col] for col in columns}
            describe_json = json.dumps(dict_for_describe) 
        else:
            describe_json = df.describe().to_json()
        
        return describe_json

    def get_pie_chart_data(self) -> str:
        """
        Return value counts of each category for each column.
        Excludes any integer or float data.
        """

        df = self.dataframe.copy()
        
        value_count_for_each_column = {}
        for col in df.columns:
            if df[col].dtype == 'O':
                tmp_dict = df[col].value_counts().to_dict()
                value_count_for_each_column[col] = tmp_dict
        
        return json.dumps(value_count_for_each_column)

    def get_bar_chart_data(self) -> str:
        """
        Return each column names with labels and values.
        """

        df = self.dataframe.copy()

        value_count_for_each_column = {}
        for col in df.columns:
            tmp_dict = df[col].value_counts().to_dict()
            labels = list(tmp_dict.keys())
            data = list(tmp_dict.values())
            value_count_for_each_column[col] = {'labels': labels, 'data': data}
        
        return json.dumps(value_count_for_each_column)

    def get_line_chart_data(self, x:str, y:str) -> str:
        """
        `x` and `y` are column name. 

        `df[x]` can be numerical or categorical.
        `df[y]` should be numerical only.

        The data uses aggregate sum by default. Returns labels and data. 
        """

        df = self.dataframe.copy()

        response_data = {}
        if df[x].dtype in ['int64', 'float64', 'O'] and df[y].dtype in ['int64', 'float64']:
            df_agg_sum = df.groupby(by=x)[y].sum()
            df_agg_sum.sort_index(inplace=True)
            df_agg_sum_dict = df_agg_sum.to_dict()

            response_data = {
                'labels': list(df_agg_sum_dict.keys()),
                'data': list(df_agg_sum_dict.values()),
            }

        return json.dumps(response_data)

    def get_scatter_plot_data(self, column1:str, column2:str) -> str:
        """
        return int or float data from two selected columns.
        """

        df = self.dataframe.copy()

        data1 = []
        data2 = []
        response_data = {}
        if df[column1].dtype in ["int64", "float64"] and df[column2].dtype in ["int64", "float64"]:
            data1 = df[column1].to_list()
            data2 = df[column2].to_list()
            response_data['data'] = {
                'column1_data': data1,
                'column2_data': data2
            }
        else:
            response_data['data'] = {}

        return json.dumps(response_data)

    def get_box_plot_data(self) -> str:
        """
        Return Min and max whisker line, IQR, Median, 2nd and 3rd Quartile.
        """
        
        df = self.dataframe.copy()

        response_data = {}
        for col in df.columns:
            if df[col].dtype in ['int64', 'float64']:
                q1 = df[col].quantile(.25)
                q3 = df[col].quantile(.75)
                IQR = q3 - q1
                min_whisker = q1 - (1.5*IQR)
                max_whisker = q3 + (1.5*IQR)
                median = df[col].median()
                mean = df[col].mean()

                response_data[col] = {
                    'q1': q1,
                    'q3': q3,
                    'iqr': IQR,
                    'min_whisker': min_whisker,
                    'max_whisker': max_whisker,
                    'median': median,
                    'mean': mean
                }

        return json.dumps({
            'labels': list(response_data.keys()),
            'data': list(response_data.values())
        })
