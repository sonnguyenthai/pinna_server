import os
import binascii

from datetime import datetime
from datetime import timedelta

from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.utils.timezone import utc


def generate_key(number=20):
    return binascii.hexlify(os.urandom(number))


class Profile(models.Model):
    user = models.OneToOneField(User)
    display_photo = models.CharField(max_length=2083, null=True)
    photo_s3_name = models.CharField(max_length=200, null=True)
    followers = models.ManyToManyField(User, null=True,
                                       related_name="followers",)
                                       #symmetrical=False)
    amount = models.FloatField(default=0)
    #mytracks = models.ForeignKey('Library', related_name='+')
    mylibrary = models.ForeignKey('Library', related_name='+')
    mystations = models.ManyToManyField('Station', null=True,
                                        related_name="subscribers",
                                        through="StationSubscriber")


class PinnaSession(models.Model):
    key = models.CharField(max_length=40, primary_key=True)
    user = models.ForeignKey(User)
    created_time = models.DateTimeField(auto_now_add=True)
    expired_time = models.DateTimeField(default=(datetime.utcnow().replace(tzinfo=utc)+ \
                                                 timedelta(hours=settings.PINNA_SESSION_EXPIRATION_TIME)))
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = generate_key()
            try:
                checked = PinnaSession.objects.get(key=self.key)
                self.key = generate_key()
            except PinnaSession.DoesNotExist:
                pass
        return super(PinnaSession, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.key


class Track(models.Model):
    user = models.ForeignKey(User, related_name="mytracks")
    name = models.CharField(max_length=200)
    s3_name = models.CharField(max_length=200, null=True)
    url = models.CharField(max_length=500)
    genre = models.ForeignKey('MusicMeta', related_name='genre_tracks')
    mood = models.ForeignKey('MusicMeta', related_name='mood_tracks')
    bpm = models.IntegerField(db_index=True)
    hashtags = models.ManyToManyField('Hashtag', null=True)
    #like_count = models.IntegerField(default=0)
    download_count = models.IntegerField(default=0)
    author = models.CharField(max_length=200, null=True)
    artist = models.CharField(max_length=200, null=True)
    duration = models.FloatField(default=0)
    price = models.FloatField(default=15)
    likes = models.ManyToManyField(User, null=True, related_name="liked_tracks")
    purchases = models.ManyToManyField(User, null=True, related_name="purchased_tracks")
    privacy_level = models.IntegerField(default=1)
    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'name',)


class Library(models.Model):
    date_created = models.DateTimeField(auto_now_add=True)
    tracks = models.ManyToManyField('Track')


class Playlist(models.Model):
    user = models.ForeignKey(User)
    name = models.CharField(max_length=200)
    date_created = models.DateTimeField(auto_now_add=True)
    tracks = models.ManyToManyField('Track')

    class Meta:
        unique_together = ('user', 'name',)


class Station(models.Model):
    user = models.ForeignKey(User)
    name = models.CharField(max_length=200)
    photo = models.CharField(max_length=2083, null=True)
    photo_s3_name = models.CharField(max_length=200, null=True)
    thumbnail =  models.CharField(max_length=2083, null=True)
    thumbnail_s3_name = models.CharField(max_length=200, null=True)
    genre = models.ForeignKey('MusicMeta', related_name='station_genres', null=True)
    mood = models.ForeignKey('MusicMeta', related_name='station_moods', null=True)
    bpm = models.CharField(max_length=100)
    hashtags = models.ManyToManyField('Hashtag', null=True)
    tracks = models.ManyToManyField('Track')
    privacy_level = models.IntegerField(default=1)
    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'name',)


class StationSubscriber(models.Model):
    profile = models.ForeignKey('Profile')
    station = models.ForeignKey('Station')
    date_subscribed = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('profile', 'station',)


class Hashtag(models.Model):
    name = models.CharField(max_length=100, unique=True)
    date_created = models.DateTimeField(auto_now_add=True)


class MusicMeta(models.Model):
    META_TYPES = (
        ('genre', 'Genre'),
        ('mood', 'Mood'),
    )
    name = models.CharField(max_length=100, unique=True, db_index=True)
    type = models.CharField(max_length='5', choices=META_TYPES)
    date_created = models.DateTimeField(auto_now_add=True)


class PinnaOrder(models.Model):
    order_id = models.CharField(max_length=100, primary_key=True)
    user = models.ForeignKey(User, null=True)
    purchase_state = models.IntegerField(default=0)
    purchase_time = models.DateTimeField()
    purchase_data = models.TextField(null=False)
    date_created = models.DateTimeField(auto_now_add=True)


class PinnaAd(models.Model):
    name = models.CharField(max_length=200)
    url = models.CharField(max_length=2083, null=True)
    s3_name = models.CharField(max_length=200, null=True)
    date_created = models.DateTimeField(auto_now_add=True)


class PinnaSettings(models.Model):
    id = models.CharField(max_length=40, primary_key=True)
    play_ad_after_songs = models.IntegerField(default=5)