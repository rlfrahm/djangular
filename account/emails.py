from django.core.mail import EmailMessage
from django.core.urlresolvers import reverse
from django.conf import settings

def send_password_reset_email(request, token):
    msg = EmailMessage()
    msg.subject = 'Password Reset for My Drink Nation'
    msg.body = """
    You recently requested to reset your password. To do so, simply follow the link below:

    %s

    Thanks,
    The My Drink Nation team
    %s
    """ % (request.build_absolute_uri(reverse('user:reset-password', args=(token.token,))), request.build_absolute_uri(reverse('core:home')))
    msg.from_email = settings.EMAIL_FROM_EMAIL
    msg.to = [token.user.email]
    msg.send()
    return msg

def send_account_activate_email(request, token):
    msg = EmailMessage()
    msg.subject = 'Thanks for signing up for My Drink Nation'
    msg.body = """
    Your newly created account is ready to be activated. To activate, simply follow the link below:

    %s

    Note: If you forgo activation for too long, you run the risk of your account being suspended.

    Thanks,
    The My Drink Nation team
    %s
    """ % (request.build_absolute_uri(reverse('user:activate', args=(token.token,))), request.build_absolute_uri(reverse('core:home')))
    msg.from_email = settings.EMAIL_FROM_EMAIL
    msg.to = [token.user.email]
    msg.send()
    return msg
