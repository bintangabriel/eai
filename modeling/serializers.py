from rest_framework import serializers
from .models import ModelTrainingRecord, MLModel, ModelKey, ObsegModel

class ModelTrainingRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = ModelTrainingRecord
        fields = ('id', 'status', 'created_time', 'updated_time')

class MLModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = MLModel
        fields = ('id', 'name', 'file_name', 'username', 'workspace', 
                  'method', 'algorithm', 'metrics_scores', 'feature', 
                  'target', 'n_cluster','created_time', 'updated_time')

class ModelKeySerializer(serializers.ModelSerializer):
    class Meta:
        model = ModelKey
        fields = ('model', 'key')

class ObsegModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = ObsegModel
        fields = ('id', 'name', 'file_name', 'username', 'workspace', 
                  'method', 'algorithm', 'metrics_scores','created_time', 'updated_time')