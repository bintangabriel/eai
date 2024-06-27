import os
import joblib
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status, permissions
import numpy as np
from .models import MLModel, ModelKey
from .serializers import MLModelSerializer

@api_view()
def model_predict_api(request, idmodel):
    # check if user passed modelkey
    try:
        modelkey = request.headers['modelkey']
    except:
        return Response({'message': "input error"},status=status.HTTP_400_BAD_REQUEST)

    # check if user modelkey matched
    try:
        ModelKey.objects.get(model__pk=idmodel, key=modelkey)
    except:
        return Response({'message': "key not match"},status=status.HTTP_401_UNAUTHORIZED)

    try:
        feature = int(request.query_params['feature'])
        username = request.query_params['username']
        workspace = request.query_params['workspace']
    except:
        return Response({'message': "input error"},status=status.HTTP_400_BAD_REQUEST)

    try:
        mlmodel = MLModel.objects.get(id=idmodel)
    except:
        return Response({'message': "data not found"}, status=status.HTTP_404_NOT_FOUND)
    
    current_path = os.getcwd()
    model_path = f'{current_path}/directory/{username}/predicting/{workspace}/{mlmodel.name}'
    try:
        model = joblib.load(model_path)
    except:
        return Response({'message': "data not found"}, status=status.HTTP_404_NOT_FOUND)
    
    predict = model.predict(np.array([feature]).reshape(-1,1))
 
    return Response({'name': predict[0][0], 'feature': mlmodel.feature}, status=status.HTTP_200_OK)

@api_view()
def get_model_detail(request, idmodel):
    # check if user passed modelkey
    try:
        modelkey = request.headers['modelkey']
    except:
        return Response({'message': "key not passed"},status=status.HTTP_400_BAD_REQUEST)

    # check if user modelkey matched
    try:
        ModelKey.objects.get(model__pk=idmodel, key=modelkey)
    except:
        return Response({'message': "key not match"},status=status.HTTP_401_UNAUTHORIZED)
        
    try:
        mlmodel = MLModel.objects.get(id=idmodel)
    except:
        return Response({'message': "data not found"}, status=status.HTTP_404_NOT_FOUND)
    mlmodel_serializer = MLModelSerializer(mlmodel)
    return Response(mlmodel_serializer.data, status=status.HTTP_200_OK)