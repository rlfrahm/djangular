# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '__first__'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Cup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=60)),
                ('ref_id', models.CharField(default=b'BABEV', unique=True, max_length=60)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('public', models.BooleanField(default=False, choices=[(True, b'Public'), (False, b'Private')])),
                ('bev_choices', models.CharField(max_length=60, choices=[(b'Non Alcohol', b'No Alcohol'), (b'Alcohol', b'Alcohol'), (b'Mixed', b'Mixed')])),
                ('thumbnail', models.ImageField(upload_to=b'cup_images', blank=True)),
                ('likes', models.IntegerField(default=0)),
                ('followers', models.IntegerField(default=0)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='CupCollection',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('cup', models.ForeignKey(to='core.Cup')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='CupComment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('message', models.TextField()),
                ('cup', models.ForeignKey(to='core.Cup')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='CupItems',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('rating_votes', models.PositiveIntegerField(default=0, editable=False, blank=True)),
                ('rating_score', models.IntegerField(default=0, editable=False, blank=True)),
                ('cup', models.ForeignKey(to='core.Cup')),
                ('recipe', models.ForeignKey(to='recipes.Recipe')),
            ],
        ),
        migrations.CreateModel(
            name='CupLikes',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('cup', models.ForeignKey(to='core.Cup')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='FavoriteCup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(unique=True, max_length=60)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('recipe', models.ForeignKey(to='recipes.Recipe')),
            ],
        ),
        migrations.CreateModel(
            name='PopularCup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(unique=True, max_length=60)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('recipe', models.ForeignKey(to='recipes.Recipe')),
            ],
        ),
        migrations.CreateModel(
            name='UserImage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('picture', models.ImageField(upload_to=b'profile_images', blank=True)),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('ref_id', models.CharField(default=b'BABEVUSER', unique=True, max_length=60)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('location', models.CharField(max_length=100, blank=True)),
                ('birthday', models.DateField()),
                ('email', models.EmailField(max_length=254, verbose_name=b'email', db_index=True)),
                ('ip_address', models.CharField(default=b'ABC', max_length=120)),
                ('picture', models.ImageField(upload_to=b'profile_images', blank=True)),
                ('user', models.OneToOneField(related_name='profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='popularcup',
            name='user',
            field=models.ForeignKey(to='core.UserProfile'),
        ),
        migrations.AddField(
            model_name='favoritecup',
            name='user',
            field=models.ForeignKey(to='core.UserProfile'),
        ),
        migrations.AlterUniqueTogether(
            name='userprofile',
            unique_together=set([('email', 'ref_id')]),
        ),
    ]
