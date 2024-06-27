import os
import secrets
from django.http import JsonResponse, FileResponse
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework import status, permissions
import requests
from .models import MLModel, ModelKey, ObsegModel
from .serializers import MLModelSerializer, ObsegModelSerializer
from file.models import File
from workspace.models import Workspace
import joblib
import time
from eai.celery import app
from eai.app_redis import Redis
from knox.auth import TokenAuthentication
from eai.util import GpuAvail
# from celery.result import AsyncResult
from .record_views import create_training_record_without_request
import json
from utils.ssh import *
from io import BytesIO
from dotenv import load_dotenv


load_dotenv()
    
# Acks late to continue the task until finish when restarting worker
def training_simulation_2(username, workspace, type, file_key, filename, model_type, id, model_name, epoch, learning_rate):
    try:
        ip_modeling = os.environ.get('MODELING_IP')
        port_modeling = os.environ.get('MODELING_PORT')

        training_service_url = f'http://10.233.16.249:7000/train/' # Change domain url on the current staging

        gpu = GpuAvail.get_gpu()
        print(f'gpu: {gpu}')
        model_metadata = {
            'model_type': model_type,
            'model_name': model_name,
            'type': type,
            'username': username,
            'workspace': workspace,
            'filename': filename,
            'gpu': gpu,
            'id': id,
            'epoch': epoch,
            'learning_rate': learning_rate,
            'file_key': file_key
        }
        print('hey')
        curl_command = generate_curl_command(training_service_url, model_metadata)
        print('gelo')
        res = tunnel_modeling_dgx(curl_command)
        # print(training_service_url)
        # res = requests.post(training_service_url, data=model_metadata)
        print(res)
        # return Response(data=res.json()) => for non-celery task
        return res
        # return res
    except Exception as e:
        print('ahhhh')
        # return Response({'message': "input error"}, status=status.HTTP_400_BAD_REQUEST) => for non-celery task
        return { 'message': str(e) , 'status': 400 }

# accept request from user
# passing params to service
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
@authentication_classes([TokenAuthentication])
def initiate_modeling(request):
    try:
        data_received = json.loads(request.body)
        print(data_received)
        type = data_received['type']
        print('type: ', type)
        if (type != "object_segmentation"):
            model_name = data_received['modelname']
            file_name = data_received['filename']
            username = data_received['username']
            workspace = data_received['workspace']
            workspace_type = data_received['type']
            method = data_received['method']
            algorithm = data_received['algorithm']
            feature = data_received['feature']
            target = data_received['target']
            n_cluster = data_received['n_cluster']

            # Simulation purpose
            if n_cluster == '':
                n_cluster = 2
    except:
        return Response({'message': "input error"},status=status.HTTP_400_BAD_REQUEST)
    
    if type == "object_segmentation":
        # try:
            username = data_received['username']
            workspace = data_received['workspace']
            filename = data_received['filename']
            model = data_received['model_type']
            model_name = data_received['model_name']
            epoch = data_received['epoch']
            learning_rate = data_received['learning_rate']
            file_key = (f'{username}_{workspace}_{filename}')

            data = create_training_record_without_request({'status': 'accepted'})
            id = data['id']
            task_status = data['status']
            train_result = training_simulation_2(
                username=username, 
                type=type, 
                file_key=file_key, 
                workspace=workspace, 
                filename=filename, 
                model_type=model, 
                id=id, 
                model_name=model_name,
                epoch=epoch,
                learning_rate=learning_rate
            )
            training_record = {
                'id' : id,
                'status': task_status
            }
            
            return Response(data=training_record, status=status.HTTP_202_ACCEPTED)
        # except Exception as e:
        #     return Response({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    else:
    # setup request to training service endpoint
        training_service_url = 'http://127.0.0.1:7000/train/' # Change domain url on the current staging
        current_path = os.getcwd()
        file_path = f'{current_path}/directory/{username}/{workspace_type}/{workspace}/{file_name}'
        files = {'file': open(file_path, 'rb')}
        model_metadata = {
            'model_name': model_name,
            'file_name' : file_name,
            'username' : username,
            'workspace' : workspace,
            'type' : workspace_type,
            'method' : method,
            'algorithm' : algorithm,
            'feature' : feature,
            'target' : target,
            'n_cluster' : n_cluster,
        }
        training_record = requests.post(training_service_url, data=model_metadata, files=files)
        
        return Response(data=training_record.json(), status=status.HTTP_202_ACCEPTED)

def save_model(request):
    # fetch request file & model metadata
    model_metadata = json.loads(request.body)
    print(model_metadata)
    workspace_type = model_metadata['type']
    if workspace_type == 'object_segmentation':
        model_name = model_metadata['model_name']
        file_name = model_metadata['filename']
        username = model_metadata['username']
        workspace = model_metadata['workspace']
        method = model_metadata['model_type']
        metrics_scores = model_metadata['metrics_scores']
        print("metrics scores: ", metrics_scores)
        # score = model_metadata['score']
# fields = ('id', 'name', 'file_name', 'username', 'workspace', 
#                   'method', 'algorithm', 'metrics_scores','created_time', 'updated_time')
        workspace_fk = Workspace.objects.get(name=workspace, username=username, type=workspace_type)
        print(f'workspace: {workspace_fk}')
        payload = {
            'name' : model_name,
            'file_name' : file_name,
            'username': username,
            'workspace' : workspace_fk.id,
            'method' : method,
            'algorithm' : method,
            'metrics_scores' : json.dumps(metrics_scores)
        }
        obsegmodel_serializer = ObsegModelSerializer(data=payload)
        print(payload)

        print(obsegmodel_serializer.is_valid())

        if obsegmodel_serializer.is_valid():
            # save model to db
            print('here')
            obsegmodel_serializer.save()
            print('model saved')

            # create & save modelkey        

            return JsonResponse(obsegmodel_serializer.data)

        return JsonResponse(obsegmodel_serializer.errors)
    else:
        files = request.FILES['file']

        # fetch model metadata
        model_name = f"{model_metadata['model_name']}.pkl"
        file_name = model_metadata['file_name']
        username = model_metadata['username']
        workspace = model_metadata['workspace']
        method = model_metadata['method']
        algorithm = model_metadata['algorithm']
        metrics_scores = model_metadata['metrics_scores']
        feature = model_metadata['feature']
        target = model_metadata['target']
        n_cluster = model_metadata['n_cluster']

        workspace_fk = Workspace.objects.get(name=workspace, username=username, type=workspace_type)
        payload = {
            'name' : model_name,
            'file_name' : file_name,
            'username': username,
            'workspace' : workspace_fk.id,
            'method' : method,
            'algorithm' : algorithm,
            'metrics_scores' : metrics_scores,
            'feature' : feature,
            'target' : target,
            'n_cluster' : n_cluster,
        }
        
        mlmodel_serializer = MLModelSerializer(data=payload)

        if mlmodel_serializer.is_valid():
            # configure save_path then save model to directory
            current_path = os.getcwd()
            save_path = f'{current_path}/directory/{username}/{workspace_type}/{workspace}/{model_name}'
            with open(f'{save_path}', 'wb') as destination:
                    for chunk in files.chunks():
                        destination.write(chunk)

            if model_metadata['method'] == 'CLUSTERING':
                labels = request.FILES['labels_predicted']
                save_path = f"{current_path}/directory/{username}/{workspace_type}/{workspace}/{model_metadata['model_name']}_labels_predicted.pkl"
                with open(f'{save_path}', 'wb') as destination:
                        for chunk in labels.chunks():
                            destination.write(chunk)
            # save model to db
            mlmodel_serializer.save()

            # create & save modelkey        
            mlmodel = MLModel.objects.get(name=model_name, username=username, workspace__name=workspace, workspace__type=workspace_type)
            modelkey = ModelKey(model=mlmodel, key=secrets.token_hex(16))
            modelkey.save()

            return JsonResponse(mlmodel_serializer.data)

        return JsonResponse(mlmodel_serializer.errors)

@api_view()
def get_model(request):
    try:
        model_name = request.query_params['modelname']
        username = request.query_params['username']
        workspace = request.query_params['workspace']
        workspace_type = request.query_params['type']
    except:
        return Response({'message': "input error"},
                        status=status.HTTP_400_BAD_REQUEST)
    
    try:
        mlmodel = MLModel.objects.get(name=model_name, 
                                      username=username, 
                                      workspace__name=workspace, 
                                      workspace__type=workspace_type)
    except:
        return Response({'message': "data not found"}, 
                        status=status.HTTP_404_NOT_FOUND)
    
    if mlmodel.method == 'CLUSTERING':
        current_path = os.getcwd()
        save_path = f'{current_path}/directory/{username}/{workspace_type}/{workspace}/{model_name[:-4]}_labels_predicted.pkl'
        labels_predicted = joblib.load(save_path)
        mlmodel_serializer = MLModelSerializer(mlmodel)
        return Response({'model': mlmodel_serializer.data,
                         'labels_predicted': labels_predicted}, status=status.HTTP_200_OK)

    mlmodel_serializer = MLModelSerializer(mlmodel)
    return Response(mlmodel_serializer.data, status=status.HTTP_200_OK)

@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([permissions.IsAuthenticated])
def delete_model(request):
    try:
        workspace_type = request.data['type']
        model_name = request.data['model_name']
        username = request.data['username']
        workspace = request.data['workspace']
        if (workspace_type == 'object_segmentation'):
            
            try:
                mlmodel = ObsegModel.objects.get(name=model_name, 
                    username=username, 
                    workspace__name=workspace,
                    workspace__type=workspace_type,
                )
            except:
                return Response({'message': "data not found"}, status=status.HTTP_404_NOT_FOUND)
            
            training_service_url = 'http://127.0.0.1:7000/delete-model/'
            data = {
                'model_name': model_name,
                'username': username,
                'workspace': workspace,
                'workspace_type': workspace_type
            }
            res = requests.post(training_service_url, data=data)
            if (res.status_code == 204 or res.status_code == 404):
                mlmodel.delete()
            else: 
                return Response({'message': 'error'}, status=status.HTTP_400_BAD_REQUEST)
            return Response({'message': "deleted successfully"},status=status.HTTP_204_NO_CONTENT)
        else:            
            try:
                mlmodel = MLModel.objects.get(name=model_name+".pkl", 
                    username=username, 
                    workspace__name=workspace,
                    workspace__type=workspace_type,
                )
            except:
                return Response({'message': "data not found"}, status=status.HTTP_404_NOT_FOUND)
            
            current_path = os.getcwd()
            save_path = f'{current_path}/directory/{username}/{workspace_type}/{workspace}/{model_name}.pkl'
            os.remove(save_path)
            mlmodel.delete()
            return Response({'message': "deleted successfully"},status=status.HTTP_204_NO_CONTENT)
    except:
        return Response({'message': "input error"},status=status.HTTP_400_BAD_REQUEST)

@api_view()
@authentication_classes([TokenAuthentication])
@permission_classes([permissions.IsAuthenticated])
def get_modelkey(request):
    try:
        idmodel = request.query_params['idmodel']
    except:
        return Response({'message': "input error"},status=status.HTTP_400_BAD_REQUEST)

    modelkey = ModelKey.objects.get(model__pk=idmodel)
    return Response({'modelkey': modelkey.key}, status=status.HTTP_200_OK)

@api_view()
@authentication_classes([TokenAuthentication])
@permission_classes([permissions.IsAuthenticated])
def list_model(request):
    try:
        username = request.query_params['username']
        workspace = request.query_params['workspace']
        workspace_type = request.query_params['type']
    except:
        return Response({'message': "input error"},status=status.HTTP_400_BAD_REQUEST)
    try: 
        if (workspace_type == 'object_segmentation'):
            mlmodels = ObsegModel.objects.filter(username=username, workspace__name=workspace, workspace__type=workspace_type)
            print(f"obseg model: {mlmodels}")
            mlmodel_serializer = ObsegModelSerializer(mlmodels, many=True)
            return Response(mlmodel_serializer.data, status=status.HTTP_200_OK)
        mlmodels = MLModel.objects.filter(username=username, workspace__name=workspace, workspace__type=workspace_type)
        mlmodel_serializer = MLModelSerializer(mlmodels, many=True)
        return Response(mlmodel_serializer.data, status=status.HTTP_200_OK)
    except:
        return Response({ 'message': 'Something wrong' }, status=status.HTTP_400_BAD_REQUEST)

@api_view()
def get_columns_type_by_modeling_method(request):
    try:
        file_name = request.query_params['filename']
        username = request.query_params['username']
        workspace = request.query_params['workspace']
        method = request.query_params['method']
    except:
        return Response({'message': "input error"}, status=status.HTTP_400_BAD_REQUEST)

    file = File.objects.get(file=file_name, username=username, workspace__name=workspace)
    columns = []
    if method == "REGRESSION":
        columns = file.numeric.split(",")
    if method == "CLASSIFICATION":
        columns = file.numeric.split(",")

    response = {
        'columns' : columns
    }
    return Response(response, status=status.HTTP_200_OK)

def ssh_to_dgx(request):

    ip_modeling = os.environ.get('MODELING_IP')
    port_modeling = os.environ.get('MODELING_PORT')

    res = gpu_tunneling_checker(f'curl -s -X GET http://{ip_modeling}:{port_modeling}/gpu/')
    return Response({'message': res}, status=status.HTTP_200_OK)

def download_model(request):
    model_metadata = json.loads(request.body)

    print(model_metadata)
    ip_modeling = os.environ.get('MODELING_IP')
    port_modeling = os.environ.get('MODELING_PORT')
    url = f"http://{ip_modeling}:{port_modeling}/train/download/"

    # curl_command = generate_curl_command_without_files(url, model_metadata)

    # res = tunnel_modeling_dgx(curl_command)

    # res = requests.post("http://127.0.0.1:7000/train/download/", json=model_metadata)

    curl_command = generate_curl_command_without_files(url, model_metadata)
    res = tunnel_modeling_dgx_download(curl_command)
    file = BytesIO(res)
    return FileResponse(file)