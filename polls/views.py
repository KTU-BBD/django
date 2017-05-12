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

        limit_in_seconds = serializer.data['timeLimit'] / 1000.0

        code_file_path = folder_path + '/' + settings.SCRIPT_NAMES[serializer.data['language']]
        code_file = open(code_file_path, 'w')
        code_file.write(serializer.data['code'])
        code_file.close()

        input_file_path = folder_path + '/' + settings.INPUT_FILE
        input_file = open(input_file_path, 'w')
        input_file.write(serializer.data['inputText'])
        input_file.close()

        client = docker.from_env()
        api = client.api
        container_name = settings.CONTAINER_NAMES[serializer.data['language']]

        memory_in_kbytes = serializer.data['memoryLimit'] * 10**3
        increased_memory_in_bytes = (serializer.data['memoryLimit']+5) * 10**6

        container = api.create_container(
            image=container_name,
            command=settings.BASE_SCRIPT + " " + str(limit_in_seconds) + "s",
            volumes=[settings.CONTAINER_MOUNTING_DIR],
            host_config=api.create_host_config(
                binds={
                    folder_path: {
                        'bind': settings.CONTAINER_MOUNTING_DIR,
                        'mode': 'rw',
                    }
                },
                mem_limit=increased_memory_in_bytes,
                cpu_period=100000,
                cpu_quota=20000
            ),
            network_disabled=True,
            stop_timeout=1
        )

        api.start(container.get('Id'))
        while client.containers.get(container.get('Id')).status == "running":
            time.sleep(0.01)

        try:
            api.stop(container.get('Id'), timeout=1)
        except Exception:
            pass

        if (serializer.data['language'].startswith("CPP") or serializer.data['language'].startswith("CSH")):
            compilation_error_file_path = folder_path + '/' + settings.COMPILATION_ERROR_FILE
            compilation_error_file_reader = open(compilation_error_file_path, 'r')
            compilation_errors = compilation_error_file_reader.read()
            compilation_error_file_reader.close()

            if len(compilation_errors) > 0:
                return JsonResponse({
                    'verdict': "COMPILATION_ERROR",
                    'language': serializer.data['language'],
                    'output': compilation_errors,
                    'timeSpent': 0,
                    'memory': 0
                })

        result_file_path = folder_path + '/' + settings.RESULT_FILE
        result_file_reader = open(result_file_path, 'r')
        results = result_file_reader.read()
        result_file_reader.close()

        runtime_error_file_path = folder_path + '/' + settings.ERROR_FILE
        runtime_error_file_reader = open(runtime_error_file_path, 'r')
        runtime_errors = runtime_error_file_reader.read()
        runtime_error_file_reader.close()

        time_file_path = folder_path + '/' + settings.TIME_FILE
        time_file_reader = open(time_file_path, 'r')
        times = time_file_reader.read()
        time_file_reader.close()

        shutil.rmtree(folder_path)
        runtime_information = times.strip().split()[-1].split(',')
        verdict = "OK"

        if len(runtime_errors) > 0:
            verdict = "RUNTIME_ERROR"
            results = runtime_errors

        if float(runtime_information[1]) > limit_in_seconds:
            verdict = "TIME_OVERFLOW"
            results = ""

        if int(runtime_information[0]) > memory_in_kbytes:
            verdict = "MEMORY_OVERFLOW"
            results = ""

        response = {
            'verdict': verdict,
            'language': serializer.data['language'],
            'output': results,
            'timeSpent': runtime_information[1],
            'memory': runtime_information[0]
        }

        return JsonResponse(response)
    else:
        return JsonResponse(serializer.errors)
