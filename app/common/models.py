from django.db import models


class Resource(models.Model):
    name = models.CharField(max_length=1024)
    url = models.URLField()
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    parent = models.ForeignKey("self", null=True, blank=True, on_delete=models.PROTECT)
