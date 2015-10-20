from django.core.urlresolvers import reverse
from rest_framework import status
from rest_framework.test import APITestCase

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

    def test_bar_create(self):
        name = 'Test bar 1'
        location = {
            'street': '123 Street',
            'city': 'Des Moines',
            'province': 'IA',
            'postal': '50305',
            'country': 'US',
            'lat': 111.0
            'lng': -91.0
        }
        self.bar = Bar.new(name, location)
        self.assertIsNotNone(self.bar)
        
    def test_bar_payment_with_tab(self):
        """
        Ensure we can create a bar payment using a tab
        """
        return True
