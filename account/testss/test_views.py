from django.test import TestCase
from django.core.urlresolvers import reverse

import datetime

from account.models import UserProfile

# class UserAccountTests(TestCase):
#
#     def test_user_registration(self):
#         """
#         Ensure that a user can be registered
#         """
#         url = reverse('user:register')
#         d = {
#             'email': 'bob@localhost.com',
#             'password': 'password',
#             'firstname': 'Bob',
#             'lastname': 'Dyllan',
#             'dob': datetime.datetime.now()
#         }
#         response = self.client.post(url, d, format='json')
#         users = UserProfile.objects.all()
#         print users
#         self.assertTrue(UserProfile.objects.all().exists())
