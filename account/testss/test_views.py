from django.test import TestCase
from django.core.urlresolvers import reverse
from django.utils import timezone
from django.contrib.auth.models import Group

import datetime, mock

from account.models import UserProfile, PasswordResetToken, AccountActivationToken

email = 'bill@localhost.com'
password = 'password'
def create_user():
    return UserProfile.new(email, password, 'Bill', 'Black', '2015-10-26')

class UserAccountTests(TestCase):

    @mock.patch('account.views.send_password_reset_email')
    @mock.patch('account.views.send_account_activate_email')
    @mock.patch('account.models.stripe')
    def setUp(self, mock_account_models_stripe, mock_send_account_activate_email, mock_send_password_reset_email):
        # Create groups
        group = Group(name='Bar Owners')
        group.save()
        g = Group(name='Drinkers')
        g.save()
        mock_account_models_stripe.Customer.create.return_value = {'id': '13542lknlknlkn'}
        mock_send_password_reset_email.return_value = True
        mock_send_account_activate_email.return_value = True

    def test_user_registration(self):
        """
        Ensure that a user can be registered
        """
        url = reverse('user:register')
        d = {
            'email': 'bob@localhost.com',
            'password': 'password',
            'firstname': 'Bob',
            'lastname': 'Dyllan',
            'dob': '2015-10-26'
        }
        response = self.client.post(url, d, format='json')
        users = UserProfile.objects.all().exists()
        self.assertTrue(users)
        self.assertTrue(AccountActivationToken.objects.all().exists())

    def test_user_login(self):
        """
        Ensure that a user can be logged in
        """
        user = create_user()
        url = reverse('user:login')
        d = {
            'email': email,
            'password': password
        }
        response = self.client.post(url, d, format='json')
        self.assertEqual(int(self.client.session['_auth_user_id']), user.pk)

    def test_password_reset(self):
        """
        Ensure that a password reset token is created
        """
        url = reverse('user:reset-password-form')
        create_user()
        d = {'email': email}
        self.client.post(url, d, format='json')
        tokens = PasswordResetToken.objects.filter().exists()
        self.assertTrue(tokens)

    def test_password_reset_token(self):
        """
        Ensure that we can use a password reset token
        """
        user = create_user()
        prt = PasswordResetToken.new(user)
        url = reverse('user:reset-password', args=(prt.token,))
        response = self.client.get(url, format='json')
        self.assertEqual(int(self.client.session['_auth_user_id']), user.pk)
        prts = PasswordResetToken.objects.all().exists()
        self.assertFalse(prts)
