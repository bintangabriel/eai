from pyexpat import model
from rest_framework import serializers
from .models import File

class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = ('file', 'size', 'username', 'workspace', 'numeric', 'non_numeric', 'created_time', 'updated_time')


class FileObjectSegmentationSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = ('file', 'size', 'username', 'workspace', 'created_time', 'updated_time')