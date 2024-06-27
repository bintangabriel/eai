import io
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from PIL import Image
from workspace.models import *
from rest_framework.response import Response
from rest_framework import status
import redis
from .serializers import *
from eai.app_redis import Redis
from zipfile import ZipFile
from io import BytesIO
import json
import zipfile

class UploadFolder(APIView):
    def post(self, request, *args, **kwargs):
        try:
            zip_file = request.FILES['file']

            username = request.data['username']
            workspace = request.data['workspace']

            if zip_file.name.endswith('.zip'):

                images = []
                mask = []
                # Validate the dataset uploaded
                with zipfile.ZipFile(zip_file, 'r') as z:
                    for img_filename in z.namelist():
                        # Skip files starting with ._ and files in __MACOSX directory
                        if (not ('__MACOSX' in img_filename)) and (not (img_filename.startswith('._'))):
                            print(img_filename)
                            if img_filename.endswith(('.jpg', '.jpeg', '.png')) and 'images/' in img_filename:
                                images.append(img_filename)
                            elif img_filename.endswith(('.jpg', '.jpeg', '.png')) and 'mask/' in img_filename:
                                mask.append(img_filename)
                if len(images) == 0 or len(mask) == 0:
                    raise CustomError('Dataset not valid', 400)

                zip_file.seek(0)

                valid_workspace = Workspace.objects.get(name=workspace,username=username)


                payload = {
                    'file' : zip_file.name,
                    'size' : round(request.data['file'].size/(1024 * 1024), 2),
                    'username' : username,
                    'workspace' : valid_workspace.id
                }
                file_serializer = FileObjectSegmentationSerializer(data=payload)
                r = Redis.get()
                r.set(username + "_" + workspace + "_" + zip_file.name, zip_file.read())

                if file_serializer.is_valid():
                    file_serializer.save()
                    return Response(file_serializer.data, status=status.HTTP_201_CREATED)
                else:
                    return Response(file_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except CustomError as e: 
            return Response({'message': "dataset error", "error" : str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(str(e))
            return Response({'message': "input error", "error" : str(e)}, status=status.HTTP_400_BAD_REQUEST)
            
        return Response({'message' : 'success'})
    
    '''
    This endpoint return rows of data with pagination, cannot return dataframe directly
    because JSON cant handle NaN value
    '''
    def get(self, request, *args, **kwargs):
        try:
            username = request.query_params['username']
            workspace = request.query_params['workspace']
        except:
            return Response({'message': "input error"},status=status.HTTP_400_BAD_REQUEST)

        r = Redis.get()
        keys = r.keys(username + "_" + workspace + "_")
        for key in keys:
            val =  r.get(key)
        print(keys)
        # files = File.objects.filter(username=username, workspace__name=workspace)
        # files_serializer = FileSerializer(files, many=True)
        # return Response(files_serializer.data, status=status.HTTP_200_OK)


def get_labels(self, request):
    try:
        username = request.query_params['username']
        workspace = request.query_params['workspace']
        dataset_name = request.query_params['dataset_name']

        r = Redis.get()
        dataset = r.get(f'{username}_{workspace}_{dataset_name}')

        zip_file = ZipFile(BytesIO(dataset), 'r')


        label = []
        for filename in zip_file.namelist():
            if filename.startswith('train/') and filename.endswith('.json'):
                with zip_file.open(filename, 'r') as file:
                    file_content = file.read().decode('utf-8')

                    json_data = json.loads(file_content)

                    categories = json_data['categories']

                    for category in categories:
                        label.append(category['name'])
                    
        return Response({ 'labels': label }, status=status.HTTP_200_OK)
    except:
        return Response({ 'message': 'Error' })
    


class CustomError(Exception):
    def __init__(self, message, status_code):
        super().__init__(message)
        self.status_code = status_code