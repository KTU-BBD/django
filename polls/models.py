from __future__ import unicode_literals

from django.db import models


class Code(models.Model):
    language = models.CharField(max_length=3)
    input_text = models.CharField(blank=False)
    code = models.TextField(blank=False)
    memory_limit = models.IntegerField(blank=True)
    time_limit = models.IntegerField(blank=True)

    def __init__(self, data):
        self.language = data.language
        self.code = data.code
        self.memory_limit = data.memory_limit
        self.time_limit = data.time_limit

    def __init__(self, language, code, input_text, memory_limit, time_limit):
        self.language = language
        self.code = code
        self.memory_limit = memory_limit
        self.time_limit = time_limit
        self.input_text = input_text
