import json
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import ModelForecastingTrainingRecord
from .serializers import ModelForecastingTrainingRecordSerializer

def create_forecasting_training_record(request):
    payload = json.loads(request.body)
    modelforecastingtrainingrecord_serializer = ModelForecastingTrainingRecordSerializer(data=payload)
    if modelforecastingtrainingrecord_serializer.is_valid():
        modelforecastingtrainingrecord_serializer.save()
        return JsonResponse(modelforecastingtrainingrecord_serializer.data)
    
    return JsonResponse(modelforecastingtrainingrecord_serializer.errors)

def update_forecasting_training_record(request):
    payload = json.loads(request.body)
    training_record = ModelForecastingTrainingRecord.objects.get(id=payload['id'])
    modelforecastingtrainingrecord_serializer = ModelForecastingTrainingRecordSerializer(training_record,data=payload)
    if modelforecastingtrainingrecord_serializer.is_valid():
        modelforecastingtrainingrecord_serializer.save()
        return JsonResponse(modelforecastingtrainingrecord_serializer.data)
    
    return JsonResponse(modelforecastingtrainingrecord_serializer.errors)

@api_view()
@permission_classes([permissions.IsAuthenticated])
def get_forecasting_training_record(request):
    try:
        training_record = ModelForecastingTrainingRecord.objects.get(id=request.query_params['id'])
    except:
        return Response({'message': "data not found"}, status=status.HTTP_404_NOT_FOUND)
    trainingrecord_serializer = ModelForecastingTrainingRecordSerializer(training_record)
    return Response(trainingrecord_serializer.data, status=status.HTTP_200_OK)