from django.db import models


class Documenttopics(models.Model):
    document = models.ForeignKey('Document', on_delete=models.CASCADE, null=False)
    topic = models.ForeignKey('Topic', on_delete=models.CASCADE)

    class Meta:
        unique_together = ('document', 'topic',)
        app_label = 'exampleapp'

