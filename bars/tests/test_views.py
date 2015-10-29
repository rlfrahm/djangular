from django.test import TestCase
from django.core.urlresolvers import reverse
from django.utils import timezone
from django.contrib.auth.models import Group

import datetime, mock

from account.models import UserProfile

from .models import TabInvite, Tab

email = 'bill@localhost.com'
password = 'password'
@mock.patch('account.models.stripe')
def create_user(mock_stripe):
    mock_stripe.Customer.create.return_value = {'id': '13542lknlknlkn'}
    return UserProfile.new(email, password, 'Bill', 'Black', '2015-10-26')

class BarsTests(TestCase):

    # def setUp(self):
    #     print ''

    @mock.patch('bars.models.authorize_source')
    def test_tab_invite_use(self, mock_authorize_source):
        """
        Ensure TabInvite's can be used by navigating to the url
        """
        mock_authorize_source.return_value = {'id': '1234'}
        user = create_user()
        token = '123'
        amount = 20
        e = 'j@j.com'
        tab = Tab.new(amount, e, user.customer.default_source, user)
        invite = TabInvite(email=email, token=token, tab=tab)
        url = reverse('bars:tab-invite', args=(token,))
