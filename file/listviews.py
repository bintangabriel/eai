from rest_framework.views import APIView
from .serializers import FileSerializer, FileObjectSegmentationSerializer
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import File
from eai.app_redis import Redis
from workspace.models import * 
from knox.auth import TokenAuthentication

class ListFileView(APIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request, *args, **kwargs):
        try:
            username = request.query_params['username']
            workspace = request.query_params['workspace']
            type = request.query_params['type']
        except:
            return Response({'message': "input error"},status=status.HTTP_400_BAD_REQUEST)
        print(type)
        if type == "object_segmentation":
            # pattern = f'{username}_{workspace}_*'
            # r = Redis.get()
            # keys = r.keys(f'{pattern}*')
            # keys = []
            # cursor = '0'
            # payload = []
            # while cursor != 0:
            #     cursor, matches = r.scan(cursor=cursor, match=pattern)
            #     keys.extend(matches)
            # for key in keys:
            #     val =  r.get(key)
            #     _, _, filename = key.decode('utf-8').partition(f'{username}_{workspace}_') 
            #     print(filename)
            #     filesize = round(len(val)/(1024 * 1024), 2)
            #     valid_workspace = Workspace.objects.get(name=workspace,username=username)
            #     print(valid_workspace)
            #     payload.append(
            #     {
            #         "file": filename,
            #         "size" : filesize,
            #         "username": username,
            #         "workspace": valid_workspace.id
            #     }
            #     ) 
            print("-----------------------------------------------")
            payload = File.objects.filter(username=username, workspace__name=workspace)
            print(payload)
            res_data = FileObjectSegmentationSerializer(payload, many=True)
            return Response(res_data.data, status=status.HTTP_200_OK)
            # else:
            #     return Response(res_data.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            files = File.objects.filter(username=username, workspace__name=workspace)
            files_serializer = FileSerializer(files, many=True)
            print(files_serializer.data)
            return Response(files_serializer.data, status=status.HTTP_200_OK)
