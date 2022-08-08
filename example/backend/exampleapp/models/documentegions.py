from django.db import models


class Documentregions(models.Model):
    document = models.ForeignKey('Document', on_delete=models.CASCADE, null=False)
    region = models.ForeignKey('Region', on_delete=models.CASCADE)

    class Meta:
        unique_together = ('document', 'region',)
        app_label = 'exampleapp'

