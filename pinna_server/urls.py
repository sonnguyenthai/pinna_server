from django.conf.urls import patterns, include, url

from account.views import LogoutView
from account.views import ChangePasswordView

from pinna import views

urlpatterns = patterns('',
    url(r'^api/', include('pinna.urls')),

)

urlpatterns += patterns('',
    url(r'^$', views.homepage, name='home'),

    url(r'^manage/music-meta$', views.manage_musicmeta, name='music_meta_view'),
    url(r'^manage/add-music-meta$',
        views.MusicMetaCreate.as_view(),
        name='add_music_meta_view'),
    url(r'^manage/edit-music-meta$',
        views.MusicMetaUpdate.as_view(),
        name='edit_music_meta_view'),
    url(r'^manage/delete-music-meta$',
        views.MusicMetaDelete.as_view(),
        name='delete_music_meta_view'),

    url(r'^manage/station-list-json',
        views.StationListJson.as_view(),
        name='station_list_json'),
    url(r'^manage/station-manage$',
        views.station_list,
        name='station_manage_view'),
    url(r'^manage/station-add',
        views.StationCreate.as_view(),
        name='station_add_view'),
    url(r'^manage/station-edit',
        views.StationUpdate.as_view(),
        name='station_edit_view'),
    url(r'^manage/station-delete',
        views.StationDelete.as_view(),
        name='station_delete_view'),
    url(r'^manage/station-detail',
        views.station_detail,
        name='station_detail_view'),

    url(r'^manage/tracks',
        views.tracks_list,
        name='track_manage_view'),

    url(r'^manage/ad-list-json',
        views.AdListJson.as_view(),
        name='ad_list_json'),
    url(r'^manage/ads',
        views.ads_list,
        name='ads_manage_view'),
    url(r'^manage/ad-create',
        views.AdCreate.as_view(),
        name='ad_create_view'),
    url(r'^manage/ad-delete',
        views.AdDelete.as_view(),
        name='ad_delete_view'),

    url(r'^manage/settings',
        views.PinnaSettingsUpdate.as_view(),
        name='settings_view'),

    url(r'^manage/user-list-json',
        views.UserListJson.as_view(),
        name='user_list_json'),
    url(r'^manage/users',
        views.user_list,
        name='user_manage_view'),
    url(r'^manage/add-coins',
        views.AddCoinsView.as_view(),
        name='add_coins_view'),
)#delete_music_meta_view

urlpatterns += patterns('',
    url(r"^password/$", views.ChangePasswordView.as_view(), name="account_password"),
    url(r"^logout/$", LogoutView.as_view(), name="account_logout"),
    url(r"^login/$", views.LoginView.as_view(), name="pinna_login"),
)