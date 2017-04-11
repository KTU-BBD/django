import os
import shutil
import time
import uuid

import docker
from django.conf import settings
from django.http import JsonResponse
from django.utils.six import BytesIO
from rest_framework.decorators import api_view
from rest_framework.parsers import JSONParser

from polls.serializers import CodeSerializer


@api_view(['GET', 'POST'])
def index(request):
    stream = BytesIO(request.body)
    data = JSONParser().parse(stream)
    serializer = CodeSerializer(data=data)

    if serializer.is_valid():
        custom_folder_name = uuid.uuid4().hex
        folder_path = settings.MASTER_MOUNTING_DIR + '/' + custom_folder_name
        os.makedirs(folder_path)

        code_file_path = folder_path + '/' + settings.SCRIPT_NAMES[serializer.data['language']]
        code_file = open(code_file_path, 'w')
        code_file.write(serializer.data['code'])
        code_file.close()

        input_file_path = folder_path + '/' + settings.INPUT_FILE
        input_file = open(input_file_path, 'w')
        input_file.write(serializer.data['input_text'])
        input_file.close()

        client = docker.from_env()
        api = client.api
        container_name = settings.CONTAINER_NAMES[serializer.data['language']]
        container = api.create_container(
            container_name, settings.BASE_SCRIPT, volumes=[settings.CONTAINER_MOUNTING_DIR],
            host_config=api.create_host_config(binds={
                folder_path: {
                    'bind': settings.CONTAINER_MOUNTING_DIR,
                    'mode': 'rw',
                }
            })
        )

        api.start(container.get('Id'))

        sleep_timer = 0
        while client.containers.get(container.get('Id')).status == "running" and sleep_timer < 5:
            time.sleep(0.1)
            sleep_timer += 0.1

        filename = folder_path + '/' + settings.RESULT_FILE
        result = open(filename, 'r')
        results = result.read()
        result.close()

        shutil.rmtree(folder_path)
        if sleep_timer < 5:
            verdict = "OK"
        else:
            verdict = "OVERFLOW"

        response = {'verdict': verdict, 'language': serializer.data['language'], 'output': results}

        return JsonResponse(response)
    else:
        return JsonResponse(serializer.errors)
