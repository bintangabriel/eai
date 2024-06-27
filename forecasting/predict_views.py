import os
import joblib
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import MLModelForecasting
import numpy as np
import pandas as pd
import json
from statsmodels.tsa.arima.model import ARIMA
from sklearn.preprocessing import MinMaxScaler
from keras.models import Sequential
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error, r2_score
from pandas.core.frame import DataFrame
import numpy as np
from typing import Optional, Any, Tuple


class LumbaLSTM:
    model: Sequential
    scaler: MinMaxScaler
    train_column_name: str
    n_steps: int
    datetime_column_name : str

    def __init__(self, dataframe: DataFrame) -> None:
        self.dataframe = dataframe
    
    def get_model(self) -> Optional[Sequential]:
        try:
            return self.model
        except AttributeError:
            return None
        
    def predict(self, n_week: int) -> Tuple[Any, Any, Any]:
        """Forecast for the n weeks ahead"""

        forecast_data = self.dataframe[self.train_column_name].values.tolist()
        lstm_model = self.get_model()
        for _ in range(n_week):
            forecast_input = self.scaled_test_data[-self.n_steps:]
            forecast_input = forecast_input.reshape((1, self.n_steps, 1))
            forecast = lstm_model.predict(forecast_input)
            forecast_data.append(self.scaler.inverse_transform(forecast)[0][0])
            self.scaled_test_data = np.append(self.scaled_test_data, forecast)

        # calculate the upper and lower bounds for the forecasted sales data
        upper_bound = np.array(forecast_data) * 1.1
        lower_bound = np.array(forecast_data) * 0.9

        df_forecast_data = pd.DataFrame({
            self.datetime_column_name: range(self.dataframe[self.datetime_column_name].min(), self.dataframe[self.datetime_column_name].max() + n_week + 1),
            self.train_column_name: forecast_data
        })
        df_upper_bound = pd.DataFrame({
            self.datetime_column_name: range(self.dataframe[self.datetime_column_name].min(), self.dataframe[self.datetime_column_name].max() + n_week + 1),
            f'upper_bound_{self.train_column_name}': upper_bound
        })
        df_lower_bound = pd.DataFrame({
            self.datetime_column_name: range(self.dataframe[self.datetime_column_name].min(), self.dataframe[self.datetime_column_name].max() + n_week + 1),
            f'lower_bound_{self.train_column_name}': lower_bound
        })

        df_forecast_data[self.train_column_name] = df_forecast_data[self.train_column_name].map(lambda x: '%.2f' % x)
        df_upper_bound[f'upper_bound_{self.train_column_name}'] = df_upper_bound[f'upper_bound_{self.train_column_name}'].map(lambda x: '%.2f' % x)
        df_lower_bound[f'lower_bound_{self.train_column_name}'] = df_lower_bound[f'lower_bound_{self.train_column_name}'].map(lambda x: '%.2f' % x)

        return df_forecast_data, df_upper_bound, df_lower_bound

class LumbaARIMA:
    model: ARIMA
    train_column_name: str
    datetime_column_name : str

    def __init__(self, dataframe: DataFrame) -> None:
        self.dataframe = dataframe
        
    def get_model(self) -> Optional[ARIMA]:
        try:
            return self.model
        except AttributeError:
            return None

    def predict(self, n_week: int, week_column_name: str) -> Tuple[Any, Any, Any]:
        """Forecast for the n weeks ahead"""

        # use the trained ARIMA model to make forecasts for the next 10 weeks
        arima_forecast_data = self.dataframe.copy()
        arima_forecast_data[week_column_name] = pd.to_numeric(arima_forecast_data[week_column_name], downcast="integer")
        arima_forecast_data[self.train_column_name] = pd.to_numeric(arima_forecast_data[self.train_column_name], downcast="integer")
        arima_forecast = self.model.forecast(steps=n_week)

        for i, forecast_value in enumerate(arima_forecast):
            week_num = len(self.dataframe) + i + 1
            new = [week_num, forecast_value]
            arima_forecast_data = arima_forecast_data.append(pd.Series(new, index=arima_forecast_data.columns[:len(new)]), ignore_index=True)

        # calculate the upper and lower bounds for the forecasted sales data
        upper_bound = np.array(arima_forecast_data[self.train_column_name]) * 1.1
        lower_bound = np.array(arima_forecast_data[self.train_column_name]) * 0.9

        df_arima_forecast_data = pd.DataFrame({
            self.datetime_column_name: range(self.dataframe[self.datetime_column_name].min(), self.dataframe[self.datetime_column_name].max() + n_week + 1),
            self.train_column_name: arima_forecast_data[self.train_column_name]
        })
        df_upper_bound = pd.DataFrame({
            self.datetime_column_name: range(self.dataframe[self.datetime_column_name].min(), self.dataframe[self.datetime_column_name].max() + n_week + 1),
            f'upper_bound_{self.train_column_name}': upper_bound
        })
        df_lower_bound = pd.DataFrame({
            self.datetime_column_name: range(self.dataframe[self.datetime_column_name].min(), self.dataframe[self.datetime_column_name].max() + n_week + 1),
            f'lower_bound_{self.train_column_name}': lower_bound
        })

        df_arima_forecast_data[self.train_column_name] = df_arima_forecast_data[self.train_column_name].map(lambda x: '%.2f' % x)
        df_upper_bound[f'upper_bound_{self.train_column_name}'] = df_upper_bound[f'upper_bound_{self.train_column_name}'].map(lambda x: '%.2f' % x)
        df_lower_bound[f'lower_bound_{self.train_column_name}'] = df_lower_bound[f'lower_bound_{self.train_column_name}'].map(lambda x: '%.2f' % x)
        
        return df_arima_forecast_data, df_upper_bound, df_lower_bound

@api_view()
@permission_classes([permissions.IsAuthenticated])
def forecast(request):
    try:
        model_id = request.query_params['id']
        username = request.query_params['username']
        workspace = request.query_params['workspace']
    except:
        return Response({'message': "input error"},status=status.HTTP_400_BAD_REQUEST)

    try:
        forecast_model = MLModelForecasting.objects.get(id=model_id)
    except:
        return Response({'message': "model not found"},status=status.HTTP_404_NOT_FOUND)
    
    current_path = os.getcwd()
    model_path = f'{current_path}/directory/{username}/forecasting/{workspace}/{forecast_model.name}.pkl'

    # read data to be forecasted
    save_path = f'{current_path}/directory/{username}/forecasting/{workspace}/{forecast_model.file_name}'
    forecast_data = pd.read_csv(save_path)
    
    # execute prediction
    if forecast_model.algorithm == 'ARIMA':
        model = joblib.load(model_path)
        arima_forecast = LumbaARIMA(dataframe=forecast_data[['week','qty']])

        arima_forecast.model = model['model']
        arima_forecast.train_column_name = forecast_model.target
        arima_forecast.datetime_column_name = forecast_model.units
        
        result = arima_forecast.predict(n_week=int(forecast_model.period), 
                                        week_column_name=forecast_model.units)
        return Response({'data': result[0],
                         'upper_bound': result[1],
                         'lower_bound': result[2]}, status=status.HTTP_200_OK)
    
    if forecast_model.algorithm == 'LSTM':
        # scaler = MinMaxScaler()
        model = joblib.load(model_path)
        lstm_model = LumbaLSTM(dataframe=forecast_data)
        lstm_model.model = model['model']
        lstm_model.scaler = model['scaler']
        lstm_model.train_column_name = forecast_model.target
        lstm_model.scaled_test_data = model['scaled_test_data']
        lstm_model.n_steps = int(forecast_model.steps)
        lstm_model.datetime_column_name = forecast_model.units
    
        # predict with lstm
        result = lstm_model.predict(int(forecast_model.period))

        return Response({'data': result[0],
                         'upper_bound': result[1],
                         'lower_bound': result[2]}, status=status.HTTP_200_OK)
