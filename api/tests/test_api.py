from django.core.urlresolvers import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from django.conf import settings

from bars.models import Bar, Tab, Checkin
from account.models import UserProfile, StripeMerchant

import datetime, mock, stripe

# Create your tests here.
class ApiTests(APITestCase):

    # @mock.patch('account.models.StripeCustomer')
    @mock.patch('account.models.stripe')
    @mock.patch('bars.models.authorize_source')
    @mock.patch('bars.models.charge_source')
    def setUp(self, mock_bar_models_authorize_source, mock_bar_models_charge_source, mock_account_models_stripe):
        # mock_account_models_customer.default_source = '123'
        mock_account_models_stripe.Customer.create.return_value = {'id': '13542lknlknlkn'}
        # Create groups
        group = Group(name='Bar Owners')
        group.save()
        g = Group(name='Drinkers')
        g.save()
        # Create a user
        email = 'bob@localhost.com'
        password = 'password'
        self.firstname = 'Bob'
        self.lastname = 'Dyllan'
        self.dob = datetime.datetime.now()
        self.user = UserProfile.new(email, password, self.firstname, self.lastname, self.dob)
        self.user.groups.add(group)
        self.client = APIClient(enforce_csrf_checks=True)
        self.client.force_authenticate(user=self.user)
        d = {
            'street': '123 Street',
            'city': 'Des Moines',
            'province': 'IA',
            'postal': '50305',
            'country': 'US',
            'lat': 41.0,
            'lng': -91.0,
        }
        bar = Bar.new('Test Bar 1', d, self.user)
        bar.save()
        m = StripeMerchant(user=self.user, account_id='123', pub_key='123', refresh_token='123', access_token='123')
        m.save()

    def test_user_get_profile(self):
        url = reverse('api:user-profile', args=(1,))
        response = self.client.get(url, format='json')
        self.assertIs(response.data.get('id'), 1)
        self.assertEqual(response.data.get('first_name'), self.firstname)
        self.assertEqual(response.data.get('last_name'), self.lastname)
        self.assertIsInstance(response.data.get('checkins'), list)

    def test_user_change_password(self):
        url = reverse('api:user-password')
        d = {
            'password': ';kjsdbfgskjsdbfg'
        }
        response = self.client.post(url, d, format='json')
        self.assertIs(response.data.get('success'), True)

    def test_bar_create(self):
        url = reverse('api:bars')
        d = {
            'name': 'Test bar 2',
            'street': '123 Street',
            'city': 'Des Moines',
            'province': 'IA',
            'postal': '50305',
            'country': 'US',
            'lat': 41.0,
            'lng': -91.0,
        }
        response = self.client.post(url, d, format='json')
        self.assertFalse(response.data.get('error'))

    def test_bar_get(self):
        """
        Ensure we can get a bar
        """
        url = reverse('api:bar', args=(1,))
        response = self.client.get(url, format='json')
        self.assertIs(response.data.get('id'), 1)

    def test_bar_get_list(self):
        """
        Ensure we can get a list of bars
        """
        url = reverse('api:bars')
        response = self.client.get(url, format='json')
        self.assertIsInstance(response.data, list)

    @mock.patch('bars.models.authorize_source')
    def test_tab_create_for_myself(self, mock_bar_models_authorize_source):
        """
        Ensure we can create a tab for ourselves
        """
        url = reverse('api:tabs')
        d = {
            'amount': 20,
            'source': '123',
            'email': self.user.email,
            'note': 'Testy test notes!'
        }
        mock_bar_models_authorize_source.return_value = {'id': 'jnsdflkgj34r'}
        response = self.client.post(url, d, format='json')
        self.assertIsNotNone(response.data.get('id'))
        self.assertEqual(response.data.get('receiver'), self.user.pk)
        self.assertEqual(response.data.get('amount'), d['amount'])

    @mock.patch('bars.models.authorize_source')
    def test_tab_create_for_another_user(self, mock_bar_models_authorize_source):
        """
        Ensure we can create a tab for another registered user
        """
        # Create another user
        user = UserProfile.new('user@localhost.com', 'password', 'Ryan', 'Frahm', datetime.datetime.now())
        user.groups.add(Group.objects.filter(name='Drinkers')[0])
        url = reverse('api:tabs')
        d = {
            'amount': 20,
            'source': '123',
            'email': user.email,
            'note': 'Testy test notes!'
        }
        mock_bar_models_authorize_source.return_value = {'id': 'jnsdflkgj34r'}
        response = self.client.post(url, d, format='json')
        self.assertIsNotNone(response.data.get('id'))
        self.assertEqual(response.data.get('receiver'), 2)
        self.assertEqual(response.data.get('amount'), d['amount'])

    @mock.patch('bars.models.send_tab_invite')
    @mock.patch('bars.models.authorize_source')
    def test_tab_create_for_someone_else(self, mock_bar_models_authorize_source, mock_bar_models_send_tab_invite):
        """
        Ensure we can create a tab for another user that is NOT registered
        """
        url = reverse('api:tabs')
        d = {
            'amount': 20,
            'source': '123',
            'email': 'email@localhost.com',
            'note': 'Testy test notes!'
        }
        mock_bar_models_authorize_source.return_value = {'id': 'jnsdflkgj34r'}
        response = self.client.post(url, d, format='json')
        self.assertIsNotNone(response.data.get('id'))
        self.assertEqual(response.data.get('email'), d['email'])
        self.assertEqual(response.data.get('amount'), d['amount'])

    @mock.patch('bars.models.authorize_source')
    def test_tab_authorize_failed(self, mock_bar_models_authorize_source):
        """
        Ensure that tab creation fails gently when card authorization fails
        """
        url = reverse('api:tabs')
        d = {
            'amount': 20,
            'source': '123',
            'email': self.user.email,
            'note': 'Testy test notes!'
        }
        err = {}
        mock_bar_models_authorize_source.return_value = err
        response = self.client.post(url, d, format='json')
        self.assertEqual(response.data.get('status'), 400)

    @mock.patch('bars.models.authorize_source')
    def test_tab_less_than_minimum(self, mock_bar_models_authorize_source):
        """
        Ensure that the tab is denied when the amount is less than our minimum
        """
        url = reverse('api:tabs')
        d = {
            'amount': settings.MIN_CARD_COST - 0.01,
            'source': '123',
            'email': self.user.email,
            'note': 'Testy test notes!'
        }
        mock_bar_models_authorize_source.return_value = {'id': 'jnsdflkgj34r'}
        response = self.client.post(url, d, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIsNotNone(response.data.get('amount'))

    @mock.patch('bars.models.authorize_source')
    @mock.patch('bars.models.charge_source')
    def test_bar_payment_less_than_minimum(self, mock_bar_models_charge_source, mock_bar_models_authorize_source):
        """
        Ensure that a payment less than the payment is less than minimum
        For this test you need:
        - A bar
        - A user
        """
        self.user.customer.default_source = '123'
        self.user.customer.save()
        mock_bar_models_authorize_source.return_value = {'id': 'jnsdflkgj34r'}
        mock_bar_models_charge_source.return_value = {'id': 'jnsdflkgj34r'}
        url = reverse('api:bar-pay', args=(1,))
        d = {
            'amount': settings.MIN_CARD_COST - 0.01
        }
        response = self.client.post(url, d, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIsNotNone(response.data.get('amount'))

    @mock.patch('bars.models.authorize_source')
    @mock.patch('bars.models.charge_source')
    def test_bar_payment_user_pays_their_own_bill(self, mock_bar_models_charge_source, mock_bar_models_authorize_source):
        """
        Ensure that a user's card is used when they don't have tabs
        For this test you need:
        - A bar
        - A user
        """
        self.user.customer.default_source = '123'
        self.user.customer.save()
        mock_bar_models_authorize_source.return_value = {'id': 'jnsdflkgj34r'}
        mock_bar_models_charge_source.return_value = {'id': 'jnsdflkgj34r'}
        url = reverse('api:bar-pay', args=(1,))
        d = {
            'amount': 10
        }
        response = self.client.post(url, d, format='json')
        self.assertEqual(len(response.data.get('transactions')), 1)
        self.assertIsNotNone(response.data.get('sale'))
        self.assertEqual(response.data.get('tab'), 0)
        transactions = response.data.get('transactions')
        self.assertEqual(transactions[0]['status'], 'authorized')

    @mock.patch('bars.models.authorize_source')
    @mock.patch('bars.models.charge_source')
    def test_bar_payment_user_uses_tab(self, mock_bar_models_charge_source, mock_bar_models_authorize_source):
        """
        Ensure that a user's tab is used if they have one
        For this test you need:
        - A bar
        - A user
        - A tab
        """
        self.user.customer.default_source = '123'
        self.user.customer.save()
        mock_bar_models_authorize_source.return_value = {'id': 'jnsdflkgj34r'}
        mock_bar_models_charge_source.return_value = {'id': 'jnsdflkgj34r'}
        # Create a tab
        tab = Tab.new(20.00, self.user.email, 'ijbwflgkbsdf', self.user)
        url = reverse('api:bar-pay', args=(1,))
        amount = 10
        d = {
            'amount': amount
        }
        response = self.client.post(url, d, format='json')
        self.assertEqual(len(response.data.get('transactions')), 1)
        self.assertIsNotNone(response.data.get('sale'))
        # The user's tab should now be $10
        self.assertEqual(response.data.get('tab'), amount)
        transactions = response.data.get('transactions')
        self.assertEqual(transactions[0]['status'], 'authorized')
        self.assertEqual(transactions[0]['amount'], amount)

    @mock.patch('bars.models.authorize_source')
    @mock.patch('bars.models.charge_source')
    def test_bar_payment_returns_notification_of_more_money_needed(self, mock_bar_models_charge_source, mock_bar_models_authorize_source):
        """
        Ensure that a user's tab is used if they have one
        For this test you need:
        - A bar
        - A user
        - A tab
        """
        self.user.customer.default_source = '123'
        self.user.customer.save()
        mock_bar_models_authorize_source.return_value = {'id': 'jnsdflkgj34r'}
        mock_bar_models_charge_source.return_value = {'id': 'jnsdflkgj34r'}
        # Create a tab
        tab = Tab.new(20.00, self.user.email, 'ijbwflgkbsdf', self.user)
        url = reverse('api:bar-pay', args=(1,))
        amount = 21
        d = {
            'amount': amount
        }
        response = self.client.post(url, d, format='json')
        # The user's tab should now be $10
        transactions = response.data.get('transactions')
        self.assertEqual(transactions[1]['amount_needed'], settings.MIN_CARD_COST - 1)
        self.assertTrue(transactions[1]['error'])

    @mock.patch('bars.models.authorize_source')
    @mock.patch('bars.models.charge_source')
    def test_bar_payment_user_uses_2_tabs(self, mock_bar_models_charge_source, mock_bar_models_authorize_source):
        """
        Ensure that a user's 2 tabs are used if they have one
        For this test you need:
        - A bar
        - A user
        - A tab
        """
        self.user.customer.default_source = '123'
        self.user.customer.save()
        mock_bar_models_authorize_source.return_value = {'id': 'jnsdflkgj34r'}
        mock_bar_models_charge_source.return_value = {'id': 'jnsdflkgj34r'}
        # Create a tab
        tab1 = Tab.new(20.00, self.user.email, 'ijbwflgkbsdf', self.user)
        tab2 = Tab.new(20.00, self.user.email, 'ijbwflgkbsdf', self.user)
        url = reverse('api:bar-pay', args=(1,))
        amount = 30
        d = {
            'amount': amount
        }
        response = self.client.post(url, d, format='json')
        self.assertEqual(len(response.data.get('transactions')), 2)
        self.assertIsNotNone(response.data.get('sale'))
        # The user's tab should now be $10
        self.assertEqual(response.data.get('tab'), 10)
        transactions = response.data.get('transactions')
        self.assertEqual(transactions[0]['status'], 'charged')
        self.assertEqual(transactions[0]['amount'], 20.00)
        self.assertEqual(transactions[1]['status'], 'authorized')
        self.assertEqual(transactions[1]['amount'], 10.00)

    @mock.patch('bars.models.authorize_source')
    @mock.patch('bars.models.charge_source')
    def test_bar_payment_user_uses_only_accepted_tabs(self, mock_bar_models_charge_source, mock_bar_models_authorize_source):
        """
        Ensure that a payment only use tabs that have been accepted
        For this test you need:
        - A bar
        - A user
        - Another user
        - A tab created by each user
        """
        self.user.customer.default_source = '123'
        self.user.customer.save()
        mock_bar_models_authorize_source.return_value = {'id': 'jnsdflkgj34r'}
        mock_bar_models_charge_source.return_value = {'id': 'jnsdflkgj34r'}
        # Create another user
        user = UserProfile.new('user@localhost.com', 'password', 'Ryan', 'Frahm', datetime.datetime.now())
        user.groups.add(Group.objects.filter(name='Drinkers')[0])
        # Create a 2 tabs
        # This one should not be accepted
        tab2 = Tab.new(20.00, self.user.email, 'ijbwflgkbsdf', user)
        # This one should be automatically accepted
        tab1 = Tab.new(20.00, self.user.email, 'ijbwflgkbsdf', self.user)
        url = reverse('api:bar-pay', args=(1,))
        amount = 10
        d = {
            'amount': amount
        }
        response = self.client.post(url, d, format='json')
        self.assertEqual(len(response.data.get('transactions')), 1)
        self.assertIsNotNone(response.data.get('sale'))
        # The user's tab should now be $10
        self.assertEqual(response.data.get('tab'), 10)
        transactions = response.data.get('transactions')
        self.assertEqual(transactions[0]['status'], 'authorized')
        self.assertEqual(transactions[0]['amount'], 10.00)
        self.assertEqual(transactions[0]['tab_id'], tab1.pk)

    @mock.patch('bars.models.authorize_source')
    @mock.patch('bars.models.charge_source')
    def test_bar_payment_user_uses_tab_and_their_money(self, mock_bar_models_charge_source, mock_bar_models_authorize_source):
        """
        Ensure that a user's own money is used after a tab is depleted
        For this test you need:
        - A bar
        - A user
        - A tab
        """
        self.user.customer.default_source = '123'
        self.user.customer.save()
        mock_bar_models_authorize_source.return_value = {'id': 'jnsdflkgj34r'}
        mock_bar_models_charge_source.return_value = {'id': 'jnsdflkgj34r'}
        # Create a tab
        tab1 = Tab.new(20.00, self.user.email, 'ijbwflgkbsdf', self.user)
        url = reverse('api:bar-pay', args=(1,))
        amount = 30
        d = {
            'amount': amount
        }
        response = self.client.post(url, d, format='json')
        self.assertEqual(len(response.data.get('transactions')), 2)
        self.assertIsNotNone(response.data.get('sale'))
        # The user's tab should now be $10
        self.assertEqual(response.data.get('tab'), 0)
        transactions = response.data.get('transactions')
        self.assertEqual(transactions[0]['status'], 'charged')
        self.assertEqual(transactions[0]['amount'], 20.00)
        self.assertEqual(transactions[0]['type'], 'tab')
        self.assertEqual(transactions[1]['status'], 'authorized')
        self.assertEqual(transactions[1]['amount'], 10.00)
        self.assertEqual(transactions[1]['type'], 'user')

    @mock.patch('bars.models.authorize_source')
    @mock.patch('bars.models.charge_source')
    def test_bar_payment_tab_is_charged_when_used_fully(self, mock_bar_models_charge_source, mock_bar_models_authorize_source):
        """
        Ensure that a user's tab is used if they have one
        For this test you need:
        - A bar
        - A user
        - A tab
        """
        self.user.customer.default_source = '123'
        self.user.customer.save()
        mock_bar_models_authorize_source.return_value = {'id': 'jnsdflkgj34r'}
        mock_bar_models_charge_source.return_value = {'id': 'jnsdflkgj34r'}
        # Create a tab
        tab = Tab.new(20.00, self.user.email, 'ijbwflgkbsdf', self.user)
        url = reverse('api:bar-pay', args=(1,))
        amount = 20
        d = {
            'amount': amount
        }
        response = self.client.post(url, d, format='json')
        self.assertEqual(len(response.data.get('transactions')), 1)
        self.assertIsNotNone(response.data.get('sale'))
        # The user's tab should now be $10
        self.assertEqual(response.data.get('tab'), 0)
        transactions = response.data.get('transactions')
        self.assertEqual(transactions[0]['status'], 'charged')
        self.assertEqual(transactions[0]['amount'], amount)

    @mock.patch('bars.models.authorize_source')
    @mock.patch('bars.models.charge_source')
    def test_bar_payment_tab_is_authorized_when_only_partially_used(self, mock_bar_models_charge_source, mock_bar_models_authorize_source):
        """
        Ensure that a user's tab is used if they have one
        For this test you need:
        - A bar
        - A user
        - A tab
        """
        self.user.customer.default_source = '123'
        self.user.customer.save()
        mock_bar_models_authorize_source.return_value = {'id': 'jnsdflkgj34r'}
        mock_bar_models_charge_source.return_value = {'id': 'jnsdflkgj34r'}
        # Create a tab
        tab = Tab.new(20.00, self.user.email, 'ijbwflgkbsdf', self.user)
        url = reverse('api:bar-pay', args=(1,))
        amount = 10
        d = {
            'amount': amount
        }
        response = self.client.post(url, d, format='json')
        self.assertEqual(len(response.data.get('transactions')), 1)
        self.assertIsNotNone(response.data.get('sale'))
        # The user's tab should now be $10
        self.assertEqual(response.data.get('tab'), amount)
        transactions = response.data.get('transactions')
        self.assertEqual(transactions[0]['status'], 'authorized')
        self.assertEqual(transactions[0]['amount'], amount)

    @mock.patch('bars.models.authorize_source')
    @mock.patch('bars.models.charge_source')
    def test_bar_payment_tab_is_removed_if_lt_minimum(self, mock_bar_models_charge_source, mock_bar_models_authorize_source):
        """
        Ensure that a tab is staged to be removed if it is less than the minimum
        For this test you need:
        - A bar
        - A user
        - A tab
        """
        self.user.customer.default_source = '123'
        self.user.customer.save()
        mock_bar_models_authorize_source.return_value = {'id': 'jnsdflkgj34r'}
        mock_bar_models_charge_source.return_value = {'id': 'jnsdflkgj34r'}
        # Create a tab
        tabamt = 20.00
        tab = Tab.new(20.00, self.user.email, 'ijbwflgkbsdf', self.user)
        url = reverse('api:bar-pay', args=(1,))
        amount = tabamt - settings.MIN_CARD_COST + 0.01
        d = {
            'amount': amount
        }
        response = self.client.post(url, d, format='json')
        self.assertEqual(len(response.data.get('transactions')), 1)
        self.assertIsNotNone(response.data.get('sale'))
        # The user's tab should now be $10
        self.assertEqual(response.data.get('tab'), amount)
        transactions = response.data.get('transactions')
        self.assertEqual(transactions[0]['status'], 'authorized')
        self.assertEqual(float(transactions[0]['amount']), amount)
        self.assertEqual(len(response.data.get('removed')), 1)

    def test_bar_checkin(self):
        """
        Ensure that we can checkin to a bar
        """
        url = reverse('api:bar-checkin', args=(1,))
        response = self.client.post(url, format='json')
        self.assertEqual(response.data.get('id'), 1)
        self.assertEqual(response.data.get('user'), self.user.pk)
        self.assertIsNotNone(response.data.get('when'))
        self.assertEqual(response.data.get('bar'), 1)

    def test_bar_checkin_get(self):
        """
        Ensure that we can get checkins at a bar
        """
        url = reverse('api:bar-checkin', args=(1,))
        c1 = Checkin.new(1, self.user)
        c2 = Checkin.new(1, self.user)
        response = self.client.get(url, format='json')
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['user'], self.user.pk)
        self.assertEqual(response.data[1]['user'], self.user.pk)
