import os
import joblib
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.response import Response
from rest_framework import status, permissions
import numpy as np
from .models import MLModel, ObsegModel
from knox.auth import TokenAuthentication
import requests
from django.http import JsonResponse
from utils.ssh import *
from dotenv import load_dotenv

load_dotenv()

@api_view(['GET', 'POST'])

@authentication_classes([TokenAuthentication])
@permission_classes([permissions.IsAuthenticated])
def predict_model(request):
    try:
        workspace_type = request.query_params['type']
        model_name = request.query_params['modelname']
        features = request.query_params.getlist('feature', '')
        username = request.query_params['username']
        workspace = request.query_params['workspace']
    except:
        return Response({'message': "input error"},status=status.HTTP_400_BAD_REQUEST)
    
    if (workspace_type == 'object_segmentation'): 
        print('username: ', request.query_params['username'])
        print('workspace: ', request.query_params['workspace'])
        file = request.FILES['file']
        print(f"file: {file}")
        files = {'file': file}
        obseg_model = ObsegModel.objects.get(
            name=model_name,
            username=username,
            workspace__name=workspace, 
            workspace__type=workspace_type
        )
        model_metadata = {
            'model_name': model_name,
            'type': workspace_type,
            'username': username,
            'workspace': workspace,
            'model_type': obseg_model.method
        }
        
        # predict_service_url = 'http://127.0.0.1:7000/inference/'
        ip_modeling = os.environ.get('MODELING_IP')
        port_modeling = os.environ.get('MODELING_PORT')

        predict_service_url = f'http://{ip_modeling}:{port_modeling}/inference/'
        # res = requests.post(predict_service_url, data=model_metadata, files=files)
        # data = res.json()
        # image = data['image']

        # Using Dgx
        curl_command = generate_curl_command(predict_service_url, model_metadata, file)
        res = tunnel_modeling_dgx(curl_command, file, True)
        print('res: ', res)
        return JsonResponse({"image": res})
    else:
        current_path = os.getcwd()
        model_path = f'{current_path}/directory/{username}/{workspace_type}/{workspace}/{model_name}'
        features_int = [float(feature) for feature in features]
        model = joblib.load(model_path)
        predict = model.predict([features_int])

        try:
            mlmodel = MLModel.objects.get(name=model_name, 
                                        username=username, 
                                        workspace__name=workspace, 
                                        workspace__type=workspace_type)
        except:
            return Response({'message': "data not found"}, 
                        status=status.HTTP_404_NOT_FOUND)
    
        if mlmodel.algorithm == 'LINEAR':
            return Response({'result': predict[0][0]}, status=status.HTTP_200_OK)
        
        return Response({'result': predict[0]}, status=status.HTTP_200_OK)
