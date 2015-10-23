from django.core.urlresolvers import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from django.contrib.auth.models import User
from django.contrib.auth.models import Group

from bars.models import Bar
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

    @mock.patch('api.views.authorize_source')
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

    @mock.patch('api.views.authorize_source')
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
    @mock.patch('api.views.authorize_source')
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

    # TODO: Test tab authorize_source failed
    @mock.patch('api.views.authorize_source')
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
        self.assertIsNotNone(response.data.get('id'))
        self.assertEqual(response.data.get('receiver'), self.user.pk)
        self.assertEqual(response.data.get('amount'), d['amount'])
    # TODO: Test tab amount less than minimum

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

    # @mock.patch('bars.models.authorize_source')
    # @mock.patch('bars.models.charge_source')
    # def test_bar_payment_user_uses_someone_elses_tab(self, mock_bar_models_charge_source, mock_bar_models_authorize_source):
    #     """
    #     Ensure that a user's card is used when they don't have tabs
    #     For this test you need:
    #     - A bar
    #     - A user
    #     """
    #     self.user.customer.default_source = '123'
    #     self.user.customer.save()
    #     mock_bar_models_authorize_source.return_value = {'id': 'jnsdflkgj34r'}
    #     mock_bar_models_charge_source.return_value = {'id': 'jnsdflkgj34r'}
    #     url = reverse('api:bar-pay', args=(1,))
    #     d = {
    #         'amount': 10
    #     }
    #     response = self.client.post(url, d, format='json')
    #     self.assertEqual(len(response.data.get('transactions')), 1)
    #     self.assertIsNotNone(response.data.get('sale'))
    #     self.assertEqual(response.data.get('tab'), 0)
    #     transactions = response.data.get('transactions')
    #     self.assertEqual(transactions[0]['status'], 'authorized')
