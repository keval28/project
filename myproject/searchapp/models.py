from django.db import models

# Create your models here.
class DataModel(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    lastname = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.name