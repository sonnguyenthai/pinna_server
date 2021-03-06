# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'PinnaOrder.user'
        db.add_column(u'pinna_pinnaorder', 'user',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True),
                      keep_default=False)

        # Adding field 'PinnaOrder.date_created'
        db.add_column(u'pinna_pinnaorder', 'date_created',
                      self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, default=datetime.datetime(2014, 11, 18, 0, 0), blank=True),
                      keep_default=False)


        # Changing field 'PinnaOrder.purchase_time'
        db.alter_column(u'pinna_pinnaorder', 'purchase_time', self.gf('django.db.models.fields.DateTimeField')())

    def backwards(self, orm):
        # Deleting field 'PinnaOrder.user'
        db.delete_column(u'pinna_pinnaorder', 'user_id')

        # Deleting field 'PinnaOrder.date_created'
        db.delete_column(u'pinna_pinnaorder', 'date_created')


        # Changing field 'PinnaOrder.purchase_time'
        db.alter_column(u'pinna_pinnaorder', 'purchase_time', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True))

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
        u'pinna.pinnaorder': {
            'Meta': {'object_name': 'PinnaOrder'},
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'order_id': ('django.db.models.fields.CharField', [], {'max_length': '100', 'primary_key': 'True'}),
            'purchase_data': ('django.db.models.fields.TextField', [], {}),
            'purchase_state': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'purchase_time': ('django.db.models.fields.DateTimeField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True'})
        },
        u'pinna.pinnasession': {
            'Meta': {'object_name': 'PinnaSession'},
            'created_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'expired_time': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2014, 12, 18, 0, 0)'}),
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
            'display_photo': ('django.db.models.fields.CharField', [], {'max_length': '2083', 'null': 'True'}),
            'followers': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'followers'", 'null': 'True', 'to': u"orm['auth.User']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mylibrary': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': u"orm['pinna.Library']"}),
            'mystations': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'subscribers'", 'null': 'True', 'through': u"orm['pinna.StationSubscriber']", 'to': u"orm['pinna.Station']"}),
            'photo_s3_name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['auth.User']", 'unique': 'True'})
        },
        u'pinna.station': {
            'Meta': {'unique_together': "(('user', 'name'),)", 'object_name': 'Station'},
            'bpm': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'genre': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'station_genres'", 'null': 'True', 'to': u"orm['pinna.MusicMeta']"}),
            'hashtags': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['pinna.Hashtag']", 'null': 'True', 'symmetrical': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mood': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'station_moods'", 'null': 'True', 'to': u"orm['pinna.MusicMeta']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'photo': ('django.db.models.fields.CharField', [], {'max_length': '2083', 'null': 'True'}),
            'photo_s3_name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True'}),
            'privacy_level': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'thumbnail': ('django.db.models.fields.CharField', [], {'max_length': '2083', 'null': 'True'}),
            'thumbnail_s3_name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True'}),
            'tracks': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['pinna.Track']", 'symmetrical': 'False'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'pinna.stationsubscriber': {
            'Meta': {'unique_together': "(('profile', 'station'),)", 'object_name': 'StationSubscriber'},
            'date_subscribed': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'profile': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['pinna.Profile']"}),
            'station': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['pinna.Station']"})
        },
        u'pinna.track': {
            'Meta': {'unique_together': "(('user', 'name'),)", 'object_name': 'Track'},
            'artist': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True'}),
            'author': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True'}),
            'bpm': ('django.db.models.fields.IntegerField', [], {}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'download_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'duration': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'genre': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'genre_tracks'", 'to': u"orm['pinna.MusicMeta']"}),
            'hashtags': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['pinna.Hashtag']", 'null': 'True', 'symmetrical': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'likes': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'liked_tracks'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'mood': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'mood_tracks'", 'to': u"orm['pinna.MusicMeta']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'price': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'privacy_level': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'purchases': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'purchased_tracks'", 'null': 'True', 'to': u"orm['auth.User']"}),
            's3_name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'mytracks'", 'to': u"orm['auth.User']"})
        }
    }

    complete_apps = ['pinna']