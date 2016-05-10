import os
import logging
import traceback
from datetime import datetime, timedelta

from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User
from django.contrib import messages
from django.conf import settings
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.timezone import utc
from django.views.generic.edit import FormView
from django.views.generic.edit import CreateView
from django.views.generic.edit import UpdateView, DeleteView

import account.forms
import account.views

from aggregate_if import Count

from braces.views import SuperuserRequiredMixin, LoginRequiredMixin

from django_datatables_view.base_datatable_view import BaseDatatableView

import models
import forms
import utils
import serializers


LOG = logging.getLogger("django.request")


class LoginView(account.views.LoginView):
    template_name = "login.html"

    def after_login(self, form):
        try:
            u = form.user.profile
        except models.Profile.DoesNotExist:
            mylib = models.Library.objects.create()
            models.Profile.objects.create(user=form.user, mylibrary=mylib)

        try:
            models.PinnaSettings.objects.get(pk=settings.PINNA_SETTING_ID)
        except models.PinnaSettings.DoesNotExist:
            models.PinnaSettings.objects.create(id=settings.PINNA_SETTING_ID)

        super(LoginView, self).after_login(form)


class ChangePasswordView(LoginRequiredMixin, account.views.ChangePasswordView):
    template_name = "password_change.html"


@user_passes_test(lambda u: u.is_superuser)
def homepage(request):
    """
    """
    users = User.objects.count()
    stations = models.Station.objects.count()
    tracks = models.Track.objects.count()
    playlists = models.Playlist.objects.count()
    m1_active = "active"

    return render_to_response("homepage.html", locals(), context_instance=RequestContext(request))


@user_passes_test(lambda u: u.is_superuser)
def manage_musicmeta(request):
    """
    """
    metas = models.MusicMeta.objects.all()
    m3_active = "active"

    return render_to_response("musicmeta_manage_page.html", locals(), context_instance=RequestContext(request))


class MusicMetaCreate(LoginRequiredMixin, SuperuserRequiredMixin ,CreateView):
    model = models.MusicMeta
    fields = ['name', 'type']
    template_name = "musicmeta_add_form.html"
    success_url = "/manage/music-meta"

    def get_context_data(self, **kwargs):
        ctx = kwargs
        ctx.update({
            "m3_active": "active",
        })
        return ctx

    def form_valid(self, form):
        messages.add_message(self.request,
                             messages.INFO,
                             "Created new item successfully")

        return super(MusicMetaCreate, self).form_valid(form)


class MusicMetaUpdate(LoginRequiredMixin, SuperuserRequiredMixin, UpdateView):
    models = models.MusicMeta
    fields = ['name', 'type']
    template_name = "musicmeta_add_form.html"
    success_url = "/manage/music-meta"

    def get_context_data(self, **kwargs):
        ctx = kwargs
        ctx.update({
            "m3_active": "active",
        })
        return ctx

    def form_valid(self, form):
        messages.add_message(self.request,
                             messages.INFO,
                             "Updated item successfully")

        return super(MusicMetaUpdate, self).form_valid(form)

    def get_object(self, queryset=None):
        obj = models.MusicMeta.objects.get(id=self.request.GET.get('id'))
        return obj


class MusicMetaDelete(LoginRequiredMixin, SuperuserRequiredMixin, DeleteView):
    models = models.MusicMeta
    template_name = "object_confirm_delete.html"
    success_url = "/manage/music-meta"

    def get_context_data(self, **kwargs):
        ctx = kwargs
        ctx.update({
            "m3_active": "active",
        })
        return ctx

    def post(self, request, *args, **kwargs):
        messages.add_message(self.request,
                             messages.INFO,
                             "Deleted item successfully")

        return super(MusicMetaDelete, self).post(request, *args, **kwargs)

    def get_object(self, queryset=None):
        obj = models.MusicMeta.objects.get(id=self.request.GET.get('id'))
        return obj


class StationListJson(LoginRequiredMixin, SuperuserRequiredMixin, BaseDatatableView):
    """
    """
    model = models.Station
    columns = ['id', 'name', 'user', 'privacy_level', 'subscribers', 'date_created']
    order_columns = columns

    # def get_initial_queryset(self):
    #     return models.Station.objects.all()

    def filter_queryset(self, qs):
        # use request parameters to filter queryset

        # simple example:
        if self.request.method == "GET":
            search = self.request.GET.get('search[value]', None)
        elif self.request.method == "POST":
            search = self.request.POST.get('search[value]', None)

        if search:
            qs = qs.filter(name__icontains=search)

        return qs

    def prepare_results(self, qs):
        # prepare list with output column data
        # queryset is already paginated here
        json_data = []
        for item in qs:
            row = []
            row.append(item.id)
            row.append(item.name)
            row.append(item.user.first_name)
            row.append(item.privacy_level)
            row.append(item.subscribers.count())
            row.append(item.date_created.strftime("%Y-%m-%d %H:%M:%S"))
            action = """
                <a href="/manage/station-detail?id={id}">
                    Detail
                </a>/
                <a href="/manage/station-edit?id={id}">
                    Edit
                </a>/
                <a href="/manage/station-delete?id={id}">
                    Delete
                </a>
            """.format(id=item.id)
            row.append(action)
            json_data.append(row)
        return json_data


@user_passes_test(lambda u: u.is_superuser)
def station_list(request):
    m2_active = "active"
    return render_to_response("station_manage_page.html",
                              locals(), context_instance=RequestContext(request))


class StationCreate(LoginRequiredMixin, SuperuserRequiredMixin, FormView):
    model = models.Station
    form_class = forms.StationForm
    template_name = "station_add_form.html"
    success_url = "/manage/station-manage"

    def get_context_data(self, **kwargs):
        ctx = kwargs
        ctx.update({
            "m2_active": "active",
        })
        return ctx

    def form_valid(self, form):
        user = self.request.user
        name = form.cleaned_data['name']
        photo = form.cleaned_data['photo']
        genre_id = form.cleaned_data['genre']
        mood_id = form.cleaned_data['mood']
        hashtags = form.cleaned_data['hashtags']
        bpm = form.cleaned_data['bpm']

        response = utils.create_station(
            user, name, photo, genre_id, mood_id, bpm, hashtags)
        response = response.data

        if response['msg_code'] == 'ok':
            messages.add_message(self.request,
                                 messages.INFO,
                                 "Created new station successfully")

        else:
            messages.add_message(self.request,
                                 messages.ERROR,
                                 response['message'])

        return super(StationCreate, self).form_valid(form)


class StationUpdate(LoginRequiredMixin, SuperuserRequiredMixin, FormView):
    models = models.Station
    form_class = forms.StationEditForm
    template_name = "station_edit_form.html"
    success_url = "/manage/station-manage"

    def get_context_data(self, **kwargs):
        ctx = kwargs
        ctx.update({
            "m2_active": "active",
        })
        return ctx

    def get_initial(self):
        initial = super(StationUpdate, self).get_initial()
        initial["name"] = self.get_object().name
        #initial["language"] = self.request.user.account.language
        return initial

    def form_valid(self, form):
        user = self.request.user
        name = form.cleaned_data['name']
        photo = form.cleaned_data['photo']

        response = utils.update_station(self.get_object(), name, photo, user)
        response = response.data

        if response['msg_code'] == 'ok':
            messages.add_message(self.request,
                                 messages.INFO,
                                 response['message'])

        else:
            messages.add_message(self.request,
                                 messages.ERROR,
                                 response['message'])

        return super(StationUpdate, self).form_valid(form)

    def get_object(self, queryset=None):
        obj = models.Station.objects.get(id=self.request.GET.get('id'))
        return obj


class StationDelete(LoginRequiredMixin, SuperuserRequiredMixin, DeleteView):
    models = models.Station
    template_name = "object_confirm_delete.html"
    success_url = "/manage/station-manage"

    def get_context_data(self, **kwargs):
        ctx = kwargs
        ctx.update({
            "m2_active": "active",
        })
        return ctx

    def post(self, request, *args, **kwargs):

        station = self.get_object()
        if station.photo_s3_name:
            utils.delete_s3_object(station.photo_s3_name, False)
        if station.thumbnail_s3_name:
            utils.delete_s3_object(station.thumbnail_s3_name, False)

        messages.add_message(self.request,
                             messages.INFO,
                             "Deleted item successfully")

        return super(StationDelete, self).post(request, *args, **kwargs)

    def get_object(self, queryset=None):
        obj = models.Station.objects.get(id=self.request.GET.get('id'))
        return obj


@user_passes_test(lambda u: u.is_superuser)
def station_detail(request):
    """
    """
    try:
        station = models.Station.objects.get(id=request.GET.get('id'))
    except models.Station.DoesNotExist:
        station = None
    else:
        serializer = serializers.StationSerializer(station)
        data = serializer.data

        data['genre'] = station.genre.name
        data['mood'] = station.mood.name

        date_created = station.date_created.strftime("%Y-%m-%d %H:%M:%S")

    m2_active = "active"

    return render_to_response("station_detail.html",
                              locals(), context_instance=RequestContext(request))


@user_passes_test(lambda u: u.is_superuser)
def tracks_list(request):
    qs = models.Track.objects.annotate(
        like_count=Count('likes')).order_by('download_count', 'like_count')[:100]

    data = []
    for item in qs:
        row = {}
        row['id'] = item.id
        row['name'] = item.name
        row['user'] = item.user.username
        row['privacy'] = item.privacy_level
        row['downloads'] = item.download_count
        row['likes'] = item.like_count
        url = utils.create_signed_url(item.url)
        row['url'] = url
        row['url_time'] = int(settings.PINNA_TRACK_EXPIRATION_TIME/3600)
        row['purchases'] = item.purchases.count()
        row['date'] = item.date_created.strftime("%Y-%m-%d %H:%M:%S")
        data.append(row)

    m4_active = "active"
    return render_to_response("track_manage_page.html",
                              locals(), context_instance=RequestContext(request))


class AdListJson(LoginRequiredMixin, SuperuserRequiredMixin, BaseDatatableView):
    """
    """
    model = models.PinnaAd
    columns = ['id', 'name', 'url', 'date_created']
    order_columns = columns


    def filter_queryset(self, qs):
        # use request parameters to filter queryset

        # simple example:
        if self.request.method == "GET":
            search = self.request.GET.get('search[value]', None)
        elif self.request.method == "POST":
            search = self.request.POST.get('search[value]', None)

        if search:
            qs = qs.filter(name__icontains=search)

        return qs

    def prepare_results(self, qs):
        # prepare list with output column data
        # queryset is already paginated here
        json_data = []
        for item in qs:
            row = []
            row.append(item.id)
            name = """
                <a href="{url}"> {name} </a>
            """.format(url=item.url, name=item.name)
            row.append(name)
            row.append(item.date_created.strftime("%Y-%m-%d %H:%M:%S"))
            action = """
                <a href="/manage/ad-delete?id={id}">
                    Delete
                </a>
            """.format(id=item.id)
            row.append(action)
            json_data.append(row)
        return json_data


@user_passes_test(lambda u: u.is_superuser)
def ads_list(request):
    m5_active = "active"
    return render_to_response("ad_manage_page.html",
                              locals(), context_instance=RequestContext(request))


class AdCreate(LoginRequiredMixin, SuperuserRequiredMixin, FormView):
    model = models.PinnaAd
    form_class = forms.AdForm
    template_name = "ad_add_form.html"
    success_url = "/manage/ads"

    def get_context_data(self, **kwargs):
        ctx = kwargs
        ctx.update({
            "m5_active": "active",
        })
        return ctx

    def form_valid(self, form):
        name = form.cleaned_data['name']
        file = form.cleaned_data['file']

        try:
            origin_name, ext = os.path.splitext(file.name)
            aws_name = 'pinna_ads/'\
                       + utils.generate_random_name(origin_name) + ext
            url = utils.add_object_via_cloudfront(aws_name, file, False)

            models.PinnaAd.objects.create(name=name, url=url, s3_name=aws_name)

            messages.add_message(self.request,
                                 messages.INFO,
                                 "Created new AD successfully")
        except Exception as e:
            LOG.error(traceback.format_exc())
            messages.add_message(self.request,
                                 messages.ERROR,
                                 "Can't create AD: %s" %e)

        return super(AdCreate, self).form_valid(form)


class AdDelete(LoginRequiredMixin, SuperuserRequiredMixin, DeleteView):
    models = models.PinnaAd
    template_name = "object_confirm_delete.html"
    success_url = "/manage/ads"

    def get_context_data(self, **kwargs):
        ctx = kwargs
        ctx.update({
            "m5_active": "active",
        })
        return ctx

    def post(self, request, *args, **kwargs):

        ad = self.get_object()
        if ad.s3_name:
            utils.delete_s3_object(ad.s3_name, False)

        messages.add_message(self.request,
                             messages.INFO,
                             "Deleted item successfully")

        return super(AdDelete, self).post(request, *args, **kwargs)

    def get_object(self, queryset=None):
        obj = models.PinnaAd.objects.get(id=self.request.GET.get('id'))
        return obj


class PinnaSettingsUpdate(LoginRequiredMixin, SuperuserRequiredMixin, UpdateView):
    models = models.PinnaSettings
    fields = ['play_ad_after_songs']
    template_name = "settings_form.html"
    success_url = "/manage/settings"

    def get_context_data(self, **kwargs):
        ctx = kwargs
        ctx.update({
            "m6_active": "active",
        })
        return ctx

    def form_valid(self, form):
        messages.add_message(self.request,
                             messages.INFO,
                             "Updated item successfully")

        return super(PinnaSettingsUpdate, self).form_valid(form)

    def get_object(self, queryset=None):
        obj = models.PinnaSettings.objects.get(id=settings.PINNA_SETTING_ID)
        return obj


class UserListJson(LoginRequiredMixin, SuperuserRequiredMixin, BaseDatatableView):
    """
    """
    model = models.User
    columns = ['id', 'username', 'first_name']
    order_columns = columns


    def filter_queryset(self, qs):
        # use request parameters to filter queryset

        # simple example:
        if self.request.method == "GET":
            search = self.request.GET.get('search[value]', None)
        elif self.request.method == "POST":
            search = self.request.POST.get('search[value]', None)

        if search:
            qs = qs.filter(username__icontains=search)

        return qs

    def prepare_results(self, qs):
        # prepare list with output column data
        # queryset is already paginated here
        json_data = []
        for item in qs:
            row = []
            row.append(item.id)
            row.append(item.username)

            admin = "No"
            if item.is_superuser:
                admin = "Yes"
            row.append(admin)

            row.append(item.first_name)
            row.append(item.profile.amount)
            row.append(item.profile.mystations.count())

            tracks = models.Track.objects.filter(user=item).count()
            row.append(tracks)

            action = """
                <a href="/manage/add-coins?id={id}">
                    Add Coins
                </a>
            """.format(id=item.id)
            row.append(action)
            json_data.append(row)
        return json_data


@user_passes_test(lambda u: u.is_superuser)
def user_list(request):
    m7_active = "active"
    return render_to_response("user_manage_page.html",
                              locals(), context_instance=RequestContext(request))


class AddCoinsView(LoginRequiredMixin, SuperuserRequiredMixin, FormView):
    form_class = forms.AddCoinsForm
    template_name =  "add_coins_form.html"
    success_url = "/manage/users"

    def get_context_data(self, **kwargs):
        ctx = kwargs
        ctx.update({
            "m7_active": "active",
            "user": self.get_user()
        })
        return ctx

    def get_initial(self):
        initial = super(AddCoinsView, self).get_initial()
        initial["profile"] = self.get_user().profile.id
        return initial

    def get_user(self):
        user_id = self.request.GET.get('id')
        user = models.User.objects.get(pk=user_id)
        return user

    def form_valid(self, form):
        coins = form.cleaned_data['coins']
        profile_id = form.cleaned_data['profile']

        try:
            profile = models.Profile.objects.get(pk=profile_id)
            profile.amount += int(coins)
            profile.save()

            messages.add_message(self.request,
                                 messages.INFO,
                                 "%s coins were added to %s account"
                                 %(coins, profile.user.username))
        except Exception as e:
            LOG.error(traceback.format_exc())
            messages.add_message(self.request,
                                 messages.ERROR,
                                 "Can't add coins: %s" %e)

        return super(AddCoinsView, self).form_valid(form)