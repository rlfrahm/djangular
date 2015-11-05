from django.test import TestCase
from django.core.urlresolvers import reverse
from django.utils import timezone
from django.contrib.auth.models import Group
from django.conf import settings

import datetime, mock

from account.models import UserProfile, StripeMerchant

from bars.models import TabInvite, Tab, Transaction, Sale, charge_source, Bar
from bars.exceptions import MinimumAmountError

email = 'bill@localhost.com'
password = 'password'
def create_user():
	return UserProfile.new(email, password, 'Bill', 'Black', '2015-10-26')

class Charge(object):
	id = '1234'

	def capture(self):
		return {'id': self.id, 'captured': True}

	def create(self):
		return {'id': self.id, 'captured': False}

class BarModelsTests(TestCase):

	@mock.patch('account.models.stripe')
	def setUp(self, mock_stripe):
		mock_stripe.Customer.create.return_value = {'id': '13542lknlknlkn'}
		# Create groups
		group = Group(name='Bar Owners')
		group.save()
		g = Group(name='Drinkers')
		g.save()

	# TODO: test that we can add a tip to a sale
	# TODO: test that a tip returns a need for more if the transaction is less
	# than the minimum
	# TODO: test that charges for amounts less than the minimum are rejected

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

	# TODO: Do we need to handle this case?
	@mock.patch('bars.models.charge_source')
	def test_sale_complete_uses_1_new_transaction(self, mock_bar_models_charge_source):
		"""
		Ensure the when there are no transactions for a Sale, a new transaction
		is created
		"""
		mock_bar_models_charge_source.return_value = {'id': 'jnsdflkgj34r'}
		user = create_user()
		d = {
			'street': '123 Street',
			'city': 'Des Moines',
			'province': 'IA',
			'postal': '50305',
			'country': 'US',
			'lat': 41.0,
			'lng': -91.0,
		}
		bar = Bar.new('Test Bar 1', d, user)
		m = StripeMerchant(user=user, account_id='123', pub_key='123', refresh_token='123', access_token='123')
		m.save()
		sale = Sale(amount=20, bar=bar, customer=user, tip=4)
		sale.complete()
		self.assertEqual(Sale.COMPLETE_STATUS, sale.status)
		ts = Transaction.objects.filter().exists()
		self.assertTrue(ts)

	@mock.patch('bars.models.authorize_source')
	@mock.patch('bars.models.charge_source')
	def test_sale_complete_uses_user_source_on_existing_transaction(self, mock_bar_models_charge_source, mock_bar_models_authorize_source):
		"""
		Ensure when a drinker pays for a drink using their own money, the tip
		is just added onto that transaction
		"""
		mock_bar_models_authorize_source.return_value = {'id': 'jnsdflkgj34r'}
		mock_bar_models_charge_source.return_value = {'id': 'jnsdflkgj34r'}
		user = create_user()
		u2 = UserProfile.new('jo@jo.com', 'password', 'Bill', 'Black', '2015-10-26')
		d = {
			'street': '123 Street',
			'city': 'Des Moines',
			'province': 'IA',
			'postal': '50305',
			'country': 'US',
			'lat': 41.0,
			'lng': -91.0,
		}
		bar = Bar.new('Test Bar 1', d, user)
		m = StripeMerchant(user=user, account_id='123', pub_key='123', refresh_token='123', access_token='123')
		m.save()
		sale = Sale(amount=20, bar=bar, customer=user, tip=4)
		sale.save()
		t1 = Transaction(sale=sale, owner=user, source=u2.customer.default_source, amount=20)
		t1.save()
		sale.complete()
		self.assertEqual(Sale.COMPLETE_STATUS, sale.status)
		transactions = Transaction.objects.all()
		self.assertEqual(len(transactions), 1)
		self.assertTrue(transactions[0].processed)
		self.assertEqual(transactions[0].amount, 24)

	@mock.patch('bars.models.authorize_source')
	@mock.patch('bars.models.charge_source')
	def test_sale_complete_only_uses_tab(self, mock_bar_models_charge_source, mock_bar_models_authorize_source):
		"""
		Ensure that the rest of a tab is used when adding a tip
		Scenario: User has tab of $25. User buys drink for $20. User adds tip
		of $5. Total sale is $25 and can all come from the tab.
		"""
		mock_bar_models_authorize_source.return_value = {'id': 'jnsdflkgj34r'}
		mock_bar_models_charge_source.return_value = {'id': 'jnsdflkgj34r'}
		user = create_user()
		u2 = UserProfile.new('jo@jo.com', 'password', 'Bill', 'Black', '2015-10-26')
		d = {
			'street': '123 Street',
			'city': 'Des Moines',
			'province': 'IA',
			'postal': '50305',
			'country': 'US',
			'lat': 41.0,
			'lng': -91.0,
		}
		bar = Bar.new('Test Bar 1', d, user)
		m = StripeMerchant(user=user, account_id='123', pub_key='123', refresh_token='123', access_token='123')
		m.save()
		tab = Tab.new(25.00, user.email, 'ijbwflgkbsdf', u2)
		sale = Sale(amount=20, bar=bar, customer=user, tip=5)
		sale.save()
		t1 = Transaction(sale=sale, owner=user, source=u2.customer.default_source, amount=20, tab=tab)
		t1.save()
		sale.complete()
		self.assertEqual(Sale.COMPLETE_STATUS, sale.status)
		transactions = Transaction.objects.all()
		self.assertEqual(len(transactions), 1)
		self.assertTrue(transactions[0].processed)
		self.assertEqual(transactions[0].amount, 25)
		self.assertIsNotNone(transactions[0].tab)

	@mock.patch('bars.models.authorize_source')
	@mock.patch('bars.models.charge_source')
	def test_sale_complete_uses_tab_users_source(self, mock_bar_models_charge_source, mock_bar_models_authorize_source):
		"""
		Ensure that there are two transactions if a tab is completely used
		Scenario: User has tab of $20. User buys drink for $20. User adds tip
		of $5. Total sale is $25 and there are two transactions, one from the tab
		and one from the user.
		"""
		mock_bar_models_authorize_source.return_value = {'id': 'jnsdflkgj34r'}
		mock_bar_models_charge_source.return_value = {'id': 'jnsdflkgj34r'}
		user = create_user()
		u2 = UserProfile.new('jo@jo.com', 'password', 'Bill', 'Black', '2015-10-26')
		d = {
			'street': '123 Street',
			'city': 'Des Moines',
			'province': 'IA',
			'postal': '50305',
			'country': 'US',
			'lat': 41.0,
			'lng': -91.0,
		}
		bar = Bar.new('Test Bar 1', d, user)
		m = StripeMerchant(user=user, account_id='123', pub_key='123', refresh_token='123', access_token='123')
		m.save()
		tab = Tab.new(20.00, user.email, 'ijbwflgkbsdf', u2)
		sale = Sale(amount=19, bar=bar, customer=user, tip=6)
		sale.save()
		t1 = Transaction(sale=sale, owner=user, source=u2.customer.default_source, amount=19, tab=tab)
		t1.save()
		sale.complete()
		self.assertEqual(Sale.COMPLETE_STATUS, sale.status)
		transactions = Transaction.objects.all()
		self.assertEqual(len(transactions), 2)
		self.assertTrue(transactions[0].processed)
		self.assertEqual(transactions[0].amount, 20)
		self.assertIsNotNone(transactions[0].tab)
		self.assertTrue(transactions[1].processed)
		self.assertEqual(transactions[1].amount, 5)
		self.assertIsNone(transactions[1].tab)

	@mock.patch('bars.models.authorize_source')
	@mock.patch('bars.models.charge_source')
	def test_sale_complete_uses_tab_users_source(self, mock_bar_models_charge_source, mock_bar_models_authorize_source):
		"""
		Ensure that if a second transaction needs to happen, a tip fails if it
		is under the minimum transaction amount
		Scenario: User has tab of $20. User buys drink for $20. User adds tip
		of $4, but the minimum sale amount is $5. Total sale is $24 and there are two transactions, one from the tab
		and one from the user. The sale should be rejected.
		"""
		mock_bar_models_authorize_source.return_value = {'id': 'jnsdflkgj34r'}
		mock_bar_models_charge_source.return_value = {'id': 'jnsdflkgj34r'}
		user = create_user()
		u2 = UserProfile.new('jo@jo.com', 'password', 'Bill', 'Black', '2015-10-26')
		d = {
			'street': '123 Street',
			'city': 'Des Moines',
			'province': 'IA',
			'postal': '50305',
			'country': 'US',
			'lat': 41.0,
			'lng': -91.0,
		}
		bar = Bar.new('Test Bar 1', d, user)
		m = StripeMerchant(user=user, account_id='123', pub_key='123', refresh_token='123', access_token='123')
		m.save()
		tab = Tab.new(20.00, user.email, 'ijbwflgkbsdf', u2)
		sale = Sale(amount=19, bar=bar, customer=user, tip=5)
		sale.save()
		t1 = Transaction(sale=sale, owner=user, source=u2.customer.default_source, amount=19, tab=tab)
		t1.save()
		try:
			sale.complete()
		except MinimumAmountError, e:
			self.assertTrue(True)
		self.assertEqual(Sale.PENDING_STATUS, sale.status)
		transactions = Transaction.objects.all()
		self.assertEqual(len(transactions), 1)
		self.assertFalse(transactions[0].processed)
		self.assertEqual(transactions[0].amount, 19)
		self.assertIsNotNone(transactions[0].tab)
