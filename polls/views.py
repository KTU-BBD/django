import os

import docker
import time

import shutil
from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth.models import User, Group
from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets
from polls.models.code import Code, CodeSerializer
from django.utils.six import BytesIO
from rest_framework.parsers import JSONParser
from polls.serializers import UserSerializer, GroupSerializer
from django.http import JsonResponse
from django.conf import settings
from rest_framework.renderers import JSONRenderer
import uuid


@csrf_exempt
def index(request):
    stream = BytesIO(request.body)
    data = JSONParser().parse(stream)
    serializer = CodeSerializer(data=data)

    if serializer.is_valid():
        custom_folder_name = uuid.uuid4().hex
        folder_path = settings.MASTER_MOUNTING_DIR + '/' + custom_folder_name
        os.makedirs(folder_path)

        code_file_path = folder_path + '/' + settings.SCRIPT_NAMES[serializer.data['language']]
        codeFile = open(code_file_path, 'w')
        codeFile.write(serializer.data['code'])
        codeFile.close()

        client = docker.from_env()
        api = client.api
        containerName = settings.CONTAINER_NAMES[serializer.data['language']]
        container = api.create_container(
            containerName, settings.BASE_SCRIPT, volumes=[settings.CONTAINER_MOUNTING_DIR],
            host_config=api.create_host_config(binds={
                folder_path: {
                    'bind': settings.CONTAINER_MOUNTING_DIR,
                    'mode': 'rw',
                }
            })
        )

        api.start(container.get('Id'))

        timee = 0
        while client.containers.get(container.get('Id')).status == "running" and timee < 5:
            time.sleep(0.1)
            timee += 0.1

        filename = folder_path + '/' + settings.RESULT_FILE
        result = open(filename, 'r')
        results = result.read()
        result.close()

        shutil.rmtree(folder_path)


        return JsonResponse(data=results, safe=False)
    else:
        return JsonResponse(serializer.errors)

        # serializer.is_valid(raise_exception=True)

        # client = docker.from_env()
        # api = client.api
        # container = api.create_container(
        # 'python-ubuntu', 'script.sh', volumes=['/mnt/vol2'],
        # host_config=api.create_host_config(binds={
        #     '/home/arviens/code': {
        #         'bind': '/mnt/vol2',
        #         'mode': 'rw',
        #     }
        # })
        # )
        #
        # api.start(container.get('Id'))
        #
        #
        # timee = 0
        # while client.containers.get(container.get('Id')).status == "running" and timee < 5:
        #     time.sleep(0.1)
        #     timee += 0.1


def dokcer(data):
    print settings.MOUNTING_DIR
    # client = docker.from_env()
    # api = client.api
    # container = api.create_container(
    # 'python-ubuntu', 'script.sh', volumes=['/mnt/vol2'],
    # host_config=api.create_host_config(binds={
    #     settings.MOUNTING_DIR: {
    #         'bind': '/mnt/vol2',
    #         'mode': 'rw',
    #     }
    # })
    # )
