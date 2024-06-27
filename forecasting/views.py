import os
import secrets
from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework import status, permissions
import requests
from .models import MLModelForecasting
from .serializers import MLModelForecastingSerializer
from file.models import File
from workspace.models import Workspace
import numpy as np
import json
from knox.auth import TokenAuthentication

# accept request from user
# passing params to service
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def initiate_forecasting(request):
    try:
        model_name = request.data['modelname']
        file_name = request.data['filename']
        username = request.data['username']
        workspace = request.data['workspace']
        algorithm = request.data['algorithm']
        period = request.data['period']
        target = request.data['target']
        steps = request.data['steps']
        units = request.data['units']
        
    except:
        return Response({'message': "input error"},status=status.HTTP_400_BAD_REQUEST)
    
    # setup request to training service endpoint
    training_service_url = 'http://10.128.0.11:7000/train/forecasting/'
    current_path = os.getcwd()
    file_path = f'{current_path}/directory/{username}/forecasting/{workspace}/{file_name}'
    files = {'file': open(file_path, 'rb')}
    model_forecasting_metadata = {
            'model_name': model_name,
            'file_name' : file_name,
            'username' : username,
            'workspace' : workspace,
            'algorithm' : algorithm,
            'period' : period,
            'target' : target,
            'steps' : steps,
            'units' : units,
    }
    training_record = requests.post(training_service_url, data=model_forecasting_metadata, files=files)
    
    return Response(data=training_record.json(), status=status.HTTP_202_ACCEPTED)

def save_forecasting_model(request):
    # fetch request file & model metadata
    model_forecasting_metadata = request.POST.dict()
    files = request.FILES['file']

    # fetch model metadata
    model_name = model_forecasting_metadata['model_name']
    file_name = model_forecasting_metadata['file_name']
    username = model_forecasting_metadata['username']
    workspace = model_forecasting_metadata['workspace']
    algorithm = model_forecasting_metadata['algorithm']
    metrics_scores = model_forecasting_metadata['metrics_scores']
    period = model_forecasting_metadata['period']
    target = model_forecasting_metadata['target']
    steps = model_forecasting_metadata['steps']
    units = model_forecasting_metadata['units']
    
    workspace_fk = Workspace.objects.get(name=workspace, username=username, type='forecasting')
    payload = {
        'name' : model_name,
        'file_name' : file_name,
        'username': username,
        'workspace' : workspace_fk.id,
        'algorithm' : algorithm,
        'metrics_scores' : metrics_scores,
        'period' : period,
        'target' : target,
        'steps' : steps,
        'units' : units,
    }
    mlmodelforecasting_serializer = MLModelForecastingSerializer(data=payload)

    if mlmodelforecasting_serializer.is_valid():
        # configure save_path then save model to directory
        current_path = os.getcwd()
        save_path = f'{current_path}/directory/{username}/forecasting/{workspace}/{model_name}.pkl'
        with open(f'{save_path}', 'wb') as destination:
                for chunk in files.chunks():
                    destination.write(chunk)
        
        if model_forecasting_metadata['algorithm'] == 'LSTM':
            scaled_test_data = [[data] for data in json.loads(model_forecasting_metadata['scaled_test_data'])]
            scaled_test_data = np.array(scaled_test_data)
            print(scaled_test_data)
            np.savetxt(f'{current_path}/directory/{username}/forecasting/{workspace}/{model_name}_std.csv',
                       scaled_test_data,
                       delimiter=",",
                       fmt="%f")
        # save model to db
        mlmodelforecasting_serializer.save()

        return JsonResponse(mlmodelforecasting_serializer.data)

    return JsonResponse(mlmodelforecasting_serializer.errors)

@api_view()
@permission_classes([permissions.IsAuthenticated])
@authentication_classes([TokenAuthentication])
def list_forecasting_model(request):
    try:
        username = request.query_params['username']
        workspace = request.query_params['workspace']
    except:
        return Response({'message': "input error"},status=status.HTTP_400_BAD_REQUEST)

    mlmodels = MLModelForecasting.objects.filter(username=username, workspace__name=workspace, workspace__type='forecasting')
    mlmodelforecasting_serializer = MLModelForecastingSerializer(mlmodels, many=True)
    return Response(mlmodelforecasting_serializer.data, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def delete_forecasting_model(request):
    try:
        model_name = request.data['model_name']
        username = request.data['username']
        workspace = request.data['workspace']
        workspace_type = request.data['type']
    except:
        return Response({'message': "input error"},status=status.HTTP_400_BAD_REQUEST)
    
    try:
        mlmodel = MLModelForecasting.objects.get(name=model_name, 
            username=username,
            workspace__name=workspace,
            workspace__type=workspace_type,
        )
    except:
        return Response({'message': "data not found"}, status=status.HTTP_404_NOT_FOUND)
    
    current_path = os.getcwd()
    save_path = f'{current_path}/directory/{username}/{workspace_type}/{workspace}/{model_name}.pkl'
    os.remove(save_path)
    mlmodel.delete()
    return Response({'message': "deleted successfully"},status=status.HTTP_204_NO_CONTENT)
