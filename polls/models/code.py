import datetime
from django.db import models
from rest_framework import serializers

class Code(models.Model):
    language = models.CharField(max_length=3)
    code = models.TextField(blank=False)
    memory_limit = models.IntegerField(blank=True)
    time_limit = models.IntegerField(blank=True)

    def __init__(self, data):
        self.language = data.language
        self.code = data.code
        self.memory_limit = data.memory_limit
        self.time_limit = data.time_limit

    def __init__(self, language, code, memory_limit, time_limit):
        self.language = language
        self.code = code
        self.memory_limit = memory_limit


class CodeSerializer(serializers.ModelSerializer):
    SUPPORTED_LANGUAGES = (
        ('CSH'),
        ('CPP'),
        ('PYT'),
    )
    language = serializers.ChoiceField(required=True,error_messages={'required': 'Language field is required'}, choices=SUPPORTED_LANGUAGES)
    code = serializers.CharField(required=True,error_messages={'required': 'Code field is required'})
    memory_limit = serializers.IntegerField(required=False)
    time_limit = serializers.IntegerField(required=False)
    class Meta:
        model = Code
        fields = ('language', 'code', 'memory_limit', 'time_limit')