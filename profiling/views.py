import json
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
import pandas as pd
from data_science.analysis import Analysis
import os
from data_science.utils import info_per_columns

@api_view()
@permission_classes([IsAuthenticated])
def get_bar_chart(request):
    try:
        file_name = request.query_params['filename']
        username = request.query_params['username']
        workspace = request.query_params['workspace']
        workspace_type = request.query_params['type']
    except:
        return Response({'message': "input error"},status=status.HTTP_400_BAD_REQUEST)

    current_path = os.getcwd()
    save_path = f'{current_path}/directory/{username}/{workspace_type}/{workspace}/{file_name}'
    dataframe = pd.read_csv(save_path)
    profiling = Analysis(dataframe=dataframe)
    result = json.loads(profiling.get_bar_chart_data())
    return Response(result,status=status.HTTP_200_OK)

@api_view()
@permission_classes([IsAuthenticated])
def get_data_describe(request):
    try:
        file_name = request.query_params['filename']
        username = request.query_params['username']
        workspace = request.query_params['workspace']
        workspace_type = request.query_params['type']
    except:
        return Response({'message': "input error"},status=status.HTTP_400_BAD_REQUEST)

    current_path = os.getcwd()
    save_path = f'{current_path}/directory/{username}/{workspace_type}/{workspace}/{file_name}'
    dataframe = pd.read_csv(save_path)
    profiling = Analysis(dataframe=dataframe)
    result = json.loads(profiling.get_data_describe())
    return Response(result,status=status.HTTP_200_OK)

@api_view()
@permission_classes([IsAuthenticated])
def get_info_per_column(request):
    try:
        file_name = request.query_params['filename']
        username = request.query_params['username']
        workspace = request.query_params['workspace']
        workspace_type = request.query_params['type']
    except:
        return Response({'message': "input error"},status=status.HTTP_400_BAD_REQUEST)

    current_path = os.getcwd()
    save_path = f'{current_path}/directory/{username}/{workspace_type}/{workspace}/{file_name}'
    dataframe = pd.read_csv(save_path)
    result = info_per_columns(dataframe)
    return Response(result,status=status.HTTP_200_OK)