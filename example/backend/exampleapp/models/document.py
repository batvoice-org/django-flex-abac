from django.db import models
from django.utils import timezone


class Document(models.Model):
    document_datetime = models.DateTimeField('date of document creation', default=timezone.now, blank=True)
    filename = models.CharField(max_length=1000)

    desk = models.ForeignKey('desk', on_delete=models.SET_NULL, null=True)
    brand = models.ForeignKey('brand', on_delete=models.CASCADE, blank=True, default="")

    topics = models.ManyToManyField('topic', through='documenttopics')
    regions = models.ManyToManyField('region', through='documentregions')
    categories = models.ManyToManyField('category', through='documentcategories')

    class Meta:
        app_label = 'exampleapp'