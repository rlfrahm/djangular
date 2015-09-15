from django.db import models
from django.conf import settings

# Create your models here.
class Bar(models.Model):
	# Details
	name = models.CharField(max_length=255)
	# slug = models.SlugField(unique=True)

	# Owner
	owner = models.ForeignKey(settings.AUTH_USER_MODEL, null=True)

	# Address
	street = models.TextField(blank=True, null=True)
	city = models.TextField(blank=True, null=True)
	province = models.TextField(blank=True, null=True)
	code = models.TextField(blank=True, null=True)

	# Image
	image = models.ImageField(upload_to='bars', blank=True, null=True)

	@models.permalink
	def get_absolute_url(self):
		return 'bars:bar-detail', (self.slug,)

class Bartender(models.Model):
	user = models.OneToOneField(settings.AUTH_USER_MODEL)
	bar = models.ForeignKey('Bar')