# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'DownloadRecord.dropbox_user'
        db.add_column(u'hcrab_downloadrecord', 'dropbox_user',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['hcrab.DropboxUser'], null=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'DownloadRecord.dropbox_user'
        db.delete_column(u'hcrab_downloadrecord', 'dropbox_user_id')


    models = {
        u'hcrab.downloadrecord': {
            'Meta': {'object_name': 'DownloadRecord'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'dropbox_user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['hcrab.DropboxUser']", 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'session_id': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '50', 'blank': 'True'}),
            'vfile': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['hcrab.VideoFile']"})
        },
        u'hcrab.dropboxuser': {
            'Meta': {'object_name': 'DropboxUser'},
            'country': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '50', 'blank': 'True'}),
            'email': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '400', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_valid': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '400', 'blank': 'True'}),
            'quota_info': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '400', 'blank': 'True'}),
            'referral_link': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '400', 'blank': 'True'}),
            'uid': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'hcrab.videofile': {
            'Meta': {'object_name': 'VideoFile'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'desp': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'download_url': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '500', 'blank': 'True'}),
            'duration': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'ext': ('django.db.models.fields.CharField', [], {'default': "'mp4'", 'max_length': '50'}),
            'has_subtitle': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'length': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'md5': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'}),
            'quality': ('django.db.models.fields.CharField', [], {'default': "u'm'", 'max_length': '20'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'queue'", 'max_length': '50'}),
            'title': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '400', 'blank': 'True'}),
            'watch_url': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'website': ('django.db.models.fields.CharField', [], {'default': "u'youtube'", 'max_length': '20'})
        }
    }

    complete_apps = ['hcrab']