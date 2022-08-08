from django.contrib import admin


from .models import (
    Desk,
    Document,
    Brand,
)

admin.site.register(Desk)
admin.site.register(Document)
admin.site.register(Brand)
