from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.utils import timezone

from notifications.emails import send_tab_invite

import uuid, os, stripe

from account.storage import OverwriteStorage

FILES_BASE = 'files'
BAR_PREFIX = 'bar'

BAR_PROFILE_DEFAULT = 'bar_profile_default.png'

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

class LocationManager(models.Manager):
    def nearby(self, lat, lng, proximity):
        """
        Return all object which distance to specified coordinates
        is less than proximity given in kilometers
        """
        # Great circle distance formula
        gcd = """
              6371 * acos(
               cos(radians(%s)) * cos(radians(lat))
               * cos(radians(lng) - radians(%s)) +
               sin(radians(%s)) * sin(radians(lat))
              )
              """
        gcd_lt = "{} < %s".format(gcd)
        return self.get_queryset()\
                   .exclude(lat=None)\
                   .exclude(lng=None)\
                   .extra(
                       select={'distance': gcd},
                       select_params=[lat, lng, lat],
                       where=[gcd_lt],
                       params=[lat, lng, lat, proximity],
                       order_by=['distance']
                   )

# Create your models here.
class Bar(models.Model):
	class Meta:
		app_label = 'bars'

	objects = LocationManager()
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

	# location = models.PointField(srid=4326, verbose_name="Location")

	avatar = models.ImageField(upload_to=path_and_rename, blank=True, storage=OverwriteStorage(), default=BAR_PROFILE_DEFAULT)
	# Image
	image = models.ImageField(upload_to='bars', blank=True, null=True)

	@property
	def avatar_url(self):
	    if self.avatar and hasattr(self.avatar, 'url'):
	        return self.avatar.url

	@property
	def location(self):
		return '%s, %s, %s' % (self.street, self.city, self.province)

	@models.permalink
	def get_absolute_url(self):
		return 'bars:bar-detail', (self.slug,)

	def is_owner(self, user_id, user=None):
		# If a user is provided, use more advanced lookup
		# if user:
		# 	role = user.role_set.filter(bar_id=self.pk)[:1]
		# 	if not role:
		# 		# No role!
		# 		return False
		# 	else:
		# 		return ('owner' in role[0].roles)
		# else:
		# 	# Do a simple comparison
		return self.owner.pk == user_id

	def is_admin(self, user_id):
		# Check if user is either 'admin' or 'owner' role
		# Get this role
		if self.owner.pk == user_id:
			return True
		roles = self.role_set.filter(user_id=user_id)[:1]
		if len(roles) < 1:
			return False
		return ('admin' in roles[0])

	@classmethod
	def get_all_within_distance(cls, lat, lng, distance):
		print lat
		print lng
		ref_location = Point(float(lat), float(lng))
		return cls.objects.filter(location__distance_lte=(ref_location, D(m=distance))).distance(ref_location).order_by('distance')

	def __unicode__(self):
		return self.name

	@classmethod
	def new(cls, name, location, owner, avatar=None):
		bar = Bar(name=name)
		bar.street = location.get('street')
		bar.city = location.get('city')
		bar.province = location.get('province')
		bar.postal = location.get('postal')
		if location.get('country'):
			bar.country = location.get('country')
		bar.lat = location.get('lat')
		bar.lng = location.get('lng')
		bar.owner = owner
		if avatar:
			bar.avatar = avatar
		bar.save()
		return bar

class Bartender(models.Model):
	user = models.OneToOneField(settings.AUTH_USER_MODEL)
	working = models.BooleanField(default=False)

class RoleInvite(models.Model):
	bar = models.ForeignKey('Bar')
	email = models.EmailField()
	token = models.CharField(max_length=100)
	roles = models.CharField(max_length=100)

	@classmethod
	def create(cls, bar, email):
		return cls(bar=bar, email=email, token=uuid.uuid4())

class Checkin(models.Model):
	user = models.ForeignKey(settings.AUTH_USER_MODEL)
	when = models.DateTimeField()
	bar = models.ForeignKey('Bar')
	created = models.DateTimeField(auto_now_add=True, auto_now=False)
	updated = models.DateTimeField(auto_now_add=False, auto_now=True)

	@classmethod
	def new(cls, bar_id, user):
		checkin = Checkin()
		checkin.bar = get_object_or_404(Bar, pk=bar_id)
		checkin.when = timezone.now()
		checkin.user = user
		checkin.save()
		return checkin

class TabInvite(models.Model):
	tab = models.OneToOneField('Tab')
	email = models.EmailField()
	token = models.CharField(max_length=100)

class Tab(models.Model):
	bar = models.ForeignKey('Bar', blank=True, null=True)
	amount = models.DecimalField(max_digits=8, decimal_places=2)
	# 'amount' will drain down as the tab is used, so we need to keep track
	# of the original amount
	total = models.DecimalField(max_digits=8, decimal_places=2)
	sender = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='sender')
	receiver = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='receiver', blank=True, null=True)
	email = models.EmailField(blank=True, null=True)
	source = models.CharField(max_length=100, null=True, blank=True, default='')
	accepted = models.BooleanField(default=False)
	created = models.DateTimeField(auto_now_add=True, auto_now=False)
	updated = models.DateTimeField(auto_now_add=False, auto_now=True)
	note = models.CharField(max_length=140, default='', null=True)
	# This holds the pre-authorization "Charge" token from Stripe
	# This assures us that the sender actually has the money
	# Note: Stripe puts a 7 day time limit on the charge so we need to expire
	# tabs
	charge = models.CharField(max_length=100, default='')

	@classmethod
	def new(cls, amount, email, source, user, request=None, note=None):
		# Authorize the payment
		charge = authorize_source(amount, user.customer.customer_id, source)
		if not charge:
			# The authorization failed
			raise Exception()
		tab = cls(total=amount, amount=amount, source=source, sender=user, note=note, email=email, charge=charge.get('id'))
		invite = None
		if user.email == email:
			# The user is buying themselves a tab
			tab.receiver = user
			tab.accepted = True
		else:
			# Figure out if this user is in the system
			users = User.objects.filter(email=email)
			if len(users) < 1:
				# There is no user with this email, send email
				invite = TabInvite(email=email, token=uuid.uuid4())
			else:
				tab.receiver = users[0]
		# At this point the tab is fully built out and we can save
		tab.save()
		# We still need to finish the invite if needed
		if invite:
			invite.tab = tab
			invite.save()
			if request:
				send_tab_invite(request, tab, invite)
		# Add the amount to the user's tab if the tab has been accepted
		if tab.accepted:
			user.profile.tab += tab.amount
			user.profile.save()
		return tab

class Sale(models.Model):
	amount = models.DecimalField(max_digits=8, decimal_places=2)
	bar = models.ForeignKey('Bar')
	customer = models.ForeignKey(settings.AUTH_USER_MODEL)
	tip = models.DecimalField(max_digits=8, decimal_places=2, default=0)
	created = models.DateTimeField(auto_now_add=True, auto_now=False)
	updated = models.DateTimeField(auto_now_add=False, auto_now=True)

	# def is_valid(self, tip):
	# 	ts = self.transaction_set.filter(processed=False)
	# 	if len(ts) > 1:
	# 		# There are more than 1 transactions still open
	# 		print 'more than 1 open transaction'
	# 	elif len(ts < 1):
	# 		# There are no open transactions, use the user's default_source
	# 		charge = charge_source(self.customer.customer.customer_id, self.customer.customer.default_source, self.bar.merchant.account_id)
	# 	else:
	# 		# Take the money from this transaction
	# 		print 'Take the money from this Transaction'

	def complete(self):
		ts = self.transaction_set.filter(processed=False)
		if len(ts) > 1:
			# There are more than 1 transactions still open
			print 'more than 1 open transaction'
		elif len(ts) < 1:
			# There are no open transactions, use the user's default_source
			charge = charge_source(self.customer.customer.customer_id, self.customer.customer.default_source, self.bar.merchant.account_id)
		else:
			# Take the money from this transaction
			t = ts[0]
			amount = None
			customer_id = None
			source = None
			account_id = self.bar.owner.merchant.account_id
			charge = None
			if t.tab:
				# This transaction has a tab and therefore has a max allowed amt
				if t.amount + self.tip <= t.tab.amount:
					# Adding the tip to this tab is still under the amount left
					# on the tab. Use the rest.
					t.amount += self.tip
					amount = t.amount
					customer_id = t.owner.customer.customer_id
					source = t.source
					t.process()
					t.save()
				else:
					# Adding the tip to this tab will cause the amount to be
					# greater than tab max. Use the rest of the tab, then create
					# another transaction.
					tip_left_over = t.amount + self.tip - t.tab.amount
					t.amount = t.tab.amount
					amount = t.amount
					t.process()
					t.save()
					transaction = Transaction(sale=self, owner=self.customer, source=self.owner.customer.default_source, amount=tip_left_over)
					if not transaction.is_valid():
						# The tip needs to be increased for this transaction
						return {'error': True, 'type': 'tip_too_low', 'deficit':settings.MIN_CARD_COST - tip_left_over}
			else:
				# This transaction does not have a tab, and therefore has no max
				# amount allowed
				t.amount += self.tip
				t.process()
				t.save()

class Transaction(models.Model):
	sale = models.ForeignKey('Sale', null=True, blank=True, default='')
	owner = models.ForeignKey(settings.AUTH_USER_MODEL)
	tab = models.ForeignKey('Tab', null=True, blank=True, default='')
	amount = models.DecimalField(max_digits=8, decimal_places=2)
	source = models.CharField(max_length=100, null=True, blank=True, default='')
	processed = models.BooleanField(default=False)
	charge = models.CharField(max_length=100, null=True, default='')
	created = models.DateTimeField(auto_now_add=True, auto_now=False)
	updated = models.DateTimeField(auto_now_add=False, auto_now=True)

	def process(self):
		charge = charge_source(self.amount, self.owner.customer.customer_id, self.source, self.sale.bar.owner.merchant.account_id, self.charge)
		self.processed = True
		# TODO: Account for failed charge
		return True

	def authorize(self):
		charge = authorize_source(self.amount, self.owner.customer.customer_id, self.source, self.sale.bar.owner.merchant.account_id)
		# TODO: Account for failed authorization
		self.charge = charge.get('id')
		return True

	def is_valid(self):
		return not (self.amount < settings.MIN_CARD_COST)

def authorize_source(amount, customer_id, source, recipient_id=None):
	try:
		charge = stripe.Charge.create(
			amount=int(amount * 100),
			currency='usd',
			customer=customer_id,
			source=source,
			capture=False,
			destination=recipient_id,
			application_fee=get_application_fee(amount) if recipient_id else None
		)
		return charge
		# return {'id': '13425432456'}
	except stripe.error.CardError, e:
		# Since it's a decline, stripe.error.CardError will be caughtbody = e.json_body
	  	err  = e.json_body['error']
		return err
	except stripe.error.RateLimitError, e:
		# Too many requests made to the API too quickly
	  	err  = e.json_body['error']
		return err
	except stripe.error.InvalidRequestError, e:
		# Invalid parameters were supplied to Stripe's API
	  	err  = e.json_body['error']
		return err
	except stripe.error.AuthenticationError, e:
		# Authentication with Stripe's API failed
  		# (maybe you changed API keys recently)
	  	err  = e.json_body['error']
		return err
	except stripe.error.APIConnectionError, e:
		# Network communication with Stripe failed
	  	err  = e.json_body['error']
		return err
	except stripe.error.StripeError, e:
		# Display a very generic error to the user, and maybe send
  		# yourself an email
	  	err  = e.json_body['error']
		return err
	except Exception, e:
		# Something else happened
	  	err  = e.json_body['error']
		return err

def charge_source(amount, customer_id, source, recipient_id, charge=None):
	application_fee = get_application_fee(amount)
	amount = int(amount * 100)
	if not charge:
		# This is not a preauthorized charge
		charge = stripe.Charge.create(
			amount=amount,
			currency='usd',
			customer=customer_id,
			source=source,
			description='Charge for tab',
			destination=recipient_id,
			application_fee=application_fee
		)
	else:
		charge = stripe.Charge.retrieve(charge)
		charge = charge.capture()
	# TODO: Send notification to this user!
	return charge

def get_application_fee(amount):
	return int(float(amount) * 0.1 * 100.00)

class Role(models.Model):
	bar = models.ForeignKey('Bar')
	user = models.ForeignKey(settings.AUTH_USER_MODEL)
	# Comma separated list of roles: "admin, manager, bartender"
	ADMIN = 0
	MANAGER = 1
	BARTENDER = 2
	roles = models.CharField(max_length=100)
	created = models.DateTimeField(auto_now_add=True, auto_now=False)
	updated = models.DateTimeField(auto_now_add=False, auto_now=True)

	@property
	def roles_array(self):
		return self.roles.split(',')
