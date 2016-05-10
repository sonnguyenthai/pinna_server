import binascii
import base64
import logging
import os
import time
import hashlib
import traceback
import random
from cStringIO import StringIO
from datetime import datetime, timedelta

from django.conf import settings
from django.utils.timezone import utc
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q

from aggregate_if import Count

import boto
from boto.cloudfront import CloudFrontConnection

from PIL import Image, ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True

from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5

from rest_framework import HTTP_HEADER_ENCODING
from rest_framework.response import Response
from rest_framework import status

from .models import (PinnaSession, Station,
                     StationSubscriber, MusicMeta, Track, Hashtag)
from serializers import (PaginatedTrackSerializer,
                         PaginatedStationSerializer,
                         PaginatedUserSerializer,
                         StationSerializer, PaginatedAdSerializer)



LOG = logging.getLogger("django.request")


def generate_random_name(name):
    name = name + str(time.time())
    return hashlib.md5(name).hexdigest()

def generate_key(number=20):
    return binascii.hexlify(os.urandom(number))


def get_header(header_name, request):
    """
    Return request's `header_name` header, as a bytestring.

    Hide some test client ickyness where the header can be unicode.
    """
    header = request.META.get("HTTP_%s" %header_name, b'')
    if type(header) == type(''):
        # Work around django test client oddness
        header = header.encode(HTTP_HEADER_ENCODING)
    return header


def check_auth_token(request):
    """
    Check if a request has valid authentication token. Return PinnaSession object if True
    """
    token = get_header(settings.PINNA_AUTH_TOKEN_HEADER, request).strip()
    if not token:
        return None

    try:
        session = PinnaSession.objects.get(pk=token)

        if not session.is_active:
            return None

        if datetime.utcnow().replace(tzinfo=utc) > session.expired_time:
            return None

        session.expired_time = datetime.utcnow().replace(tzinfo=utc) + \
                                timedelta(hours=settings.PINNA_SESSION_EXPIRATION_TIME)
        session.save()
        return session
    except:
        msg = traceback.format_exc()
        LOG.error(msg)
        return None


def expire_token(token):
    """
    Makes a token expired.
    """
    session = PinnaSession.objects.get(pk=token.strip())
    session.expired_time = datetime.utcnow().replace(tzinfo=utc)
    session.is_active = False
    session.save()


def get_distribution(is_music=True):
    """
    Get CloudFront distribution
    """
    try:
        cnn = CloudFrontConnection(aws_access_key_id=settings.PINNA_AWS_ACCESS_KEY_ID,
                                   aws_secret_access_key=settings.PINNA_AWS_SECRET_KEY_ID)

        if is_music:
            dis = cnn.get_distribution_info(settings.PINNA_AWS_MUSIC_DATA_ID)
        else:
            dis = cnn.get_distribution_info(settings.PINNA_AWS_USER_PROFILE_ID)

        return dis
    except:
        msg = traceback.format_exc()
        LOG.error(msg)
        return None


def add_object_via_cloudfront(name, content, is_music=True):
    """
    Add object to S3 via CloudFront
    @Return: CloudFront url of the object
    """
    dis = get_distribution(is_music)
    obj = dis.add_object(name, content)
    if obj:
        return obj.url()
    else:
        return None


def create_signed_url(url, expire_time=settings.PINNA_TRACK_EXPIRATION_TIME,
                      is_music=False, valid_after_time=None):
    """
    Create a signed url for a s3 object via CloudFront
    expire_time: time.time() + duration_in_sec.
    valid_after_time: time.time() + secs_until_valid.
    """
    #expire_time = None
    expire_time = int(time.time() + expire_time)

    dis = get_distribution(is_music)
    signed = dis.create_signed_url(
                url,
                keypair_id=settings.PINNA_CLOUDFRONT_KEY_ID,
                expire_time=expire_time,
                valid_after_time=valid_after_time,
                private_key_file=settings.PINNA_CLOUDFRONT_PRIVATE_KEY_FILE,
            )
    return signed


def get_s3_bucket(is_music=True):
    """
    Return PINNA S3 bucket
    """
    con = boto.connect_s3(aws_access_key_id=settings.PINNA_AWS_ACCESS_KEY_ID,
                           aws_secret_access_key=settings.PINNA_AWS_SECRET_KEY_ID)

    if is_music:
        buc = con.get_bucket(settings.PINNA_MUSIC_BUCKET)
    else:
        buc = con.get_bucket(settings.PINNA_USER_PROFILE_BUCKET)

    return buc


def check_s3_object(name, is_music=True, buc=None):
    """
    Check if an object already existed
    """
    if not buc:
        buc = get_s3_bucket(is_music)
    key = buc.get_key(name)
    if not key:
        return True
    else:
        return False


def add_s3_object(name, content, is_music=True):
    """
    Create an object on the S3 bucket
    """
    try:
        buc = get_s3_bucket(is_music)
        item = boto.s3.key.Key(buc)
        item.key = name
        obj = item.set_contents_from_file(content)
        if obj:
            return True
        else:
            return False
    except:
        msg = traceback.format_exc()
        LOG.error(msg)
        return False


def delete_s3_object(name, is_music=True):
    """
    Remove an object from S3 bucket
    """
    buc = get_s3_bucket(is_music)
    key = buc.get_key(name)
    key.delete()


def invalid_auth_response(msg='Authenticated token was invalid',
                          msg_code='invalid_auth_token'):
    """
    Return a Response object for invalid authenticated token case
    """
    data = {}
    data['code'] = 0
    data['msg_code'] = msg_code
    data['message'] = msg

    return Response(data, status.HTTP_401_UNAUTHORIZED)


def successful_response(msg, msg_code, **kwargs):
    """
    Successful Response
    """
    data = {}
    data['code'] = 1
    data['msg_code'] = msg_code
    data['message'] = msg
    data.update(kwargs)

    return Response(data, status.HTTP_202_ACCEPTED)


def failed_response(msg, msg_code):
    """
    Successful Response
    """
    data = {}
    data['code'] = 0
    data['msg_code'] = msg_code
    data['message'] = msg

    return Response(data, status.HTTP_406_NOT_ACCEPTABLE)


def check_email_existed(email, exclude_user=False):
    """
    Check if an emails is existed in the db
    """
    if User.objects.filter(email=email).count():
        return True
    return False


def slugify_name(name):
    """
    Turn a name to be more friendly to url
    """
    return slugify(name)


def valid_email(email):
    """
    Validate an email address
    """
    try:
        validate_email(email)
    except ValidationError:
        return False
    else:
        return True


def paginate_items(request, queryset, type="track", user=None):
    """
    Return list of tracks with pagination
    """
    if request.method == "GET":
        data = request.QUERY_PARAMS
    else:
        data = request.DATA

    per_page = data.get('per_page', settings.PINNA_NUMBER_OF_TRACKS_PER_PAGE)
    page = data.get('page', 1)

    paginator = Paginator(queryset, per_page)


    try:
        items = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        items = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999),
        # deliver last page of results.
        items = paginator.page(paginator.num_pages)

    serializer_context = {'request': request, 'current_user': user}

    if type == "track":
        serializer = PaginatedTrackSerializer(items,
                                             context=serializer_context)

    if type == "station":
        serializer = PaginatedStationSerializer(items,
                                             context=serializer_context)

    if type == "user":
        serializer = PaginatedUserSerializer(items,
                                             context=serializer_context)

    if type == "ad":
        serializer = PaginatedAdSerializer(items,
                                             context=serializer_context)

    return serializer.data


def get_trending_stations():
    """
    Get trending stations
    """
    date = datetime.utcnow().replace(tzinfo=utc) - \
                                timedelta(hours=settings.PINNA_TRENDING_STATION_TIME)

    subs = StationSubscriber.objects.annotate(
        sub_count=Count('profile', Q(date_subscribed__gt=date))).order_by('sub_count')[:50]

    stations = []
    for s in subs:
        if s.station not in stations:
            stations.append(s.station)

    if not stations:
        stations = Station.objects.order_by('?')[:50]

    return stations


def resize_image(buf, w=160, h=180):
    """
    Resize an image for downsampling
    """
    image = Image.open(buf)

    if image.mode != "RGB":
        image = image.convert("RGB")

    maxSize = (w, h)
    image.thumbnail(maxSize, Image.ANTIALIAS)
    # Turn back into file-like object
    resizedImageFile = StringIO()
    image.save(resizedImageFile , 'JPEG', optimize = True, quality=90)
    resizedImageFile.seek(0)    # So that the next read starts at the beginning
    return resizedImageFile


def create_station(user, name, photo, genre, mood, bpm, hashtags):

    station, created = Station.objects.get_or_create(name=name,
                                                        user=user)

    if not created:
        msg = "The station name already existed"
        return failed_response(msg, "name_existed")
    else:
        try:
            genre_obj = MusicMeta.objects.get(pk=genre)
            mood_obj = MusicMeta.objects.get(pk=mood)

            station.genre = genre_obj
            station.mood = mood_obj

            if bpm:
                bmp_v = " to ".join([b.strip() for b in bpm])
                station.bpm = bmp_v

            if hashtags:
                tags = []
                for t in hashtags.split(','):
                    try:
                        tag = Hashtag.objects.get(name=t)
                        tags.append(tag)
                    except Hashtag.DoesNotExist:
                        pass
                if tags:
                    station.hashtags = tags

            origin_name, ext = os.path.splitext(photo.name)
            if not ext:
                ext = "jpg"

            aws_name = slugify_name(user.username) + \
                       '/station_images/' + generate_random_name(origin_name)
            thumb_name = aws_name + '_thumb' + ext
            aws_name += ext
            photo_obj = add_object_via_cloudfront(aws_name, photo, False)
            photo.seek(0)
            thumb = add_object_via_cloudfront(thumb_name, resize_image(photo), False)
            if not (photo_obj and thumb):
                msg = "Can't upload station photo to S3"
                msg_code = "failed"
                return failed_response(msg, msg_code)

            station.photo = photo_obj
            station.photo_s3_name = aws_name
            station.thumbnail = thumb
            station.thumbnail_s3_name = thumb_name

            station.save()

            context = {"current_user": user}
            serializer = StationSerializer(station, context=context)
            msg = "The station was created"
            return successful_response(msg, "ok", **serializer.data)
        except Exception as e:
            LOG.error("[STATION] Creating error: %s" %traceback.format_exc())
            try:
                if station.photo_s3_name:
                    delete_s3_object(station.photo_s3_name, False)
                if station.thumbnail_s3_name:
                    delete_s3_object(station.thumbnail_s3_name, False)
                station.delete()
            except:
                pass
            msg = "Can't create station"
            return failed_response(msg, "failed")


def update_station(station, name, photo, user):
    if name:
        try:
            Station.objects.get(user=user, name=name)
            msg = "This name is existed"
            return failed_response(msg, "name_existed")
        except Station.DoesNotExist:
            station.name = name
            station.save()

    if photo:
        origin_name, ext = os.path.splitext(photo.name)
        if not ext:
            ext = "jpg"

        aws_name = slugify_name(user.username) + '/station_images/'\
                   + generate_random_name(origin_name)
        thumb_name = aws_name + '_thumb' + ext
        aws_name += ext
        photo_obj = add_object_via_cloudfront(aws_name, photo, False)
        photo.seek(0)
        thumb = add_object_via_cloudfront(thumb_name, resize_image(photo), False)
        if not (photo_obj and thumb):
            msg = "Can't upload station photo to S3"
            msg_code = "failed"
            return failed_response(msg, msg_code)

        try:
            old_photo = station.photo_s3_name
            old_thumb = station.thumbnail_s3_name
            delete_s3_object(old_photo, False)
            delete_s3_object(old_thumb, False)
        except AttributeError:
            pass

        station.photo = photo_obj
        station.photo_s3_name = aws_name
        station.thumbnail = thumb
        station.thumbnail_s3_name = thumb_name
        station.save()

    msg = "The station with id %s is updated" %station.id
    return successful_response(msg, "ok")


def get_station_tracks(station):
    """
    """
    genre = station.genre
    mood = station.mood
    hashtags = station.hashtags.all()

    bpm = station.bpm
    if bpm:
        bpms = bpm.split('to')
        min_bpm = int(bpms[0])
        max_bpm = int(bpms[1])

    tracks = Track.objects.filter(genre=genre, mood=mood)

    if bpm:
        tracks = tracks.filter(bpm__range=(min_bpm, max_bpm))

    if hashtags:
        tracks = tracks.filter(hashtags__in=hashtags).distinct()

    count = tracks.count()
    if count < 50:
        result = tracks
    else:
        if count > 50:
            count = 50
        result = random.sample(tracks, count)

    return result


def verify_signature(signed_data, signature_base64):
    """
    Returns whether the given data was signed with the private key.
    Use for Google In-App purchase signatures
    """
    h = SHA.new()
    h.update(signed_data)

    # Scheme is RSASSA-PKCS1-v1_5.
    pkey = RSA.importKey(base64.standard_b64decode(settings.PINNA_GOOGLE_PLAY_PKEY))
    verifier = PKCS1_v1_5.new(pkey)

    # The signature is base64 encoded. Decode it
    signature = base64.standard_b64decode(signature_base64)

    return verifier.verify(h, signature)