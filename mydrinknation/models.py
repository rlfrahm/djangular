from datetime import date
from time import time
from django.db import models
from django.contrib.auth.models import User
from djangoratings.fields import RatingField
from recipes.models import Recipe

from accounts.models import UserProfile


def get_upload_file_name(instance, filename):
    return "uploaded_files/%s_%s" % (str(time()).replace('.','_'), filename)

class FavoriteCup(models.Model):
    title = models.CharField(max_length=60, unique=True)
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)
    user = models.ForeignKey(UserProfile)
    recipe = models.ForeignKey(Recipe)

    # business = models.ForeignKey(Business)

    def __unicode__(self):
        return "%s" %(self.title)

class PopularCup(models.Model):
    title = models.CharField(max_length=60, unique=True)
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)
    user = models.ForeignKey(UserProfile)
    recipe = models.ForeignKey(Recipe)
    # business = models.ForeignKey(Business)

    def __unicode__(self):
        return "%s" %(self.title)

class Cup(models.Model):
    NOALCOHOL = 'Non Alcohol'
    ALCOHOL = 'Alcohol'
    MIXED = 'Mixed'

    BEV_TYPE_CHOICES=((NOALCOHOL, 'No Alcohol'), (ALCOHOL, 'Alcohol'), (MIXED, 'Mixed'),)
    PUBLIC_CHOICES = ((True, 'Public'), (False, 'Private'))

    title = models.CharField(max_length=60, unique=False)
    ref_id = models.CharField(max_length=60, unique=True, default='BABEV')
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)
    user = models.ForeignKey(User)
    public = models.BooleanField(default=False, choices=PUBLIC_CHOICES)
    bev_choices = models.CharField(max_length=60, choices=BEV_TYPE_CHOICES, unique=False)

    thumbnail = models.ImageField(upload_to='cup_images', blank=True)
    likes = models.IntegerField(default=0)
    followers = models.IntegerField(default=0)
    #rating = RatingField(range=5)

    def __unicode__(self):
        return "%s" %(self.title)

    def get_recipes(self):
        # TODO: Fix this, it could be done better
        recipes = []
        items = CupItems.objects.filter(cup=self)
        for item in items:
            recipes.append(item.recipe)

        return recipes

    def get_items(self):
        return CupItems.objects.filter(cup=self)

class CupComment(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User)
    message = models.TextField()
    cup = models.ForeignKey(Cup)

class CupLikes(models.Model):
    user = models.ForeignKey(User)
    cup = models.ForeignKey(Cup)
    created = models.DateTimeField(auto_now_add=True)

class CupItems(models.Model):
    cup = models.ForeignKey(Cup)
    recipe = models.ForeignKey(Recipe)
    rating = RatingField(range=5)

class CupCollection(models.Model):
    cup = models.ForeignKey(Cup)
    user = models.ForeignKey(User)
    created = models.DateTimeField(auto_now_add=True)


# Allows user to upload a profile image to the navbar.
class UserImage(models.Model):
    # This line is required. Links UserProfile to a User model instance.
    user = models.OneToOneField(User)

    # The additional attributes we wish to include.
    # cup = models.URLField(blank=True)
    picture = models.ImageField(upload_to='profile_images', blank=True)

    # Override the __unicode__() method to return out something meaningful!
    def __unicode__(self):
        return self.user.username