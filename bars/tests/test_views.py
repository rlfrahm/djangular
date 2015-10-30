from django.test import TestCase
from django.core.urlresolvers import reverse
from django.utils import timezone
from django.contrib.auth.models import Group

import datetime, mock

from account.models import UserProfile

from bars.models import TabInvite, Tab

email = 'bill@localhost.com'
password = 'password'
def create_user():
    return UserProfile.new(email, password, 'Bill', 'Black', '2015-10-26')

class BarsTests(TestCase):

    @mock.patch('account.models.stripe')
    def setUp(self, mock_stripe):
        mock_stripe.Customer.create.return_value = {'id': '13542lknlknlkn'}
        # Create groups
        group = Group(name='Bar Owners')
        group.save()
        g = Group(name='Drinkers')
        g.save()

    @mock.patch('bars.models.authorize_source')
    def test_tab_invite_login_redirect(self, mock_authorize_source):
        """
        Ensure TabInvite view requires login
        """
        mock_authorize_source.return_value = {'id': '1234'}
        user = create_user()
        token = '123'
        amount = 20
        e = 'j@j.com'
        tab = Tab.new(amount, e, user.customer.default_source, user)
        invite = TabInvite(email=email, token=token, tab=tab)
        # u = UserProfile.new(e, 'password', 'J', 'J', '2015-10-26')
        url = reverse('bars:tab-invite', args=(token,))
        response = self.client.get(url, format='json')
        redirect = 'next=' + url
        self.assertTrue(url in response.get('location'))

    # @mock.patch('bars.models.authorize_source')
    # def test_tab_invite_use(self, mock_authorize_source):
    #     """
    #     Ensure TabInvite view requires login
    #     """
    #     mock_authorize_source.return_value = {'id': '1234'}
    #     user = create_user()
    #     token = '123'
    #     amount = 20
    #     e = 'j@j.com'
    #     tab = Tab.new(amount, e, user.customer.default_source, user)
    #     invite = TabInvite(email=email, token=token, tab=tab)
    #     u = UserProfile.new(e, 'password', 'J', 'J', '2015-10-26')
    #     self.client.login(email=e, password='password')
    #     url = reverse('bars:tab-invite', args=(token,))
    #     response = self.client.get(url, format='json')
    #     self.assertFalse(TabInvite.objects.filter().exists())
