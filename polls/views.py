import os
import shutil
import time
import uuid

import docker
from django.conf import settings
from django.http import JsonResponse
from django.utils.six import BytesIO
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser

from polls.models.code import CodeSerializer

"""
 TODO add empty request validation, also don't forget to return error codes
 sample request
    {
        "code": "varr = raw_input('Choose a number: ')\nttt = raw_input('Choose a number: ')\nprint varr\nprint ttt",
        "input_text": "test\ntest",
        "language": "PYT"
    }
 Addr: http://127.0.0.1:8000/test/

"""

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
