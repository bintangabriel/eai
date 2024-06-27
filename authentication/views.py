import os
import shutil
from django.http import HttpResponsePermanentRedirect
from rest_framework.response import Response
from rest_framework.decorators import api_view
from knox.models import AuthToken
from rest_framework_simplejwt.tokens import RefreshToken
from .models import UserProfile
import jwt
from rest_framework import status
from .utils import Util, generate_image_name
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status, permissions
from workspace.models import Workspace
from .serializers import *
from rest_framework.permissions import AllowAny

class CustomRedirect(HttpResponsePermanentRedirect):
    allowed_schemes = [os.environ.get('APP_SCHEME'), 'http', 'https']

'''
Create user
'''
@api_view(['POST'])
def RegisterUser(request):
    try:
        username = request.data['username']
        email = request.data['email']
        password = request.data['password']
        no_telp = request.data['no_telp']
    except:
        return Response({'message': "input error"},status=status.HTTP_400_BAD_REQUEST)
    
    registerSerializer = RegisterSerializer(data=request.data)

    registerSerializer.is_valid(raise_exception=True)
    user_record = registerSerializer.save()
    user_temp = UserSerializer(user_record)    
    
    # generate token
    token = jwt.encode(user_temp.data, "rahasia")

    # send email
    url = "https://lumba-ai-testing.vercel.app/verify-email?username=" + \
        user_temp.data['username'] + "&token=" + str(token)
    body = user_temp.data['username'] + ', ' + \
        'please verify your account through this link \n' + url
    email_data = {
        'email_body' : body,
        'to_email' : user_temp.data['email'],
        'email_subject' : 'Verify your account'
    }
    Util.send_email(data=email_data)

    return Response(user_temp.data, status=status.HTTP_201_CREATED)

'''
Verify User otherwise they cannot use app,
Verification url sent through email
'''
@api_view(['GET'])
def VerifyAccount(request):
    token = request.query_params['token']
    try:
        payload = jwt.decode(token, "rahasia", algorithms=["HS256"])
        user = UserProfile.objects.get(id=payload['id'])
        if not user.is_active:
            user.is_active = True
            user.save()
        
        # create directory for username
        dir_name = user.username
        current_dir = os.getcwd() 
        parent_dir = f'{current_dir}/directory/'
        path = os.path.join(parent_dir, dir_name)
        os.mkdir(path)

        # create subdirectory (workspace type) for predicting and forecasting
        parent_workspace_dir = f'{current_dir}/directory/{dir_name}'
        predicting_path = os.path.join(parent_workspace_dir, 'predicting')
        forecasting_path = os.path.join(parent_workspace_dir, 'forecasting')
        os.mkdir(predicting_path)
        os.mkdir(forecasting_path)

        return Response({
            'message': 'activated',
            'token': AuthToken.objects.create(user)[1]
        })

    except jwt.ExpiredSignatureError:
        return Response({'error':'Activation Expired'}, status=status.HTTP_400_BAD_REQUEST)

    except jwt.exceptions.DecodeError:
        return Response({'error':'Invalid Token'}, status=status.HTTP_400_BAD_REQUEST)

'''
Get User
'''
@api_view()
def GetUser(request):
    try:
        userProfile = UserProfile.objects.get(username=request.query_params['username'])
    except:
        return Response({'message': "data not found"}, status=status.HTTP_404_NOT_FOUND)
    serializer = UserProfileSerializer(userProfile)
    return Response(serializer.data, status=status.HTTP_200_OK)

'''
Update User data
'''
@api_view(['PUT'])
def UpdateUser(request):
    try:
        username = request.query_params['username']
    except:
        return Response({'message': "input error"},status=status.HTTP_400_BAD_REQUEST)
    
    try:
        user = UserProfile.objects.get(username=username)
    except:
        return Response({'message': "data not found"}, status=status.HTTP_404_NOT_FOUND)

    serializer = UpdateUserProfileDataSerializer(user, data=request.data)
    if serializer.is_valid():
        serializer.save()

        # update user's subdirectory name
        current_dir = os.getcwd() 
        parent_dir = f'{current_dir}/directory/'
        old_path = os.path.join(parent_dir, username)
        new_path = os.path.join(parent_dir, request.data['username'])
        os.rename(old_path, new_path)

        user = UserProfile.objects.get(username=request.data['username'])
        userProfileSerializer = UserProfileSerializer(user)
        return Response(userProfileSerializer.data, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

'''
Update User picture
'''
@api_view(['PUT'])
def UpdateUserPicture(request):
    try:
        username = request.query_params['username']
        profile_picture = request.data['profile_picture']
    except:
        return Response({'message': "input error"},status=status.HTTP_400_BAD_REQUEST)
    
    try:
        user = UserProfile.objects.get(username=username)
    except:
        return Response({'message': "data not found"}, status=status.HTTP_404_NOT_FOUND)

    serializer = UpdateUserProfilePictureSerializer(user, data=request.data)
    if serializer.is_valid():
        serializer.save()
        user = UserProfile.objects.get(username=username)
        userProfileSerializer = UserProfileSerializer(user)
        return Response(userProfileSerializer.data, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

'''
Update User password
'''
@api_view(['PUT'])
def UpdateUserPassword(request):
    try:
        username = request.query_params['username']
        old_password = request.data['old_password']
        new_password = request.data['new_password']
    except:
        return Response({'message': "input error"},status=status.HTTP_400_BAD_REQUEST)
    
    try:
        user = UserProfile.objects.get(username=username)
    except:
        return Response({'message': "data not found"}, status=status.HTTP_404_NOT_FOUND)

    if user.check_password(old_password):
        serializer = UpdateUserProfilePasswordSerializer(user, data={'password': new_password})
    if serializer.is_valid():
        user.set_password(new_password)
        user.save()
        user = UserProfile.objects.get(username=username)
        userProfileSerializer = UserProfileSerializer(user)
        return Response(userProfileSerializer.data, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

'''
Login User
'''
@api_view(['POST'])
@permission_classes([AllowAny])
def Login(request):
    print("heiheiehie")
    loginSerializer = LoginSerializer(data=request.data)
    loginSerializer.is_valid(raise_exception=True)
    user = loginSerializer.validated_data
    token = AuthToken.objects.create(user)[1]
    print('============================================')
    print(token)
    return Response({
        'user': UserSerializer(user).data,
        'token': token
    })

'''
Delete user and user's directory
1. delete workspace from db
2. delete user from db
3. delete user's directory
'''
@api_view(['POST'])
@permission_classes([permissions.IsAdminUser])
def DeleteUser(request):
    try:
        username = request.data['username']
    except:
        return Response({'message': "input error"},status=status.HTTP_400_BAD_REQUEST)
    
    try:
        user = UserProfile.objects.get(username=username)
    except:
        return Response({'message': "username not found"},status=status.HTTP_404_NOT_FOUND)
        
    current_dir = os.getcwd()
    path = f'{current_dir}/directory/{username}'
    shutil.rmtree(path)
    user.delete()
    
    workspace = Workspace.objects.filter(username=username)
    if workspace.count() != 0:
        workspace.delete()
    
    return Response({'message': "deleted successfully"},status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])
def ListUser(request):
    users = UserProfile.objects.all()
    users_serializer = UserProfileSerializer(users, many=True)
    return Response(users_serializer.data, status=status.HTTP_200_OK)