from django.db import models
from django.conf import settings

# Create your models here.
class Bar(models.Model):
	name = models.CharField(max_length=255)

class Bartender(models.Model):
	user = models.OneToOneField(settings.AUTH_USER_MODEL)
	bar = models.ForeignKey('Bar')