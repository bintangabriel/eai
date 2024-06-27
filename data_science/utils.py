from typing import Optional, Literal, Dict, Any
from pandas import DataFrame


def convert_data_type(
    df: DataFrame,
    column: str,
    data_type_target: Literal['int', 'float', 'object']
) -> Optional[DataFrame]:
    """Convert a column in dataframe to a specific type."""
    
    try:
        df[column] = df[column].astype(data_type_target)
        return df
    except ValueError:
        return None

def info_per_columns(df: DataFrame) -> Dict[str, Any]:
    """Utils function to return information of columns."""

    response = {}
    cols = df.columns
    idx = 0
    for col in cols:
        data = df[col].describe()

        if df[col].dtype == 'object':
            value_counts_percentage = df[col].value_counts(normalize=True).mul(100).round(1).to_dict()

            response[idx] = {
                'column_name': col,
                'column_type': str(df[col].dtype),
                'total_data_valid': len(df[col]) - df[col].isna().sum(),
                'total_data_invalid': df[col].isna().sum(),
                'unique': data['unique'],
                'mode': data['top'],
                'unique_values': value_counts_percentage,
            }

        elif df[col].dtype in ['int64', 'float64']:
            response[idx] = {
                'column_name': col,
                'column_type': str(df[col].dtype),
                'total_data_valid': len(df[col]) - df[col].isna().sum(),
                'total_data_invalid': df[col].isna().sum(),
                'mean': data['mean'],
                'median': df[col].median(),
                'mode': df[col].mode()[0],
                'q1': data['25%'],
                'q3': data['75%'],
                'min': data['min'],
                'max': data['max'],
                'std': data['std'],
                'bar_chart': df[col].value_counts().to_dict(),
            }

        else:
            response[idx] = {}

        idx += 1

    return response
