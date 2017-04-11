import docker
from django.core.checks import Tags as DjangoTags
from django.core.checks import register, Critical

from CodeCheckerAPI import settings


class Tags(DjangoTags):
    dockerTag = 'docker'


@register(Tags.dockerTag)
def check_docker_images(app_configs=None, **kwargs):
    errors = []

    if not settings.DEBUG:
        try:
            api = docker.from_env().api
            for name in settings.CONTAINER_NAMES.values():
                print api.pull(name, 'latest')
        except Exception:
            errors.append(
                Critical(
                    "Cannot pull docker images from hub. Check internet connection or images names.",
                )
            )
    return errors
