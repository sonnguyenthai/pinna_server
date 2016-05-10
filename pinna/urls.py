from django.conf.urls import patterns, url

import user_api
import music_api
#import views

### USER API endpoints
urlpatterns = patterns('',
    url(r'^user/create$', user_api.create_user),
    url(r'^user/login$', user_api.login),
    url(r'^user/logout$', user_api.logout),
    #url(r'^user/(?P<userid>[0-9]+)/$')
    url(r'^user/profile$', user_api.get_profile),
    url(r'^user/update$', user_api.update),
    url(r'^user/changepassword$', user_api.change_password),
    url(r'^user/(?P<user_id>[0-9]+)/profile$', user_api.get_user_profile),

    url(r'^user/follow/(?P<userid>[0-9]+)$', user_api.follow),
    url(r'^user/unfollow/(?P<userid>[0-9]+)$', user_api.unfollow),
    url(r'^user/followers/(?P<userid>[0-9]+)$', user_api.get_followers),
    url(r'^user/add_coins$', user_api.add_coins),

)

### MUSIC API endpoints
urlpatterns += patterns('',
    url(r'^music/upload$', music_api.upload_track),
    url(r'^music/(?P<trackid>[0-9]+)$', music_api.manage_track),
    url(r'^music/search$', music_api.search_track),
    url(r'^music/like/(?P<trackid>[0-9]+)$', music_api.like),
    url(r'^music/unlike/(?P<trackid>[0-9]+)$', music_api.unlike),
    url(r'^music/is_liked/(?P<trackid>[0-9]+)$', music_api.is_liked),
    url(r'^music/download/(?P<trackid>[0-9]+)$', music_api.download),
    url(r'^music/purchase/(?P<track_id>[0-9]+)$', music_api.purchase),

    url(r'^music/genres$', music_api.list_genres),
    url(r'^music/moods$', music_api.list_moods),
    url(r'^music/mytracks/tracks$', music_api.get_my_tracks),
    url(r'^music/mylibrary/tracks$', music_api.get_tracks_of_my_library),

    url(r'^music/playlists$', music_api.list_playlists),
    url(r'^music/playlist/create$', music_api.create_playlist),
    url(r'^music/playlist/(?P<playlist_id>[0-9]+)$', music_api.manage_playlist),
    url(r'^music/playlist/(?P<playlist_id>[0-9]+)/add$', music_api.add_tracks_to_playlist),
    url(r'^music/playlist/(?P<playlist_id>[0-9]+)/remove$', music_api.remove_tracks_from_playlist),

    url(r'^music/stations$', music_api.list_my_stations),
    url(r'^music/station/create$', music_api.create_station),
    url(r'^music/station/trending', music_api.get_trending_stations),
    url(r'^music/station/(?P<station_id>[0-9]+)$', music_api.manage_station),
    url(r'^music/station/(?P<station_id>[0-9]+)/subscribe$', music_api.subcribe_station),
    url(r'^music/station/(?P<station_id>[0-9]+)/unsubscribe$', music_api.unsubcribe_station),
    url(r'^music/station/search$', music_api.search_stations),
    url(r'^music/station/my_stations/(?P<userid>[0-9]+)$', music_api.list_stations),
    url(r'^music/station/(?P<station_id>[0-9]+)/details$', music_api.get_station_info),

    url(r'^music/get_ads$', music_api.get_ads),

)
