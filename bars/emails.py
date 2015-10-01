from django.core.mail import EmailMessage
from django.core.urlresolvers import reverse

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
  msg.from_email = 'no-reply@mydrinknation.com'
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
  msg.from_email = 'no-reply@mydrinknation.com'
  msg.to = [invite.email]
  msg.send()
  return msg

def send_us_bar_inquiry(request, name, bar_name, email, phone, license, comments):
  msg = EmailMessage()
  msg.subject = 'Bar Inquiry: %s' % bar_name
  msg.body = """
  Who: %s with %s
  License # (last six): %s
  Email: %s
  Phone: %s
  Comments: %s
  """ % (name, bar_name, license, email, phone, comments)
  msg.from_email = 'no-reply@mydrinknation.com'
  msg.to = ['frahmryan@gmail.com']
  msg.send()
  return msg
