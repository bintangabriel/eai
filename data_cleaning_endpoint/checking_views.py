import json
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import pandas as pd
from data_science.preprocess import Preprocess
from data_science.analysis import Analysis
import os

@api_view()
def null_check(request):
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
    preproceess = Preprocess(dataframe=dataframe)
    result = preproceess.data_null_check()
    return Response(result,status=status.HTTP_200_OK)

@api_view()
def duplication_check(request):
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
    preproceess = Preprocess(dataframe=dataframe)
    result = preproceess.data_duplication_check()
    return Response(result,status=status.HTTP_200_OK)

@api_view()
def outlier_check(request):
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
    preproceess = Preprocess(dataframe=dataframe)
    result = preproceess.data_outlier_check()
    return Response(result,status=status.HTTP_200_OK)

@api_view()
def get_boxplot(request):
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
    analysis = Analysis(dataframe=dataframe)
    result = json.loads(analysis.get_box_plot_data())
    return Response(result,status=status.HTTP_200_OK)