import itertools
import os
import random
import traceback
import logging

from django.contrib.auth.models import User
from django.conf import settings

from rest_framework.decorators import api_view

import models
import serializers
import utils

_LOG = logging.getLogger("django.request")

@api_view(['POST'])
def upload_track(request):
    """
    Upload track to db
    """
    session = utils.check_auth_token(request)
    if not session:
        return utils.invalid_auth_response()

    else:
        file = request.FILES.get('file', None)
        name = request.DATA.get('name', '')
        genre = request.DATA.get('genre', '')
        mood = request.DATA.get('mood', '')
        bmp = request.DATA.get('bpm', 0)
        hashtags = request.DATA.get('hashtags', '')
        duration = request.DATA.get('duration', 0)
        author = request.DATA.get('author', '')
        artist = request.DATA.get('artist', '')

        if not (file and name and genre and mood and bmp and duration):
            msg = "These fields are empty:"

            empty_files = []
            if not name:
                empty_files.append('name')
            if not file:
                empty_files.append('file')
            if not genre:
                empty_files.append('genre')
            if not mood:
                empty_files.append('mood')
            if not bmp:
                empty_files.append('bpm')
            if not duration:
                empty_files.append('duration')

            msg += ",".join(empty_files)
            msg_code = "empty_fields"

            return utils.failed_response(msg, msg_code)

        user = session.user

        try:
            genre_obj =  models.MusicMeta.objects.get(pk=genre)
        except models.MusicMeta.DoesNotExist:
            return utils.failed_response(
                'Genre with id: %s does not exist' %genre,
                'invalid_field')

        try:
            mood_obj = models.MusicMeta.objects.get(pk=mood)
        except models.MusicMeta.DoesNotExist:
            return utils.failed_response(
                'Mood with id: %s does not exist' %mood,
                'invalid_field')

        try:
            bmp = int(bmp)
        except:
            return utils.failed_response(
                'Invalid bmp: %s. BMP must be a integer number' %bmp,
                'invalid_field')

        try:
            track = models.Track.objects.get(user=user, name=name)
            msg = "The track name already existed"
            msg_code = "existed"
            return utils.failed_response(msg, msg_code)
        except models.Track.DoesNotExist:
            aws_name = utils.slugify_name(user.username) + '/' + utils.slugify_name(name)
            origin_name, ext = os.path.splitext(file.name)
            aws_name += ext
            url = utils.add_object_via_cloudfront(aws_name, file)
            if url:
                track = models.Track.objects.create(user=user,
                                                    name=name,
                                                    s3_name=aws_name,
                                                    url=url,
                                                    genre=genre_obj,
                                                    mood=mood_obj,
                                                    bpm=bmp,
                                                    duration=duration,
                                                    author=author,
                                                    artist=artist)
                tags = hashtags.split(',')
                for t in tags:
                    tag, created = models.Hashtag.objects.get_or_create(name=t)
                    track.hashtags.add(tag)

                track.save()

                #user.profile.mytracks.tracks.add(track)
                #user.profile.save()

                msg = "The track %s was created" %name
                msg_code = "ok"

                return utils.successful_response(msg,
                                                 msg_code,
                                                 url=utils.create_signed_url(track.url),
                                                 id=track.id)
            else:
                msg = "Can't upload this track to S3"
                msg_code = "failed"
                return utils.failed_response(msg, msg_code)


@api_view(['GET', 'DELETE', 'PUT'])
def manage_track(request, trackid):
    """
    Get track information by track ID
    """
    session = utils.check_auth_token(request)
    if not session:
        return utils.invalid_auth_response()

    try:
        track = models.Track.objects.get(pk=trackid)

        if request.method == 'GET':
            if track.user != session.user:
                if track.privacy_level != 1:
                    msg= "You don't have permission to view this track"
                    return utils.failed_response(msg, "permission_denied")

            msg = "Found the track %s" %track.name
            context = {"current_user": session.user}
            serializer = serializers.TrackSerializer(track, context=context)
            return utils.successful_response(msg, 'ok', **serializer.data)

        elif request.method == 'DELETE':
            if track.user != session.user:
                msg= "You don't have permission to delete this track"
                return utils.failed_response(msg, "permission_denied")

            name = track.name
            utils.delete_s3_object(track.s3_name)
            track.delete()
            msg = "The track %s was deleted" %name
            msg_code = "ok"
            return utils.successful_response(msg, msg_code)

        elif request.method == 'PUT':
            if track.user != session.user:
                msg= "You don't have permission to update this track"
                return utils.failed_response(msg, "permission_denied")

            name = request.DATA.get('name', '')
            genre = request.DATA.get('genre', '')
            mood = request.DATA.get('mood', '')
            bmp = request.DATA.get('bpm', 0)
            hashtags = request.DATA.get('hashtags', '')
            duration = request.DATA.get('duration', 0)
            author = request.DATA.get('author', '')
            artist = request.DATA.get('artist', '')

            if name:
                track.name = name.strip()

            if genre:
                try:
                    genre_obj =  models.MusicMeta.objects.get(pk=genre)
                except models.MusicMeta.DoesNotExist:
                    return utils.failed_response(
                        'Genre with id: %s does not exist' %genre,
                        'invalid_field')

                track.genre = genre_obj

            if mood:
                try:
                    mood_obj = models.MusicMeta.objects.get(pk=mood)
                except models.MusicMeta.DoesNotExist:
                    return utils.failed_response(
                        'Mood with id: %s does not exist' %mood,
                        'invalid_field')

                track.mood = mood_obj

            if bmp:
                try:
                    bmp = int(bmp)
                except:
                    return utils.failed_response(
                        'Invalid bmp: %s. BMP must be a integer number' %bmp,
                        'invalid_field')

                track.bpm = bmp

            if hashtags:
                tags = hashtags.split(',')
                track.hashtags.clear()
                for t in tags:
                    tag, created = models.Hashtag.objects.get_or_create(name=t)
                    track.hashtags.add(tag)

            if duration:
                track.duration = duration

            if author:
                track.author = author

            if artist:
                track.artist = artist

            track.save()

            msg = "The track was updated"
            context = {"current_user": session.user}
            serializer = serializers.TrackSerializer(track, context=context)
            return utils.successful_response(msg, 'ok', **serializer.data)
    except models.Track.DoesNotExist:
        msg = "The track with id %s does not exist" %trackid
        msg_code = "not_found"
        return utils.failed_response(msg, msg_code)


@api_view(['GET'])
def list_genres(request):
    """
    List all available genres
    """
    session = utils.check_auth_token(request)
    if not session:
        return utils.invalid_auth_response()

    genres = models.MusicMeta.objects.filter(type="genre")

    if not genres:
        msg = "There is no genre found"
        msg_code = "not_found"
        return utils.failed_response(msg, msg_code)

    results = [[genre.id, genre.name] for genre in genres]

    msg = "There are %s genres found" %len(genres)
    msg_code = "ok"

    return utils.successful_response(msg,
                                     msg_code,
                                     genres=results)


@api_view(['GET'])
def list_moods(request):
    """
    List all available moods
    """
    session = utils.check_auth_token(request)
    if not session:
        return utils.invalid_auth_response()

    moods = models.MusicMeta.objects.filter(type="mood")

    if not moods:
        msg = "There is no mood found"
        msg_code = "not_found"
        return utils.failed_response(msg, msg_code)

    results = [[mood.id, mood.name] for mood in moods]

    msg = "There are %s moods found" %len(moods)
    msg_code = "ok"

    return utils.successful_response(msg,
                                     msg_code,
                                     moods=results)


@api_view(['GET'])
def get_my_tracks(request):
    """
    Get all tracks of My Tracks
    """
    session = utils.check_auth_token(request)
    if not session:
        return utils.invalid_auth_response()

    profile = session.user.profile

    tracks = session.user.mytracks.all()
    #serializer = serializers.TrackSerializer(tracks, many=True)
    data = utils.paginate_items(request, tracks)

    if tracks:
        msg = "There are %s tracks found" %len(tracks)
        msg_code = "ok"
        return utils.successful_response(msg, msg_code, **data)
    msg = "There is no track found"
    msg_code = "not_found"
    return utils.failed_response(msg, msg_code)


@api_view(['GET'])
def search_track(request):
    """
    Search track by name
    """
    session = utils.check_auth_token(request)
    if not session:
        return utils.invalid_auth_response()


    search_term = request.QUERY_PARAMS.get('search_term', None)

    if not search_term:
        return utils.failed_response('Search term is empty',
                                     'empty_fields')

    search_term = search_term.strip()
    tracks = models.Track.objects.filter(name__icontains=search_term)[:1000]
    #serializer = serializers.TrackSerializer(tracks, many=True)
    data = utils.paginate_items(request, tracks, user=session.user)

    if tracks:
        msg = "There are %s tracks found" %len(tracks)
        msg_code = "ok"
        return utils.successful_response(msg, msg_code, **data)
    msg = "There is no track found"
    msg_code = "not_found"
    return utils.failed_response(msg, msg_code)


@api_view(['GET'])
def list_playlists(request):
    """
    List all playlist of a user
    """
    session = utils.check_auth_token(request)
    if not session:
        return utils.invalid_auth_response()

    user = session.user
    playlists = user.playlist_set.all()
    serializer = serializers.PlaylistSerializer(playlists, many=True)

    if playlists:
        msg = "There are %s playlists found" %len(playlists)
        return utils.successful_response(msg, "ok", playlists=serializer.data)

    msg = "There is no playlist found"
    return utils.failed_response(msg, "not_found")


@api_view(['POST'])
def create_playlist(request):
    """
    Create a playlist
    """
    session = utils.check_auth_token(request)
    if not session:
        return utils.invalid_auth_response()

    pl_name =  request.DATA.get('playlist_name', None)
    track_ids = request.DATA.get('tracks', [])

    if not pl_name:
        msg = "Playlist name is empty"
        return utils.failed_response(msg, "empty_fields")

    pl_name = pl_name.strip()
    playlist, created = models.Playlist.objects.get_or_create(name=pl_name, user=session.user)
    if not created:
        msg = "This name was existed"
        return utils.failed_response(msg, "name_existed")

    for id in track_ids:
        try:
            track = models.Track.objects.get(id=id)
            playlist.tracks.add(track)
            session.user.profile.mylibrary.tracks.add(track)
        except models.Track.DoesNotExist:
            pass

    if track_ids:
        session.user.profile.mylibrary.save()
        playlist.save()

    msg = "The track %s was created" %pl_name
    return utils.successful_response(msg, "ok", playlist_id=playlist.id)


@api_view(['GET', 'PUT', 'DELETE'])
def manage_playlist(request, playlist_id):
    """
    Getting/deleting/updating a playlist
    """
    session = utils.check_auth_token(request)
    if not session:
        return utils.invalid_auth_response()

    try:
        playlist = models.Playlist.objects.get(pk=playlist_id)
    except models.Playlist.DoesNotExist:
        msg = "The playlist with id %s does not exist" %playlist_id
        return utils.failed_response(msg, "invalid_playlist")

    if request.method == "GET":
        tracks = playlist.tracks.all()
        #serializer = serializers.TrackSerializer(tracks, many=True)
        data = utils.paginate_items(request, tracks, user=session.user)

        if not tracks:
            msg = "The playlist is empty"
            return utils.failed_response(msg, "empty_playlist")

        msg = "There are %s track in the playlist" %len(tracks)
        return utils.successful_response(msg, "ok",
                                         playlist_name=playlist.name,
                                         **data)
    if request.method == "DELETE":
        if playlist.user != session.user:
            msg = "This playlist is not yours"
            return utils.failed_response(msg, "permission_denied")

        playlist.delete()
        msg = "The playlist was removed"
        return utils.successful_response(msg, "ok")

    if request.method == "PUT":
        if playlist.user != session.user:
            msg = "This playlist is not yours"
            return utils.failed_response(msg, "permission_denied")

        playlist_name = request.DATA.get("playlist_name", "")

        if playlist_name:
            try:
                p = models.Playlist.objects.get(user=session.user, name=playlist_name)
                msg = "This name is existed"
                return utils.failed_response(msg, "name_existed")
            except models.Playlist.DoesNotExist:
                playlist.name = playlist_name.strip()
                playlist.save()

        msg = "The playlist name was changed"
        return utils.successful_response(msg, "ok")


@api_view(['POST'])
def add_tracks_to_playlist(request, playlist_id):
    """
    Add tracks to playlist
    """
    session = utils.check_auth_token(request)
    if not session:
        return utils.invalid_auth_response()

    try:
        playlist = models.Playlist.objects.get(pk=playlist_id, user=session.user)
    except models.Playlist.DoesNotExist:
        msg = "The playlist with id %s does not exist" %playlist_id
        return utils.failed_response(msg, "invalid_playlist")

    track_ids = request.DATA.get("tracks", [])
    count = 0
    for id in track_ids:
        try:
            track = models.Track.objects.get(pk=id)
            playlist.tracks.add(track)
            playlist.save()

            session.user.profile.mylibrary.tracks.add(track)
            session.user.profile.mylibrary.save()

            count += 1
        except models.Track.DoesNotExist:
            pass

    if count == 1:
        msg = "The track was added to the playlist"
    else:
        msg = "There are %s tracks were added to the playlist" %count
    return utils.successful_response(msg, "ok")


@api_view(['POST'])
def remove_tracks_from_playlist(request, playlist_id):
    """
    Remove tracks from playlist
    """
    session = utils.check_auth_token(request)
    if not session:
        return utils.invalid_auth_response()

    try:
        playlist = models.Playlist.objects.get(pk=playlist_id, user=session.user)
    except models.Playlist.DoesNotExist:
        msg = "The playlist with id %s does not exist" %playlist_id
        return utils.failed_response(msg, "invalid_playlist")

    track_ids = request.DATA.get("tracks", [])
    count = 0
    for id in track_ids:
        try:
            track = models.Track.objects.get(pk=id)
            playlist.tracks.remove(track)
            playlist.save()

            session.user.profile.mylibrary.tracks.remove(track)
            session.user.profile.mylibrary.save()

            count += 1
        except models.Track.DoesNotExist:
            pass

    if count == 1:
        msg = "The track was removed from the playlist"
    else:
        msg = "There are %s tracks were removed from the playlist" %count
    return utils.successful_response(msg, "ok")


@api_view(['GET'])
def get_tracks_of_my_library(request):
    """
    Get all tracks of My Library of a user
    """
    session = utils.check_auth_token(request)
    if not session:
        return utils.invalid_auth_response()

    tracks = session.user.profile.mylibrary.tracks.all()
    #serializer = serializers.TrackSerializer(tracks, many=True)
    data = utils.paginate_items(request, tracks, user=session.user)

    if tracks:
        msg = "There are %s tracks found" %len(tracks)
        msg_code = "ok"
        return utils.successful_response(msg, msg_code, **data)
    msg = "There is no track found"
    msg_code = "empty_library"
    return utils.failed_response(msg, msg_code)


@api_view(['GET'])
def like(request, trackid):
    """
    Like a track
    """
    session = utils.check_auth_token(request)
    if not session:
        return utils.invalid_auth_response()

    try:
        track = models.Track.objects.get(pk=trackid)
    except models.Track.DoesNotExist:
        msg = "The track with id %s does not exist" %trackid
        return utils.failed_response(msg, "not_found")

    track.likes.add(session.user)
    track.save()

    session.user.profile.mylibrary.tracks.add(track)
    session.user.profile.mylibrary.save()

    return utils.successful_response("Successfully", "ok")


@api_view(['GET'])
def unlike(request, trackid):
    """
    Unlike a track
    """
    session = utils.check_auth_token(request)
    if not session:
        return utils.invalid_auth_response()

    try:
        track = models.Track.objects.get(pk=trackid)
    except models.Track.DoesNotExist:
        msg = "The track with id %s does not exist" %trackid
        return utils.failed_response(msg, "not_found")


    if track.likes.filter(pk=session.user.pk).exists():
        session.user.profile.mylibrary.tracks.add(track)
        session.user.profile.mylibrary.save()
        track.likes.remove(session.user)
        track.save()

    return utils.successful_response("Successfully", "ok")


@api_view(['GET'])
def is_liked(request, trackid):
    """
    Check if a track is liked
    """
    session = utils.check_auth_token(request)
    if not session:
        return utils.invalid_auth_response()

    try:
        track = models.Track.objects.get(pk=trackid)
    except models.Track.DoesNotExist:
        msg = "The track with id %s does not exist" %trackid
        return utils.failed_response(msg, "not_found")


    if track.likes.filter(pk=session.user.pk).exists():
        return utils.successful_response("Liked", "liked")
    else:
        return utils.successful_response("Not yet", "not")


@api_view(['GET'])
def download(request, trackid):
    """
    Increasing download count of a track by 1
    """
    session = utils.check_auth_token(request)
    if not session:
        return utils.invalid_auth_response()

    try:
        track = models.Track.objects.get(pk=trackid)
    except models.Track.DoesNotExist:
        msg = "The track with id %s does not exist" %trackid
        return utils.failed_response(msg, "not_found")

    track.download_count += 1

    if track.download_count % 500 == 0:
        if track.price < 150:
            track.price += 15

    track.save()

    return utils.successful_response("Successfully", "ok")


@api_view(['GET'])
def list_my_stations(request):
    """
    List all stations of a user
    """
    session = utils.check_auth_token(request)
    if not session:
        return utils.invalid_auth_response()

    stations1 = session.user.profile.mystations.all()

    stations2 = session.user.station_set.all()

    stations = []

    for st in list(itertools.chain(stations1, stations2)):
        if st not in stations:
            stations.append(st)

    data = utils.paginate_items(request, stations, "station", user=session.user)

    if not stations:
        msg = "There is no station"
        return utils.failed_response(msg, "not_found")

    msg = "There are %s stations found" %len(stations)
    return utils.successful_response(msg, "ok", **data)


@api_view(['GET', 'PUT', 'DELETE'])
def manage_station(request, station_id):
    """
    List all tracks of a station
    Update station name

    """
    session = utils.check_auth_token(request)
    if not session:
        return utils.invalid_auth_response()

    try:
        station = models.Station.objects.get(pk=station_id)
    except:
        msg = "There is no station with id %s" %station_id
        return utils.failed_response(msg, "not_found")

    if request.method == "GET":
        if station.user != session.user:
            if station.privacy_level != 1:
                msg = "You don't have permission to view this station"
                return utils.failed_response(msg, "permission_denied")

        tracks = utils.get_station_tracks(station)

        if not tracks:
            msg = "There is no track in this station"
            return utils.failed_response(msg, "empty_station")

        context = {"current_user": session.user}
        serializer = serializers.StationSerializer(station, context=context)

        data = utils.paginate_items(request, tracks, user=session.user)
        data.update(serializer.data)

        msg = "There are %s tracks found" %len(tracks)
        return utils.successful_response(msg, "ok", **data)

    if request.method == "PUT":
        if station.user != session.user:
            msg = "You don't have permission to do this action"
            return utils.failed_response(msg, "permission_denied")

        station_name = request.DATA.get('name', None)

        photo = request.FILES.get('photo', None)

        return utils.update_station(station, station_name, photo, session.user)

    if request.method == "DELETE":
        if station.user != session.user:
            msg = "You don't have permission to do this action"
            return utils.failed_response(msg, "permission_denied")

        try:
            old_photo = station.photo_s3_name
            old_thumb = station.thumbnail_s3_name
            utils.delete_s3_object(old_photo, False)
            utils.delete_s3_object(old_thumb, False)
        except AttributeError:
            pass

        station.delete()
        msg = "The station with id %s was deleted" %station_id
        return utils.successful_response(msg, "ok")


@api_view(['POST'])
def create_station(request):
    """
    Create a station
    """
    session = utils.check_auth_token(request)
    if not session:
        return utils.invalid_auth_response()

    genre = request.DATA.get("genre", None)
    mood = request.DATA.get("mood", None)
    bpm = request.DATA.get("bpm", 0)
    photo = request.FILES.get('photo', None)
    name = request.DATA.get("name", None)
    hashtags = request.DATA.get("hashtags", None)

    if not (genre and mood and name and photo):
        misses = []
        if not genre:
            misses.append("genre")

        if not mood:
            misses.append("mood")

        if not name:
            misses.append("name")

        if not photo:
            misses.append("photo")

        msg = "There are missed fields: " + ",".join(misses)
        return utils.failed_response(msg, "empty_fields")

    if bpm:
        bpm = bpm.split(",")
        if len(bpm) != 2:
            msg = "Invalid bpm. This parameter should be 'min_bpm, max_bpm'"
            return utils.failed_response(msg, "invalid_bpm")

    return utils.create_station(session.user, name, photo, genre, mood, bpm, hashtags)


@api_view(['GET'])
def subcribe_station(request, station_id):
    """
    Add a station to My Stations
    """
    session = utils.check_auth_token(request)
    if not session:
        return utils.invalid_auth_response()

    try:
        station = models.Station.objects.get(pk=station_id)
    except:
        msg = "There is no station with id %s" %station_id
        return utils.failed_response(msg, "not_found")

    models.StationSubscriber.objects.get_or_create(profile=session.user.profile,
                                                         station=station)

    return utils.successful_response("Subscribed", "ok")


@api_view(['GET'])
def unsubcribe_station(request, station_id):
    """
    Remove a station from My Stations
    """
    session = utils.check_auth_token(request)
    if not session:
        return utils.invalid_auth_response()

    try:
        station = models.Station.objects.get(pk=station_id)
    except:
        msg = "There is no station with id %s" %station_id
        return utils.failed_response(msg, "not_found")

    try:
        subscriber = models.StationSubscriber.objects.get(profile=session.user.profile,
                                                          station=station)
        subscriber.delete()
    except models.StationSubscriber.MultipleObjectsReturned:
        subscribers = models.StationSubscriber.objects.filter(profile=session.user.profile,
                                                          station=station)
        for subscriber in subscribers:
            subscriber.delete()


    return utils.successful_response("Unsubcribed", "ok")


@api_view(['GET'])
def search_stations(request):
    """
    Search stations by name
    """
    session = utils.check_auth_token(request)
    if not session:
        return utils.invalid_auth_response()

    search_term = request.QUERY_PARAMS.get("search_term", "")
    if not search_term:
        return utils.failed_response('Search term is empty',
                                     'empty_fields')

    search_term = search_term.strip()
    stations = models.Station.objects.filter(
        name__icontains=search_term, privacy_level=1)[:1000]
    data = utils.paginate_items(
        request, stations, "station", user=session.user)

    if not stations:
        msg = "There is no station found"
        return utils.failed_response(msg, "not_found")

    msg = "There are %s stations found" %len(stations)
    return utils.successful_response(msg, "ok", **data)


@api_view(['GET'])
def get_trending_stations(request):
    """
    Get list of trending stations
    """
    session = utils.check_auth_token(request)
    if not session:
        return utils.invalid_auth_response()

    stations = utils.get_trending_stations()
    data = utils.paginate_items(request, stations, "station", user=session.user)

    if not stations:
        msg = "There is no station"
        return utils.failed_response(msg, "not_found")

    msg = "There are %s stations found" %len(stations)
    return utils.successful_response(msg, "ok", **data)


@api_view(['GET'])
def list_stations(request, userid):
    """
    List all stations of a user
    """
    session = utils.check_auth_token(request)
    if not session:
        return utils.invalid_auth_response()

    try:
        user = User.objects.get(pk=userid)
    except User.DoesNotExist:
        msg = "The user with id %s does not exist" %userid
        return utils.failed_response(msg, "invalid_user")

    stations1 = user.profile.mystations.filter(privacy_level=1)

    stations2 = user.station_set.filter(privacy_level=1)

    stations = []
    for st in list(itertools.chain(stations1, stations2)):
        if st not in stations:
            stations.append(st)

    data = utils.paginate_items(request, stations, "station", user=session.user)

    if not stations:
        msg = "There is no station"
        return utils.failed_response(msg, "not_found")

    msg = "There are %s stations found" %len(stations)
    return utils.successful_response(msg, "ok", **data)


@api_view(['GET'])
def get_station_info(request, station_id):
    """
    Add a station to My Stations
    """
    session = utils.check_auth_token(request)
    if not session:
        return utils.invalid_auth_response()

    try:
        station = models.Station.objects.get(pk=station_id)
    except:
        msg = "There is no station with id %s" %station_id
        return utils.failed_response(msg, "not_found")

    if station.user != session.user:
        if station.privacy_level != 1:
            msg = "You don't have permission to view this station"
            return utils.failed_response(msg, "permission_denied")

    context = {"current_user": session.user}
    serializer = serializers.StationSerializer(station, context=context)
    msg = "Successfully"
    return utils.successful_response(msg, "ok", **serializer.data)


@api_view(['GET'])
def purchase(request, track_id):
    """
    Purchase a track. Increase that track purchases attribute value
    . Decrease current user amount (pinna amount)
    """
    session = utils.check_auth_token(request)
    if not session:
        return utils.invalid_auth_response()

    try:
        track = models.Track.objects.get(pk=track_id)
    except models.Track.DoesNotExist:
        msg = "There is no track with id %s" %track_id
        return utils.failed_response(msg, "not_found")

    if session.user.profile.amount < track.price:
        msg = "There is not enough PINNA coin in your account"
        return utils.failed_response(msg, "not_enough")

    track.purchases.add(session.user)

    track.user.profile.amount += track.price
    track.user.profile.save()

    session.user.profile.amount -= track.price
    session.user.profile.mylibrary.tracks.add(track)
    session.user.profile.mylibrary.save()
    session.user.profile.save()

    if track.purchases.count() % 100 == 0:
        if track.price < 150:
            track.price += 15

    track.save()

    msg = "Purchased successfully"
    return utils.successful_response(msg, "ok", amount=session.user.profile.amount)


@api_view(['GET'])
def get_ads(request):
    """
    Get Ads list and ad settings
    """
    session = utils.check_auth_token(request)
    if not session:
        return utils.invalid_auth_response()

    try:
        ads = models.PinnaAd.objects.all()

        data = utils.paginate_items(request, ads, "ad", user=session.user)

        setting = models.PinnaSettings.objects.get(pk=settings.PINNA_SETTING_ID)

        data.update({"play_after":setting.play_ad_after_songs})

        return utils.successful_response("Successfully", "ok", **data)
    except:
        _LOG.error(traceback.format_exc())
        msg = "Internal server error"
        return utils.failed_response(msg, "failed")
