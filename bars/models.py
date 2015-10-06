from django.db import models
from django.conf import settings
from django.contrib.auth.models import User

from .emails import send_tab_invite

import uuid, os

from account.storage import OverwriteStorage

FILES_BASE = 'files'
BAR_PREFIX = 'bar'

BAR_PROFILE_DEFAULT = 'static/images/user_profile_default.png'

def path_and_rename(instance, filename):
	ext = filename.split('.')[-1]
	# get filename
	if instance.pk:
		path = '%s_%s' % (BAR_PREFIX, instance.pk)
		filename = '{}.{}'.format(instance.pk, ext)
	else:
		# set filename as random string
		ran = uuid4().hex
		path = '%s_%s' % (BAR_PREFIX, ran)
		filename = '{}.{}'.format(ran, ext)
	# return the whole path to the file
	return os.path.join(path, filename)

# Create your models here.
class Bar(models.Model):
	class Meta:
		app_label = 'bars'
	# Details
	name = models.CharField(max_length=255)
	# slug = models.SlugField(unique=True)

	# Owner
	owner = models.ForeignKey(settings.AUTH_USER_MODEL, null=True)

	# Address
	street = models.CharField(max_length=255, blank=True, null=True)
	city = models.CharField(max_length=255, blank=True, null=True)
	province = models.CharField(max_length=255, blank=True, null=True)
	postal = models.CharField(max_length=25, blank=True, null=True)
	country = models.CharField(max_length=2, default='US')
	lat = models.DecimalField(max_digits=16, decimal_places=14)
	lng = models.DecimalField(max_digits=16, decimal_places=14)

	avatar = models.ImageField(upload_to=path_and_rename, blank=True, storage=OverwriteStorage(), default=BAR_PROFILE_DEFAULT)
	# Image
	image = models.ImageField(upload_to='bars', blank=True, null=True)

	@property
	def avatar_url(self):
	    if self.avatar and hasattr(self.avatar, 'url'):
	        return self.avatar.url

	@models.permalink
	def get_absolute_url(self):
		return 'bars:bar-detail', (self.slug,)

	def is_owner(self, user_id):
		return self.owner.pk == user_id

	def __unicode__(self):
		return self.name

class Bartender(models.Model):
	user = models.ForeignKey(settings.AUTH_USER_MODEL)
	bar = models.ForeignKey('Bar')
	working = models.BooleanField(default=False)

class BartenderInvite(models.Model):
	bar = models.ForeignKey('Bar')
	email = models.EmailField()
	token = models.CharField(max_length=100)

	@classmethod
	def create(cls, bar, email):
		return cls(bar=bar, email=email, token=uuid.uuid4())

class Checkin(models.Model):
	user = models.ForeignKey(settings.AUTH_USER_MODEL)
	when = models.DateTimeField()
	bar = models.ForeignKey('Bar')
	created = models.DateTimeField(auto_now_add=True, auto_now=False)
	updated = models.DateTimeField(auto_now_add=False, auto_now=True)

class TabInvite(models.Model):
	tab = models.ForeignKey('Tab')
	email = models.EmailField()
	token = models.CharField(max_length=100)

class Tab(models.Model):
	bar = models.ForeignKey('Bar', blank=True, null=True)
	amount = models.DecimalField(max_digits=6, decimal_places=2)
	sender = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='sender')
	receiver = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='receiver', blank=True, null=True)
	email = models.EmailField(blank=True, null=True)
	source = models.CharField(max_length=100, null=True, blank=True, default='')
	accepted = models.BooleanField(default=False)
	created = models.DateTimeField(auto_now_add=True, auto_now=False)
	updated = models.DateTimeField(auto_now_add=False, auto_now=True)
	note = models.CharField(max_length=140, default='', null=True)

	def set_receiver(self, request, email):
		if request.user.email is email:
			self.receiver = request.user
			return self
		user = User.objects.get(email=email)
		if not user:
			# There is no user with this email, send email
			invite = TabInvite()
			invite.tab = self
			invite.email = email
			invite.token = uuid.uuid4()
			invite.save()
			send_tab_invite(request, self, invite)
			self.email = email
		else:
			self.receiver = user
		return self

class Sale(models.Model):
	amount = models.DecimalField(max_digits=6, decimal_places=2)
	bar = models.ForeignKey('Bar')
	customer = models.ForeignKey(settings.AUTH_USER_MODEL)
	created = models.DateTimeField(auto_now_add=True, auto_now=False)
	updated = models.DateTimeField(auto_now_add=False, auto_now=True)
