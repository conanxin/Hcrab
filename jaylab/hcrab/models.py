#coding=utf-8
import os
from django.conf import settings
from django.db import models

status_choices = (
    ('queue', u'排队中'),
    ('downloading', u'下载中'),
    ('dropbox_pushing', u'推送dropbox'),
    ('finished', u'完成'),
    ('download_failed', u'下载失败'),
    ('push_failed', u'推送失败'),

)
quality_choices = (
    ('l', u'低'),
    ('m', u'中'),
    ('h', u'高'),
)


class DropboxUser(models.Model):
    class Meta:
        verbose_name = u'Dropbox用户'
        verbose_name_plural = verbose_name

    uid = models.CharField(max_length=50, unique=True)
    email = models.CharField(max_length=400, blank=True, default='')
    country = models.CharField(max_length=50, blank=True, default='')
    name = models.CharField(max_length=400, blank=True, default='')
    quota_info = models.CharField(max_length=400, blank=True, default='')
    referral_link = models.CharField(max_length=400, blank=True, default='')

    access_key = models.CharField(max_length=50, blank=True, default='')
    access_secret = models.CharField(max_length=50, blank=True, default='')

    is_valid = models.BooleanField(default='True')

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __unicode__(self):
        if not self.name:
            return 'dropbox user %i' % self.id
        return self.name

    def get_client(self):
        from dropbox import client, rest, session
        sess = session.DropboxSession(settings.DROPBOX_APP_KEY,
                                      settings.DROPBOX_APP_SECRET,
                                      settings.DROPBOX_ACCESS_TYPE)
        sess.set_token(self.access_key, self.access_secret)
        client = client.DropboxClient(sess)
        return client


class VideoFile(models.Model):
    class Meta:
        verbose_name = u'视频文件'
        verbose_name_plural = verbose_name

    title = models.CharField(max_length=400, blank=True, default='')

    watch_url = models.CharField(max_length=500)
    md5 = models.CharField(max_length=50, unique=True)
    download_url = models.CharField(max_length=500, blank=True, default='')
    duration = models.IntegerField(blank=True, null=True)
    length = models.IntegerField(blank=True, null=True, verbose_name=u'文件大小(byte)')
    desp = models.TextField(blank=True, default='')
    ext = models.CharField(max_length=50, default='mp4')
    quality = models.CharField(max_length=20, default=u'm', choices=quality_choices)
    has_subtitle = models.BooleanField(default=False)
    website = models.CharField(max_length=20, default=u'youtube')

    latest_ref = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.title

    def get_filename(self):
        return self.md5 + '.' + self.ext

    def get_srt_filename(self):
        '''字幕文件的名字'''
        return self.md5 + '.en.srt'

    def get_length_display(self):
        if self.length:
            return '%i MB' % (self.length/1024.0/1024.0)
        return ''

    def get_file_path(self):
        return os.path.join(settings.SERVER_VIDEO_DIR, self.get_filename())

    def get_srt_file_path(self):
        return os.path.join(settings.SERVER_VIDEO_DIR, self.get_srt_filename())

    def is_downloaded(self):
        return os.path.exists(self.get_file_path())


class DownloadRecord(models.Model):
    class Meta:
        verbose_name = u'下载记录'
        verbose_name_plural = verbose_name

    session_id = models.CharField(max_length=50, blank=True, default='')
    dropbox_user = models.ForeignKey(DropboxUser, null=True)
    status = models.CharField(max_length=50, choices=status_choices, default='queue')
    vfile = models.ForeignKey(VideoFile)
    submit_url = models.CharField(max_length=400, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    def get_download_url(self):
        if self.vfile.is_downloaded():
            return settings.HOST + settings.VIDEO_URL + '/' + self.vfile.get_filename()
        return None

    def get_srt_url(self):
        if self.vfile.has_subtitle:
            return settings.HOST + settings.VIDEO_URL + '/' + self.vfile.get_srt_filename()
        return ''

    def __unicode__(self):
        return 'Download_record_%i' % self.id


