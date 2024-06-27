import json
import os
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status, permissions

from data_science.core import DataScience
from .serializers import FileSerializer
from .models import File
import pandas as pd
from drf_yasg.utils import swagger_auto_schema
from workspace.models import Workspace
from knox.auth import TokenAuthentication

from eai.app_redis import Redis

class FileView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    authentication_classes = (TokenAuthentication, )
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(request_body=FileSerializer)
    def post(self, request, *args, **kwargs):
        try:
            file_name = request.data['file'].name
            username = request.data['username']
            workspace = request.data['workspace']
            workspace_type = request.data['type']
        except:
            return Response({'message': "input error"},status=status.HTTP_400_BAD_REQUEST)

        # count file size
        file_size = round(request.data['file'].size/(1024 * 1024), 2)

        # check and collect columns type
        df = pd.read_csv(request.data['file'].file)
        ds = DataScience(dataframe=df)
        columns_type = ds.get_all_column_type()
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
            'file' : file_name,
            'size' : file_size,
            'username' : username,
            'workspace' : workspace_fk.id,
            'numeric' : numeric,
            'non_numeric' : non_numeric,
        }
        file_serializer = FileSerializer(data=payload)
       
        if file_serializer.is_valid():
            # configure save_path
            current_path = os.getcwd()
            save_path = f'{current_path}/directory/{username}/{workspace_type}/{workspace}/{file_name}'
            
            # save file to directory
            if os.path.isfile(save_path):
                return Response({'errcode': "input error", 'message':"file name must unique"},status=status.HTTP_400_BAD_REQUEST)
            
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            
            with open(f'{save_path}', 'wb') as destination:
                for chunk in request.data['file'].chunks():
                    destination.write(chunk)
            file_serializer.save()
            response_data = {k:v for k,v in file_serializer.data.items() if k not in ["numeric", "non_numeric"]}
            return Response(response_data, status=status.HTTP_201_CREATED)

        else:
            return Response(file_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    '''
    This endpoint return rows of data with pagination, cannot return dataframe directly
    because JSON cant handle NaN value
    '''
    def get(self, request):
        try:
            file_name = request.query_params['filename']
            username = request.query_params['username']
            workspace = request.query_params['workspace']
            workspace_type = request.query_params['type']
        except:
            return Response({'message': "input error"},status=status.HTTP_400_BAD_REQUEST)
        
        # open file as df
        current_path = os.getcwd()
        save_path = f'{current_path}/directory/{username}/{workspace_type}/{workspace}/{file_name}'
        dataframe = pd.read_csv(save_path)

        # set pagination
        max_row = dataframe.shape[0]
        page = int(request.query_params['page'])
        rowsperpage  = int(request.query_params['rowsperpage'])
        first_row = (page - 1) * rowsperpage
        last_row = first_row + rowsperpage
        if last_row > max_row:
            last_row = max_row

        return Response(json.loads(dataframe.iloc[first_row:last_row].to_json()), status=status.HTTP_200_OK)

    def put(self, request):
        try:
            old_file_name = request.query_params['oldfilename']
            username = request.query_params['username']
            workspace = request.query_params['workspace']
            workspace_type = request.query_params['type']
            new_file_name = request.data['newfilename']
        except:
            return Response({'message': "input error"},status=status.HTTP_400_BAD_REQUEST)

        try:
            file = File.objects.get(file=old_file_name, username=username, workspace__name=workspace, workspace__type=workspace_type)
        except:
            return Response({'message': "data not found"}, status=status.HTTP_404_NOT_FOUND)
        
        workspace_fk = Workspace.objects.get(name=workspace, username=username, type=workspace_type)
        payload = {
            'file' : new_file_name,
            'username' : username,
            'workspace' : workspace_fk.id,
        }
        file_serializer = FileSerializer(file, data=payload)
        if file_serializer.is_valid():
            # rename file in directory
            current_path = os.getcwd()
            old_name = f'{current_path}/directory/{username}/{workspace_type}/{workspace}/{old_file_name}'
            new_name = f'{current_path}/directory/{username}/{workspace_type}/{workspace}/{new_file_name}'
            # check if name already exist
            if os.path.isfile(new_name):
                return Response({'errcode': "input error", 'message':"file name must unique"},status=status.HTTP_400_BAD_REQUEST)
            os.rename(old_name, new_name)

            file_serializer.save()
            return Response(file_serializer.data, status=status.HTTP_200_OK)
        
        return Response(file_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        try:
            file_name = request.data['filename']
            username = request.data['username']
            workspace = request.data['workspace']
            workspace_type = request.data['type']
        except:
            return Response({'message': "input error"},status=status.HTTP_400_BAD_REQUEST)

        try:
            if (workspace_type == 'object_segmentation'):
                # TODO :  Delete file record in db
                r = Redis.get()
                r.delete(username + '_' + workspace + '_' + file_name)
            file = File.objects.get(file=file_name, username=username, workspace__name=workspace, workspace__type=workspace_type)
        except:
            return Response({'message': "data not found"}, status=status.HTTP_404_NOT_FOUND)
        
        if (workspace_type != 'object_segmentation'):
            current_path = os.getcwd()
            save_path = f'{current_path}/directory/{username}/{workspace_type}/{workspace}/{file_name}'
            os.remove(save_path)
        file.delete()
        return Response({'message': "deleted successfully"},status=status.HTTP_204_NO_CONTENT)
