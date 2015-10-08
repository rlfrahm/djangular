from django.core.mail import EmailMessage
from django.core.urlresolvers import reverse
from django.conf import settings

def send_bartender_invite(request, invite):
  msg = EmailMessage()
  msg.subject = 'You have been invited to join %s' % invite.bar.name
  msg.body = """
  %s has invited you to join the My Drink Nation network!

  To accept this invitation, simply follow this link: %s.

  My Drink Nation helps people buy drinks for their friends. Come help make that happen!

  Thanks,
  The My Drink Nation team
  %s
  """ % (invite.bar.name, request.build_absolute_uri(reverse('bars:bartender-invite', args=(invite.bar.pk, invite.token,))), request.build_absolute_uri(reverse('core:home')))
  msg.from_email = settings.EMAIL_FROM_EMAIL
  msg.to = [invite.email]
  msg.send()
  return msg

def send_tab_invite(request, tab, invite):
  msg = EmailMessage()
  msg.subject = 'You have a $%0.00f tab waiting for you on My Drink nation' % tab.amount
  msg.body = """
  %s has opened a $%0.00f tab for you on My Drink Nation! This is money you can use to buy yourself a drink at a bar.

  To accept this invitation, simply follow this link: %s.

  My Drink Nation helps people buy drinks for their friends. Come join us!

  Thanks,
  The My Drink Nation team
  %s
  """ % (tab.sender.first_name, tab.amount, request.build_absolute_uri(reverse('bars:bartender-invite', args=(tab.pk, invite.token,))), request.build_absolute_uri(reverse('core:home')))
  msg.from_email = settings.EMAIL_FROM_EMAIL
  msg.to = [invite.email]
  msg.send()
  return msg

def send_us_bar_inquiry(request, name, bar_name, email, phone, license, comments):
  msg = EmailMessage()
  msg.subject = 'Bar Inquiry: %s' % bar_name
  msg.body = """
  Person: %s
  Bar: %s
  License # (last six): %s
  Email: %s
  Phone: %s
  Comments: %s
  """ % (name, bar_name, license, email, phone, comments)
  msg.from_email = settings.EMAIL_FROM_EMAIL
  msg.to = ['frahmryan@gmail.com']
  msg.send()
  return msg

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

def send_bar_creation_email(request, bar):
    msg = EmailMessage()
    msg.subject = 'Next steps for %s' % bar.name
    msg.body = """
    Thank you for registering your bar with My Drink Nation!

    There are some important next steps you need to take to unlock the full power of My Drink Nation:

    1) Make sure you add a profile image for %s
    2) Start inviting your bartenders
    3) Connect your bank account to start receiving drink orders

    Thanks,
    The My Drink Nation team
    %s
    """ % (bar.name, request.build_absolute_uri(reverse('core:home')))
    msg.from_email = settings.EMAIL_FROM_EMAIL
    msg.to = [bar.owner.email]
    msg.send()
    return msg
