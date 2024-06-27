from datetime import datetime
import os
import shutil
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .serializers import WorkspaceSerializer
from .models import Workspace
from knox.auth import TokenAuthentication

class WorkspaceView(APIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request, *args, **kwargs):
        # manual parsing the request
        try:
            name = request.data['name']
            username = request.data['username']
            description = request.data['description']
            workspace_type = request.data['type']
        except:
            return Response({'message': "input error"},status=status.HTTP_400_BAD_REQUEST)

        if Workspace.objects.filter(name=name, username=username, type=workspace_type).exists() :
            return Response({'message': "already exist"},status=status.HTTP_400_BAD_REQUEST)
        
        dir_name = name
        current_dir = os.getcwd() 
        parent_dir = f'{current_dir}/directory/{username}/{workspace_type}'
        path = os.path.join(parent_dir, dir_name)
        os.makedirs(path)

        payload = {
            'name' : name,
            'username' : username,
            'description' : description,
            'type' : workspace_type
        }
        workspace_serializer = WorkspaceSerializer(data=payload)
       
        if workspace_serializer.is_valid():
            workspace_serializer.save()
            return Response(workspace_serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(workspace_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def get(self, request, *args, **kwargs):
        try:
            workspace = Workspace.objects.get(name=request.query_params['name'], 
                                              username=request.query_params['username'],
                                              type=request.query_params['type'])
        except:
            return Response({'message': "data not found"}, status=status.HTTP_404_NOT_FOUND)
        workspace_serializer = WorkspaceSerializer(workspace)
        return Response(workspace_serializer.data, status=status.HTTP_200_OK)

    def put(self, request, *args, **kwargs):
        try:
            workspace = Workspace.objects.get(name=request.query_params['name'],
                                              username=request.query_params['username'],
                                              type=request.query_params['type'])
        except:
            return Response({'message': "data not found"}, status=status.HTTP_404_NOT_FOUND)

        workspace_serializer = WorkspaceSerializer(workspace, data=request.data)
        if workspace_serializer.is_valid():
            workspace_serializer.save()

            # update user's subdirectory name
            current_dir = os.getcwd()
            username = request.query_params['username']
            workspace_type = request.query_params['type']
            parent_dir = f'{current_dir}/directory/{username}/{workspace_type}'
            old_path = os.path.join(parent_dir, request.query_params['name'])
            new_path = os.path.join(parent_dir, request.data['name'])
            os.rename(old_path, new_path)
            
            return Response(workspace_serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(workspace_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, *args, **kwargs):
        try:
            workspace = Workspace.objects.get(name=request.data['name'], 
                                              username=request.data['username'],
                                              type=request.data['type'])
        except:
            return Response({'message': "data not found"}, status=status.HTTP_404_NOT_FOUND)
        
        current_dir = os.getcwd()
        username = request.data['username']
        workspace_type = request.data['type']
        parent_dir = f'{current_dir}/directory/{username}/{workspace_type}'
        path = os.path.join(parent_dir, request.data['name'])
        
        workspace.delete()
        shutil.rmtree(path)
        
        return Response({'message': "deleted successfully"},status=status.HTTP_204_NO_CONTENT)