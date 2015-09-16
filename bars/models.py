from django.db import models
from django.conf import settings

import uuid

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

	# Stripe
	# stripe_id

	@models.permalink
	def get_absolute_url(self):
		return 'bars:bar-detail', (self.slug,)

	def is_owner(self, user_id):
		return self.owner.pk == user_id

class Bartender(models.Model):
	user = models.OneToOneField(settings.AUTH_USER_MODEL)
	bar = models.ForeignKey('Bar')

class BartenderInvite(models.Model):
	bar = models.ForeignKey('Bar')
	email = models.EmailField()
	token = models.CharField(max_length=100)

	@classmethod
	def create(cls, bar, email):
		return cls(bar=bar, email=email, token=uuid.uuid4())