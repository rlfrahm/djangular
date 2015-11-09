from django.core.management.base import BaseCommand, CommandError
from bars.models import Sale

from datetime import timedelta
from django.utils import timezone

class Command(BaseCommand):
	help = 'Completes sales that have been left open'

	def handle(self, *args, **options):
		try:
			time_threshold = timezone.now() - timedelta(hours=1)
			sales = Sale.objects.filter(created__lt=time_threshold, status=Sale.PENDING_STATUS)
		except Exception, e:
			raise CommandError('The transaction query failed')

		for s in sales:
			s.complete()

		self.stdout.write('Successfully closed %i sales older than %s' % (len(sales), time_threshold))
