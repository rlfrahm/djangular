from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

import datetime

from bars.models import Bar

# Create your models here.
class UserProfile(models.Model):
    DRINKER = 'Drinker'
    BARTENDER = 'Bartender'
    BUSINESS = 'Business'

    USER_TYPE_CHOICES=((DRINKER, 'Drinker'), (BARTENDER, 'Bartender'), (BUSINESS, 'Business'),)


    user = models.OneToOneField(User, related_name="profile")
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)
    location = models.CharField(max_length=100, blank=True)
    # age = models.PositiveIntegerField(blank=True,null=True)
    # birthday = models.DateField()
    dob = models.DateField(default=datetime.date.today)
    email= models.EmailField('email', unique=False, db_index=True)
    ip_address = models.CharField(max_length=120, default='ABC')
    picture = models.ImageField(upload_to='profile_images', blank=True)


    def save(self, *args, **kwargs):
        try:
            existing = UserProfile.objects.all().get(user=self.user)
            self.id=existing.id
        except UserProfile.DoesNotExist:
            pass
        models.Model.save(self, *args, **kwargs)

    def is_birthday(self):
        birthday = self.cleaned_data['Birthday']
        age = (date.now() - birthday).days/365
        if age < 21:
            raise models.ValidationError('Must be at least 21 years old to register')
        return self.age in (self.DRINKER, self.BARTENDER_SERVER)

    def is_birthday_2(self):
        birthday_2 = self.cleaned_data['Birthday']
        age = (date.now() - birthday_2).days/365
        if age < 18:
            raise models.ValidationError('Must be at least 18 years old to register')
        return self.age in (self.BARTENDER_SERVER, self.DRINKER)

    def is_established(self):
        established = self.cleaned_data['Established']
        started = (date.now() - established).days/1
        if started < 1:
            raise models.ValidationError('Must be in business for at least 1 day to register')
        return self.age in (self.BUSINESS, self.DRINKER)


    def __unicode__(self):
        return self.user.username

    class Meta:
        unique_together = ("email", "user",)