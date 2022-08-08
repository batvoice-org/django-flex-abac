from django.db import models
from django.utils import timezone


class Evaluation(models.Model):
    name = models.CharField(max_length=1000)
    document = models.ForeignKey('Document', on_delete=models.CASCADE, null=False)

    class Meta:
        app_label = 'exampleapp'