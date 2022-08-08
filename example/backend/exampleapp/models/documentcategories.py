from django.db import models


class Documentcategories(models.Model):
    document = models.ForeignKey('Document', on_delete=models.CASCADE, null=False)
    category = models.ForeignKey('Category', on_delete=models.CASCADE)

    class Meta:
        unique_together = ('document', 'category')
        app_label = 'exampleapp'

