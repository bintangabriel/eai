from rest_framework import serializers
from .models import ModelForecastingTrainingRecord, MLModelForecasting

class ModelForecastingTrainingRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = ModelForecastingTrainingRecord
        fields = ('id', 'status', 'created_time', 'updated_time')

class MLModelForecastingSerializer(serializers.ModelSerializer):
    class Meta:
        model = MLModelForecasting
        fields = ('id', 'name', 'file_name', 'username', 'workspace', 'algorithm', 'metrics_scores', 'period', 'target', 'steps', 'units', 'created_time', 'updated_time')
