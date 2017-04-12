import docker
import subprocess
from django.test import TestCase

from CodeCheckerAPI import settings


class DockerTestCase(TestCase):
    def test_docker_service_is_running(self):
        self.assertTrue('docker' in subprocess.check_output(['ps', '-A']), 'Docker service is not running')

    def test_docker_contains_images(self):
        api = docker.from_env().api
        for images in api.images():
            if images['RepoTags'][0] not in settings.CONTAINER_NAMES.values():
                self.fail('Image ' + images['RepoTags'][0] + ' not found. Please download it or rename to required name')