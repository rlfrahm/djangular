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
        user = UserProfile.create(email, password, firstname, lastname, dob)
        user.save()
        # Create a bar
    def test_bar_payment_with_tab(self):
        """
        Ensure we can create a bar payment using a tab
        """
