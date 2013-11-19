#coding=utf-8
from django.contrib import admin
from models import *


class VideoFileAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'title', 'get_length_display', 'quality')


class DownloadRecordAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'vfile', 'session_id', 'get_status_display')
    #list_filter = ('session_id',)

class DropboxUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'country')

admin.site.register(VideoFile, VideoFileAdmin)
admin.site.register(DownloadRecord, DownloadRecordAdmin)
admin.site.register(DropboxUser, DropboxUserAdmin)
