# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0001_initial'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='userprofile',
            unique_together=set([('email', 'user')]),
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='ref_id',
        ),
    ]
