from django.core.urlresolvers import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from django.contrib.auth.models import User
from django.contrib.auth.models import Group

from bars.models import Bar
from account.models import UserProfile

import datetime

# Create your tests here.
class BarsTests(APITestCase):
    def setup(self):
        # Create a user
        email = 'bob@localhost.com'
        password = 'password'
        firstname = 'Bob'
        lastname = 'Dyllan'
        dob = datetime.datetime.now()
        self.user = UserProfile.new(email, password, firstname, lastname, dob)
        print self.user
        client = APIClient(enforce_csrf_checks=True)
        client.force_authenticate(user=self.user)

    def test_bar_create(self):
        email = 'bob@localhost.com'
        username = email[:30]
        password = 'password'
        firstname = 'Bob'
        lastname = 'Dyllan'
        # dob = datetime.datetime.now()
        # self.user = UserProfile.new(email, password, firstname, lastname, dob)
        # print self.user
        user = User.objects.create_user(username, email, password)
        user.first_name = firstname
        user.last_name = lastname
        user.save()
        group = Group(name='Bar Owners')
        group.save()
        user.groups.add(group)
        client = APIClient(enforce_csrf_checks=True)
        client.force_authenticate(user=user)
        url = reverse('api:bars')
        d = {
            'name': 'Test bar 1',
            'street': '123 Street',
            'city': 'Des Moines',
            'province': 'IA',
            'postal': '50305',
            'country': 'US',
            'lat': 111.0,
            'lng': -91.0,
        }
        response = client.post(url, d, format='json')
        self.assertFalse(response.data.get('error'))

    def test_bar_payment_with_tab(self):
        """
        Ensure we can create a bar payment using a tab
        """
        return True
