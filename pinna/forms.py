from django import forms
from django.utils.translation import ugettext_lazy as _

import models


class AddMusicMetaForm(forms.Form):
    """
    """
    name = forms.CharField(
        label=_("Name"),
        max_length=30,
        widget=forms.TextInput(),
        required=True
    )
    type = forms.ChoiceField(
        label=_("Type"),
        choices= models.MusicMeta.META_TYPES,
        required=False
    )

    def clean_name(self):
        value = self.cleaned_data["name"]
        if self.initial.get("name") == value:
            return value
        qs = models.MusicMeta.objects.filter(name__iexact=value)
        if not qs.exists():
            return value
        raise forms.ValidationError(_("This name already existed"))


def genres():
    return [(genre.id, genre.name)
            for genre in models.MusicMeta.objects.filter(type='genre')]

def moods():
    return [(mood.id, mood.name)
            for mood in models.MusicMeta.objects.filter(type='mood')]


class StationForm(forms.Form):
    """
    """
    name = forms.CharField(
        label=_("Name"),
        max_length=100,
        widget=forms.TextInput(),
        required=True
    )

    photo = forms.ImageField(
        label=_('Photo'),
        required=True,
    )

    genre = forms.ChoiceField(
        label=_("Genre"),
        choices= genres(),
        required=True
    )

    mood = forms.ChoiceField(
        label=_("Mood"),
        choices= moods(),
        required=True
    )

    bpm = forms.CharField(
        label=_('BPM'),
        max_length=10,
        widget=forms.TextInput(),
        required=False,
        help_text = _("Range of BPMs. Example: 120, 320"),
    )

    hashtags = forms.CharField(
        label=_('Hashtags'),
        max_length=100,
        widget=forms.TextInput(),
        required=False,
        help_text = _("Example: hashtag1, hashtag2 ..."),
    )


class StationEditForm(forms.Form):
    """
    """
    name = forms.CharField(
        label=_("Name"),
        max_length=100,
        widget=forms.TextInput(),
        required=False
    )

    photo = forms.ImageField(
        label=_('Photo'),
        required=False,
    )


class AdForm(forms.Form):
    """
    """
    name = forms.CharField(
        label=_("Name"),
        max_length=100,
        widget=forms.NumberInput(),
        required=True
    )

    file = forms.FileField(
        label=_('File'),
        required=True,
    )


class AddCoinsForm(forms.Form):
    """
    """
    coins = forms.IntegerField(
        label=_("Coins"),
        widget=forms.TextInput(),
        required=True
    )

    profile = forms.IntegerField(
        widget=forms.HiddenInput(),
    )