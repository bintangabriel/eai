import json
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import pandas as pd
from file.serializers import FileSerializer
from data_science.preprocess import Preprocess
import os
import string
import random
from data_science.utils import convert_data_type
from workspace.models import Workspace

@api_view(['POST'])
def cleaning_handler(request):
    try:
        file_name = request.data['filename']
        username = request.data['username']
        workspace = request.data['workspace']
        workspace_type = request.data['type']
    except:
        return Response({'message': "input error"},status=status.HTTP_400_BAD_REQUEST)
    
    current_path = os.getcwd()
    save_path = f'{current_path}/directory/{username}/{workspace_type}/{workspace}/{file_name}'
    dataframe = pd.read_csv(save_path)
    preprocess = Preprocess(dataframe=dataframe)
    
    # handle missing data
    if request.data['missing'] == '1':
        if request.data['columns_missing'] != '':
            col = request.data['columns_missing'].split(",")
            preprocess.data_null_handler(col)
        else:
            preprocess.data_null_handler()

    # handle duplication
    if request.data['duplication'] == '1':
        if request.data['columns_duplication'] != '':
            col = request.data['columns_duplication'].split(",")
            preprocess.data_duplication_handler(col)
        else:
            preprocess.data_duplication_handler()

    # handle outlier
    if request.data['outlier'] == '1':
        preprocess.data_outlier_handler()

    # handle converting data
    if request.data['convert'] == '1':
        columns = request.data['columns_convert'].split(",")
        target = request.data['target_type_convert']
        for column in columns:
            convert_data_type(df=preprocess.dataframe, column=column, data_type_target=target)

    # handle normalization
    if request.data['normalize'] == '1':
        target_columns = request.data['columns_normalize'].split(",")
        method = request.data['method_normalize']
        preprocess.data_normalization_handler(target_columns=target_columns,method=method)

    # handle oversampling
    if request.data['oversampling'] == '1':
        target_columns = request.data['columns_oversampling']
        preprocess.data_imbalance_handler(target_column=target_columns)

    # generate new file name
    new_file_name = generate_file_name(file_name)
    
    # save cleaned dataset to csv
    save_path = f'{current_path}/directory/{username}/{workspace_type}/{workspace}/{new_file_name}'    
    if os.path.isfile(save_path):
        return Response({'errcode': "input error", 'message':"file name must unique"},status=status.HTTP_400_BAD_REQUEST)
    preprocess.dataframe.to_csv(save_path)

    # create new file model with serializer
    file_size = round(os.path.getsize(save_path)/(1024 * 1024), 2)

    # check and collect columns type
    columns_type = preprocess.get_all_column_type()
    numeric_type = []
    non_numeric_type = []
    for k,v in columns_type.items():
        if v in ['Numerical']:
            numeric_type.append(k)
        else:
            non_numeric_type.append(k)
    numeric = ''
    non_numeric = ''
    if not len(numeric_type) == 0:
        numeric = ','.join(numeric_type)
    if not len(non_numeric_type) == 0:
        non_numeric_type = ','.join(non_numeric_type)

    workspace_fk = Workspace.objects.get(name=workspace, username=username, type=workspace_type)
    payload = {
            'file' : new_file_name,
            'size': file_size,
            'username' : username,
            'workspace' : workspace_fk.id,
            'numeric' : numeric,
            'non_numeric' : non_numeric,
        }
    file_serializer = FileSerializer(data=payload)   
    if not file_serializer.is_valid():
        os.remove(save_path)
        return Response(file_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # save file model to database
    file_serializer.save()

    return Response(json.loads(preprocess.dataframe.head(10).to_json()), status=status.HTTP_200_OK)

def generate_file_name(file_name):
    file, ext = os.path.splitext(file_name)
    new_file_name = file + "_" + random_string() + ext
    return new_file_name

def random_string(length=4):
    return ''.join(random.choice(string.ascii_letters) for _ in range(length))