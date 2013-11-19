#coding=utf-8
import os, time, subprocess, json
os.environ['DJANGO_SETTINGS_MODULE'] = 'jaylab.settings'
from django.conf import settings
from jaylab.hcrab.models import *

command = '%s -i -c -R 3 --write-info-json --write-srt -o %s -f %s %s'

to_download = DownloadRecord.objects.filter(status='queue').\
                  order_by('created_at')[:settings.N_PER_MINUTE]

print len(to_download)
for r in to_download:
    print 'process download record: %i .' % r.id
    tried_times = 0
    vfile = r.vfile
    if not vfile.is_downloaded():
        r.status = 'downloading'
        r.save()
        print 'has not download. start to download.'
        if vfile.quality == 'h':
            format = '22'
        else:
            format = '18'
        cmd = command % (settings.YOUTUBE_DL_PATH, vfile.get_file_path(), format, vfile.watch_url)
        print cmd
        subprocess.call(cmd, shell=True)
        print 'finish 1st youtube-dl process'
        if not vfile.is_downloaded() and format == '22':
            print 'try to download in low qulity'
            format2 = '18'
            cmd = command % (settings.YOUTUBE_DL_PATH, vfile.get_file_path(), format2, vfile.watch_url)
            subprocess.call(cmd, shell=True)
            print 'finish 2nd youtube-dl process'
        tried_times += 1

        if not vfile.is_downloaded():
            is_success = False
            while tried_times < settings.MAX_DOWNLOAD_TIMES:
                subprocess.call(cmd, shell=True)
                tried_times += 1
                if vfile.is_downloaded():
                    is_success = True
                    break
                time.sleep(0.5)

            if not is_success:
                r.status = 'download_failed'
                r.save()
                print 'downloaded failed.'
                continue

        print 'downloaded.'
        vfile.has_subtitle = os.path.exists(vfile.get_srt_file_path())
        json_file_path = os.path.join(settings.SERVER_VIDEO_DIR,
                                      '%s.info.json' % vfile.get_filename())
        info = json.load(open(json_file_path))
        vfile.title = info.get('title')
        vfile.desp = info.get('description')
        vfile.download_url = info.get('url')
        duration = info.get('duration')
        if duration:
            vfile.duration = int(duration)
        vfile.length = os.path.getsize(vfile.get_file_path())
        vfile.save()
    else:
        print 'downloaded before.'
    dropbox_user = r.dropbox_user
    if dropbox_user:
        print 'pushing dropbox.'
        r.status = 'dropbox_pushing'
        r.save()
        c = dropbox_user.get_client()
        title = vfile.title
        #https://www.dropbox.com/help/145/en
        incompatible_characters = ['/', '\\', '<', '>', ':', '"', '|', '?', '*']
        for char in incompatible_characters:
            title = title.replace(char, '')
        #print title
        resp = c.put_file('/%s.%s' % (title, vfile.ext), open(vfile.get_file_path()))
        if vfile.has_subtitle:
           resp = c.put_file('/%s.srt' % title, open(vfile.get_srt_file_path()))
        #需要错误处理
        #...
    print 'finished'
    r.status = 'finished'
    r.save()

    time.sleep(0.1)
