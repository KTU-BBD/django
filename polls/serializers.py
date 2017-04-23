from django.conf import settings
from rest_framework import serializers

from polls.models.code import Code


class CodeSerializer(serializers.ModelSerializer):
    SUPPORTED_LANGUAGES = settings.CONTAINER_NAMES.keys()
    language = serializers.ChoiceField(required=True, error_messages={'required': 'Language field is required'},
                                       choices=SUPPORTED_LANGUAGES)
    code = serializers.CharField(required=True, error_messages={'required': 'Code field is required'})
    inputText = serializers.CharField(required=True, error_messages={'required': 'Input text field is required'})
    memoryLimit = serializers.IntegerField(required=True)
    timeLimit = serializers.IntegerField(required=True)

    class Meta:
        model = Code
        fields = ('language', 'inputText', 'code', 'memoryLimit', 'timeLimit')
