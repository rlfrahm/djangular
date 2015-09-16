from django.core.mail import EmailMessage
from django.core.urlresolvers import reverse

def send_bartender_invite(invite, to):
  msg = EmailMessage()
  msg.subject = 'You have been invited to join %s' % invite.bar.name
  msg.body = """
  %s has invited you to join the My Drink Nation network!

  To accept this invitation, simply follow this link: %s.

  My Drink Nation helps people buy drinks for their friends. Come help make that happen!
  """ % (invite.bar.name, reverse('bars:bartender-invite', args=(invite.bar.pk, invite.token,)))
  msg.from_email = 'no-reply@mydrinknation.com'
  msg.to = [to]
  msg.save()
  return msg