from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.contrib.auth.models import Group

import datetime, os, uuid

from .storage import OverwriteStorage

FILES_BASE = 'files'
USER_PREFIX = 'user'

USER_PROFILE_DEFAULT = 'user_profile_default.png'

def path_and_rename(instance, filename):
	ext = filename.split('.')[-1]
	# get filename
	if instance.pk:
		path = '%s_%s' % (USER_PREFIX, instance.pk)
		filename = '{}.{}'.format(instance.pk, ext)
	else:
		# set filename as random string
		ran = uuid4().hex
		path = '%s_%s' % (USER_PREFIX, ran)
		filename = '{}.{}'.format(ran, ext)
	# return the whole path to the file
	return os.path.join(path, filename)

# Create your models here.
class UserProfile(models.Model):
	user = models.OneToOneField(User, related_name="profile")
	created = models.DateTimeField(auto_now_add=True, auto_now=False)
	updated = models.DateTimeField(auto_now_add=False, auto_now=True)
	location = models.CharField(max_length=100, blank=True)
	ip_address = models.CharField(max_length=120, default='ABC')
	avatar = models.ImageField(upload_to=path_and_rename, blank=True, storage=OverwriteStorage(), default=USER_PROFILE_DEFAULT)

	# The Django User model provides an "active" attribute,
	# but using said attribute causes DRF to return a 403
	# if the user has not activated their account. We want
	# to allow the user to use their account before activation.
	# Therefore, our own "active" attribute is required.
	active = models.BooleanField(default=False)

	@property
	def is_active(self):
		return self.active

	@property
	def avatar_url(self):
	    if self.avatar and hasattr(self.avatar, 'url'):
	        return self.avatar.url

	def save(self, *args, **kwargs):
		try:
			existing = UserProfile.objects.all().get(user=self.user)
			self.id=existing.id
		except UserProfile.DoesNotExist:
			pass
		# if self.tab < 0:
		# 	self.tab = 0
		models.Model.save(self, *args, **kwargs)

	def is_birthday(self):
		birthday = self.cleaned_data['Birthday']
		age = (date.now() - birthday).days/365
		if age < 21:
			raise models.ValidationError('Must be at least 21 years old to register')
		return self.age in (self.DRINKER, self.BARTENDER_SERVER)

	def is_birthday_2(self):
		birthday_2 = self.cleaned_data['Birthday']
		age = (date.now() - birthday_2).days/365
		if age < 18:
			raise models.ValidationError('Must be at least 18 years old to register')
		return self.age in (self.BARTENDER_SERVER, self.DRINKER)

	def is_established(self):
		established = self.cleaned_data['Established']
		started = (date.now() - established).days/1
		if started < 1:
			raise models.ValidationError('Must be in business for at least 1 day to register')
		return self.age in (self.BUSINESS, self.DRINKER)

	def is_owner(self):
		return self.user.bar_set.count() > 0

	def __unicode__(self):
		return self.user.username

	@classmethod
	def new(cls, username, email, password, firstname, lastname):
		user = User.objects.create_user(username, email, password)
		user.first_name = firstname
		user.last_name = lastname
		user.save()

		profile = UserProfile(user=user, active=False)
		profile.save()
		return user

	class Meta:
		unique_together = ("user",)

class PasswordResetToken(models.Model):
	user = models.OneToOneField(settings.AUTH_USER_MODEL)
	token = models.CharField(max_length=100)

	def __unicode__(self):
		return self.user.username

	@classmethod
	def new(cls, user):
		prt = cls(user=user, token=uuid.uuid4())
		prt.save()
		return prt

class AccountActivationToken(models.Model):
	user = models.OneToOneField(settings.AUTH_USER_MODEL)
	token = models.CharField(max_length=100)

	def __unicode__(self):
		return self.user.username
