from datetime import datetime, timedelta

from django.conf import settings
from django.utils.timezone import utc

from rest_framework import serializers
from rest_framework import pagination

import models
import utils


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User
    """
    display_name = serializers.SerializerMethodField('get_display_name')
    photo = serializers.SerializerMethodField('get_photo')
    num_followers = serializers.SerializerMethodField('get_num_followers')
    is_followed = serializers.SerializerMethodField('get_is_followed')

    class Meta:
        model = models.User
        fields = ('id', 'display_name', 'photo',
                  'num_followers', 'is_followed', 'email',
        )

    def __init__(self, *args, **kwargs):
        context = kwargs.get('context', {})
        self.current_user = context.get("current_user", None)
        super(UserSerializer, self).__init__(*args, **kwargs)

    def get_display_name(self, obj):
        return obj.first_name

    def get_photo(self, obj):
        return obj.profile.display_photo

    def get_num_followers(self, obj):
        return obj.profile.followers.count()

    def get_is_followed(self, obj):
        if not self.current_user:
            return True
        if self.current_user == obj:
            return True
        if obj.profile.followers.filter(pk=self.current_user.pk).exists():
            return True
        return False


class TrackSerializer(serializers.ModelSerializer):
    """
    Serializer class of Track
    """
    url = serializers.SerializerMethodField('generate_track_url')
    hashtags = serializers.SlugRelatedField(many=True, slug_field='name')
    genre = serializers.PrimaryKeyRelatedField(many=False)
    mood = serializers.PrimaryKeyRelatedField(many=False)
    like_count = serializers.SerializerMethodField('get_like_count')
    is_liked = serializers.SerializerMethodField('check_is_liked')
    is_purchased = serializers.SerializerMethodField('check_is_purchased')
    owner_id = serializers.SerializerMethodField('get_owner_id')


    def __init__(self, *args, **kwargs):
        context = kwargs.get('context', {})
        self.current_user = context.get("current_user", None)
        super(TrackSerializer, self).__init__(*args, **kwargs)


    class Meta:
        model = models.Track
        fields = ('id', 'name', 'url',
                  'like_count', 'download_count',
                  'duration', 'author', 'genre',
                  'mood', 'hashtags', 'price', 'artist',
                  'is_liked', 'owner_id', 'is_purchased',
        )


    def generate_track_url(self, obj):
        return utils.create_signed_url(obj.url)

    def get_like_count(self, obj):
        return obj.likes.count()

    def check_is_liked(self, obj):
        if not self.current_user:
            self.current_user = obj.user
        if obj.likes.filter(pk=self.current_user.pk).exists():
            return True
        return False

    def get_owner_id(self, obj):
        return obj.user.pk

    def check_is_purchased(self, obj):
        if (not self.current_user) or (self.current_user == obj.user):
            return True
        if obj.purchases.filter(pk=self.current_user.pk).exists():
            return True
        return False


class PlaylistSerializer(serializers.ModelSerializer):
    num_tracks = serializers.SerializerMethodField('num_of_tracks')

    class Meta:
        model = models.Playlist
        fields = ('id', 'name', 'num_tracks')

    def num_of_tracks(self, obj):
        return obj.tracks.count()


class StationSerializer(serializers.ModelSerializer):
    num_tracks = serializers.SerializerMethodField('num_of_tracks')
    genre = serializers.PrimaryKeyRelatedField(many=False)
    mood = serializers.PrimaryKeyRelatedField(many=False)
    num_subscribers = serializers.SerializerMethodField('num_of_subscribers')
    author = serializers.SerializerMethodField('station_author')
    owner_id = serializers.SerializerMethodField('get_owner_id')
    recent_num_subscribers = serializers.SerializerMethodField('get_recent_num_subscribers')
    hashtags = serializers.SlugRelatedField(many=True, slug_field='name')
    is_subscribed = serializers.SerializerMethodField('check_is_subscribed')

    def __init__(self, *args, **kwargs):
        context = kwargs.get('context', {})
        self.current_user = context.get("current_user", None)

        super(StationSerializer, self).__init__(*args, **kwargs)

    class Meta:
        model = models.Station
        fields = ('id', 'name', 'genre',
                  'mood', 'bpm', 'author', 'num_subscribers',
                  'recent_num_subscribers', 'privacy_level',
                  'photo', 'thumbnail', 'hashtags', 'owner_id', 'is_subscribed'
            )

    def check_is_subscribed(self, obj):
        if not self.current_user:
            return True
        if self.current_user.profile.stationsubscriber_set.filter(station=obj).exists():
            return True
        return False

    def num_of_tracks(self, obj):
        return obj.tracks.count()

    def num_of_subscribers(self, obj):
        return obj.subscribers.count()

    def station_author(self, obj):
        return obj.user.first_name

    def get_owner_id(self, obj):
        return obj.user.pk

    def get_recent_num_subscribers(self, obj):
        date = datetime.utcnow().replace(tzinfo=utc) - \
                                    timedelta(hours=settings.PINNA_TRENDING_STATION_TIME)
        return obj.stationsubscriber_set.filter(date_subscribed__gt=date).count()


class AdSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.PinnaAd
        fields = ('id', 'name', 'url')


class LinksSerializer(serializers.Serializer):
    next = pagination.NextPageField(source='*')
    prev = pagination.PreviousPageField(source='*')


class PaginationSerializer(pagination.BasePaginationSerializer):
    next_page = pagination.NextPageField(source='*')
    previous_page = pagination.PreviousPageField(source='*')
    total = serializers.Field(source='paginator.count')
    num_pages = serializers.Field(source='paginator.num_pages')
    #current_page = serializers.Field(source='paginator.num_pages')

    results_field = 'tracks'


class PaginatedTrackSerializer(PaginationSerializer):
    """
    Serializes page objects of Track querysets.
    """
    class Meta:
        object_serializer_class = TrackSerializer


class PaginatedStationSerializer(PaginationSerializer):
    """
    Serializes page objects of Station querysets.
    """
    results_field = 'stations'

    class Meta:
        object_serializer_class = StationSerializer


class PaginatedUserSerializer(PaginationSerializer):
    """
    Serializes page objects of Station querysets.
    """
    results_field = 'users'

    class Meta:
        object_serializer_class = UserSerializer


class PaginatedAdSerializer(PaginationSerializer):
    """
    Serializes page objects of PinnaAd querysets.
    """
    results_field = 'ads'

    class Meta:
        object_serializer_class = AdSerializer