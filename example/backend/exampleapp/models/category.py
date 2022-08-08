from django.db import models
from treebeard.mp_tree import MP_Node


class Category(MP_Node):
    name = models.CharField(max_length=3000, default="", blank=True)

    class Meta:
        app_label = 'exampleapp'
