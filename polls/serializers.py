from django.conf import settings
from rest_framework import serializers

from polls.models.code import Code


class CodeSerializer(serializers.ModelSerializer):
    SUPPORTED_LANGUAGES = settings.CONTAINER_NAMES.keys()
    language = serializers.ChoiceField(required=True, error_messages={'required': 'Language field is required'},
                                       choices=SUPPORTED_LANGUAGES)
    code = serializers.CharField(required=True, error_messages={'required': 'Code field is required'})
    input_text = serializers.CharField(required=True, error_messages={'required': 'Input text field is required'})
    memory_limit = serializers.IntegerField(required=True)
    time_limit = serializers.IntegerField(required=True)

    class Meta:
        model = Code
        fields = ('language', 'input_text', 'code', 'memory_limit', 'time_limit')
