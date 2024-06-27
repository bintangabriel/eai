from rest_framework.views import APIView
from .serializers import WorkspaceSerializer
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import Workspace
from knox.auth import TokenAuthentication

class ListWorkspaceView(APIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request, *args, **kwargs):
        try:
            username = request.query_params['username']
        except:
            return Response({'message': "input error"},status=status.HTTP_400_BAD_REQUEST)
            
        workspaces = Workspace.objects.filter(username=username)
        workspaces_serializer = WorkspaceSerializer(workspaces, many=True)
        return Response(workspaces_serializer.data, status=status.HTTP_200_OK)