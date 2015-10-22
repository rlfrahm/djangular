from django.core.urlresolvers import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from django.contrib.auth.models import User
from django.contrib.auth.models import Group

from bars.models import Bar
from account.models import UserProfile

import datetime

# Create your tests here.
class ApiTests(APITestCase):
    def setUp(self):
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
        self.user = UserProfile.new(email, password, self.firstname, self.lastname, self.dob, add_stripe=False)
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

    def test_tab_create(self):
        """
        Ensure we can create a bar payment using a tab
        """
        url = reverse('api:tabs')
        return True
