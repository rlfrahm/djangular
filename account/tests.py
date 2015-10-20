from django.test import TestCase
import datetime
from django.contrib.auth.models import User

from .models import UserProfile

# Create your tests here.
class AccountTests(TestCase):

    def test_account_create(self):
        """
        Ensure we can create a user profile
        """
        email = 'bob@localhost.com'
        password = 'password'
        firstname = 'Bob'
        lastname = 'Dyllan'
        dob = datetime.datetime.now()
        user = User.objects.create_user(email, email, password)
        user.first_name = firstname
        user.last_name = lastname
        user.save()

        up = UserProfile(user=user, dob=dob, active=False)
        up.save()
        self.assertIsNotNone(up.pk)
