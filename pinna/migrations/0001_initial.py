# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Profile'
        db.create_table(u'pinna_profile', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['auth.User'], unique=True)),
            ('display_photo', self.gf('django.db.models.fields.CharField')(max_length=100, null=True)),
            ('amount', self.gf('django.db.models.fields.FloatField')(default=0)),
            ('mytracks', self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', to=orm['pinna.Library'])),
            ('mylibrary', self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', to=orm['pinna.Library'])),
        ))
        db.send_create_signal(u'pinna', ['Profile'])

        # Adding M2M table for field followers on 'Profile'
        m2m_table_name = db.shorten_name(u'pinna_profile_followers')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('profile', models.ForeignKey(orm[u'pinna.profile'], null=False)),
            ('user', models.ForeignKey(orm[u'auth.user'], null=False))
        ))
        db.create_unique(m2m_table_name, ['profile_id', 'user_id'])

        # Adding model 'PinnaSession'
        db.create_table(u'pinna_pinnasession', (
            ('key', self.gf('django.db.models.fields.CharField')(max_length=40, primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('created_time', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('expired_time', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2014, 10, 4, 0, 0))),
            ('is_active', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal(u'pinna', ['PinnaSession'])

        # Adding model 'Track'
        db.create_table(u'pinna_track', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('url', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('genre', self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', to=orm['pinna.MusicMeta'])),
            ('mood', self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', to=orm['pinna.MusicMeta'])),
            ('bpm', self.gf('django.db.models.fields.IntegerField')()),
            ('like_count', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('download_count', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('author', self.gf('django.db.models.fields.CharField')(max_length=200, null=True)),
            ('artist', self.gf('django.db.models.fields.CharField')(max_length=200, null=True)),
            ('duration', self.gf('django.db.models.fields.FloatField')(default=0)),
            ('price', self.gf('django.db.models.fields.FloatField')(default=0)),
            ('date_created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal(u'pinna', ['Track'])

        # Adding unique constraint on 'Track', fields ['user', 'name']
        db.create_unique(u'pinna_track', ['user_id', 'name'])

        # Adding M2M table for field hashtags on 'Track'
        m2m_table_name = db.shorten_name(u'pinna_track_hashtags')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('track', models.ForeignKey(orm[u'pinna.track'], null=False)),
            ('hashtag', models.ForeignKey(orm[u'pinna.hashtag'], null=False))
        ))
        db.create_unique(m2m_table_name, ['track_id', 'hashtag_id'])

        # Adding model 'Library'
        db.create_table(u'pinna_library', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('date_created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal(u'pinna', ['Library'])

        # Adding M2M table for field tracks on 'Library'
        m2m_table_name = db.shorten_name(u'pinna_library_tracks')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('library', models.ForeignKey(orm[u'pinna.library'], null=False)),
            ('track', models.ForeignKey(orm[u'pinna.track'], null=False))
        ))
        db.create_unique(m2m_table_name, ['library_id', 'track_id'])

        # Adding model 'Playlist'
        db.create_table(u'pinna_playlist', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('date_created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal(u'pinna', ['Playlist'])

        # Adding unique constraint on 'Playlist', fields ['user', 'name']
        db.create_unique(u'pinna_playlist', ['user_id', 'name'])

        # Adding M2M table for field tracks on 'Playlist'
        m2m_table_name = db.shorten_name(u'pinna_playlist_tracks')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('playlist', models.ForeignKey(orm[u'pinna.playlist'], null=False)),
            ('track', models.ForeignKey(orm[u'pinna.track'], null=False))
        ))
        db.create_unique(m2m_table_name, ['playlist_id', 'track_id'])

        # Adding model 'Station'
        db.create_table(u'pinna_station', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('bpm', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('date_created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal(u'pinna', ['Station'])

        # Adding unique constraint on 'Station', fields ['user', 'name']
        db.create_unique(u'pinna_station', ['user_id', 'name'])

        # Adding M2M table for field genres on 'Station'
        m2m_table_name = db.shorten_name(u'pinna_station_genres')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('station', models.ForeignKey(orm[u'pinna.station'], null=False)),
            ('musicmeta', models.ForeignKey(orm[u'pinna.musicmeta'], null=False))
        ))
        db.create_unique(m2m_table_name, ['station_id', 'musicmeta_id'])

        # Adding M2M table for field moods on 'Station'
        m2m_table_name = db.shorten_name(u'pinna_station_moods')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('station', models.ForeignKey(orm[u'pinna.station'], null=False)),
            ('musicmeta', models.ForeignKey(orm[u'pinna.musicmeta'], null=False))
        ))
        db.create_unique(m2m_table_name, ['station_id', 'musicmeta_id'])

        # Adding M2M table for field tracks on 'Station'
        m2m_table_name = db.shorten_name(u'pinna_station_tracks')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('station', models.ForeignKey(orm[u'pinna.station'], null=False)),
            ('track', models.ForeignKey(orm[u'pinna.track'], null=False))
        ))
        db.create_unique(m2m_table_name, ['station_id', 'track_id'])

        # Adding model 'Hashtag'
        db.create_table(u'pinna_hashtag', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=100)),
            ('date_created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal(u'pinna', ['Hashtag'])

        # Adding model 'MusicMeta'
        db.create_table(u'pinna_musicmeta', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=100)),
            ('type', self.gf('django.db.models.fields.CharField')(max_length='5')),
            ('date_created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal(u'pinna', ['MusicMeta'])


    def backwards(self, orm):
        # Removing unique constraint on 'Station', fields ['user', 'name']
        db.delete_unique(u'pinna_station', ['user_id', 'name'])

        # Removing unique constraint on 'Playlist', fields ['user', 'name']
        db.delete_unique(u'pinna_playlist', ['user_id', 'name'])

        # Removing unique constraint on 'Track', fields ['user', 'name']
        db.delete_unique(u'pinna_track', ['user_id', 'name'])

        # Deleting model 'Profile'
        db.delete_table(u'pinna_profile')

        # Removing M2M table for field followers on 'Profile'
        db.delete_table(db.shorten_name(u'pinna_profile_followers'))

        # Deleting model 'PinnaSession'
        db.delete_table(u'pinna_pinnasession')

        # Deleting model 'Track'
        db.delete_table(u'pinna_track')

        # Removing M2M table for field hashtags on 'Track'
        db.delete_table(db.shorten_name(u'pinna_track_hashtags'))

        # Deleting model 'Library'
        db.delete_table(u'pinna_library')

        # Removing M2M table for field tracks on 'Library'
        db.delete_table(db.shorten_name(u'pinna_library_tracks'))

        # Deleting model 'Playlist'
        db.delete_table(u'pinna_playlist')

        # Removing M2M table for field tracks on 'Playlist'
        db.delete_table(db.shorten_name(u'pinna_playlist_tracks'))

        # Deleting model 'Station'
        db.delete_table(u'pinna_station')

        # Removing M2M table for field genres on 'Station'
        db.delete_table(db.shorten_name(u'pinna_station_genres'))

        # Removing M2M table for field moods on 'Station'
        db.delete_table(db.shorten_name(u'pinna_station_moods'))

        # Removing M2M table for field tracks on 'Station'
        db.delete_table(db.shorten_name(u'pinna_station_tracks'))

        # Deleting model 'Hashtag'
        db.delete_table(u'pinna_hashtag')

        # Deleting model 'MusicMeta'
        db.delete_table(u'pinna_musicmeta')


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'pinna.hashtag': {
            'Meta': {'object_name': 'Hashtag'},
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'})
        },
        u'pinna.library': {
            'Meta': {'object_name': 'Library'},
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'tracks': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['pinna.Track']", 'symmetrical': 'False'})
        },
        u'pinna.musicmeta': {
            'Meta': {'object_name': 'MusicMeta'},
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': "'5'"})
        },
        u'pinna.pinnasession': {
            'Meta': {'object_name': 'PinnaSession'},
            'created_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'expired_time': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2014, 10, 4, 0, 0)'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '40', 'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'pinna.playlist': {
            'Meta': {'unique_together': "(('user', 'name'),)", 'object_name': 'Playlist'},
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'tracks': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['pinna.Track']", 'symmetrical': 'False'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'pinna.profile': {
            'Meta': {'object_name': 'Profile'},
            'amount': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'display_photo': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'}),
            'followers': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'followers'", 'null': 'True', 'to': u"orm['auth.User']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mylibrary': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': u"orm['pinna.Library']"}),
            'mytracks': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': u"orm['pinna.Library']"}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['auth.User']", 'unique': 'True'})
        },
        u'pinna.station': {
            'Meta': {'unique_together': "(('user', 'name'),)", 'object_name': 'Station'},
            'bpm': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'genres': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'station_genres'", 'symmetrical': 'False', 'to': u"orm['pinna.MusicMeta']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'moods': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'station_moods'", 'symmetrical': 'False', 'to': u"orm['pinna.MusicMeta']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'tracks': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['pinna.Track']", 'symmetrical': 'False'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'pinna.track': {
            'Meta': {'unique_together': "(('user', 'name'),)", 'object_name': 'Track'},
            'artist': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True'}),
            'author': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True'}),
            'bpm': ('django.db.models.fields.IntegerField', [], {}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'download_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'duration': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'genre': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': u"orm['pinna.MusicMeta']"}),
            'hashtags': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['pinna.Hashtag']", 'null': 'True', 'symmetrical': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'like_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'mood': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': u"orm['pinna.MusicMeta']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'price': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        }
    }

    complete_apps = ['pinna']