from django.db import models


class Topic(models.Model):
    name = models.CharField(max_length=3000, default="", blank=True)
    parent = models.ForeignKey("self", on_delete=models.CASCADE, default=None, null=True, blank=True)

    class Meta:
        app_label = 'exampleapp'
