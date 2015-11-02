from django.test import TestCase
from django.core.urlresolvers import reverse
from django.utils import timezone
from django.contrib.auth.models import Group
from django.conf import settings

import datetime, mock

from account.models import UserProfile

from bars.models import TabInvite, Tab, Transaction, Sale, charge_source

class Charge(object):
	id = '1234'

	def capture(self):
		return {'id': self.id, 'captured': True}

	def create(self):
		return {'id': self.id, 'captured': False}

class BarModelsTests(TestCase):

	# TODO: test that we can add a tip to a sale
	# TODO: test that a tip returns a need for more if the transaction is less
	# than the minimum

	@mock.patch('bars.models.stripe.Charge')
	def test_charge_source_preauthorized(self, mock_stripe_charge):
		"""
		Ensure that charge_source uses a preauthorized charge
		"""
		mock_stripe_charge.retrieve.return_value = Charge()
		charge = charge_source(20, '123', '123', '123', '123')
		self.assertTrue(charge.get('captured'))

	@mock.patch('bars.models.stripe.Charge')
	def test_charge_source_new(self, mock_stripe_charge):
		"""
		Ensure that a new charge is created
		"""
		mock_stripe_charge.create.return_value = {'captured': False}
		charge = charge_source(20, '123', '123', '123')
		self.assertFalse(charge.get('captured'))

	def test_transaction_is_valid(self):
		"""
		Ensure that 'is_valid' returns correctly for a transaction
		"""
		t = Transaction(amount=settings.MIN_CARD_COST - 0.01)
		self.assertFalse(t.is_valid())
		t.amount = settings.MIN_CARD_COST
		self.assertTrue(t.is_valid())

	def test_sale_complete_uses_tab(self):
		"""
		Ensure
		Need:
		- A bar
		- A tab
		- A sale
		- A transaction
		"""
		print ''
