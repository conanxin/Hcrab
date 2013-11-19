#coding=utf-8
import re,uuid, datetime
from hashlib import md5
from django.conf import settings
from django.core.context_processors import csrf
from django.shortcuts import render_to_response, redirect
from django.core.urlresolvers import reverse
from dropbox import client, rest, session

from models import *
from utils import *

youtube_pattern = [r'youtube\.com/watch\?v=[0-9, a-z, A-Z, \-, _]+',
                   r'youtu\.be/[0-9, a-z, A-Z, \-, _]+']


def file2md5(url, quality):
    m = md5()
    m.update(url + quality)
    return m.hexdigest()


def index(request):
    records = []
    dropbox_uid = request.session.get('dropbox_uid', '')
    if dropbox_uid:
        records = DownloadRecord.objects.filter(dropbox_user__uid=dropbox_uid).order_by('-created_at')[:100]
    else:
        sid = request.session.get('session_id', '')
        if sid:
            records = DownloadRecord.objects.filter(session_id=sid).order_by('-created_at')[:100]
        else:
            sid = uuid.uuid1().hex
            request.session['session_id'] = sid
            request.session.set_expiry(settings.EXPIRE_HOURS*3600)

    for r in records:
        if r.vfile.is_downloaded():
            r.title = ' '.join( r.vfile.title.split()[:6]) + '...'
            r.durl = r.get_download_url()
        else:
            r.title = '-'
            r.durl = r.get_status_display()

    params = {}
    params.update(csrf(request))
    params['records'] = records

    params['disk_used_percent'] = disk_usage()[4]

    if dropbox_uid:
        params['is_dropbox_user'] = True
    return render_to_response('hcrab/index.html', params)


def add(request):
    back_url = reverse(index)

    dropbox_uid = request.session.get('dropbox_uid', '')
    dropbox_user = None
    if dropbox_uid:
        dropbox_user = DropboxUser.objects.get(uid=dropbox_uid)
    else:
        sid = request.session.get('session_id', '')
        if not sid:
            info = u'请打开浏览器cookie支持。'
            return render_to_response('info.html',
                                      {'info': info,
                                       'interval': 3,
                                       'back_url': back_url})
	    
        n = DownloadRecord.objects.filter(session_id=sid).count()
        if n >= settings.N_PER_USER_EVERYDAY:
            info = u'Sorry, 因为服务器资源有限，每个用户在%i小时内只能下载%i个Youtube视频 :('%(settings.EXPIRE_HOURS, settings.N_PER_USER_EVERYDAY)
            return render_to_response('info.html',
                                      {'info': info,
                                       'interval': 5,
                                       'back_url': back_url})

    if int(disk_usage()[4][:-1]) > 95:
        info = u'Sorry, 服务器硬盘已满，请明天来下载吧 :('
        return render_to_response('info.html',
                                  {'info': info,
                                   'interval': 5,
                                   'back_url': back_url})

    url = request.POST.get('url', '')
    origin_url = url
    if not url:
        info = u'请填写视频链接。'
        return render_to_response('info.html',
                                  {'info': info,
                                   'interval': 3,
                                   'back_url': back_url})
    for p in youtube_pattern:
        r = re.search(p, url)
        if r:
            break
    if r:        
        url = r.group()
    else:
        r = re.search('v=([0-9, a-z, A-Z, \-, _]+)', url)
        if url.find('youtube.com') != -1 and r:
            url = "youtube.com/watch?" + r.group()
            print url
        else:
            info ='视频地址不正确.'
            return render_to_response('info.html',
                                  { 'info': info,
                                    'interval': 3,
                                    'back_url':back_url,
                                    })

    is_hd = request.POST.get('is_hd')
    if is_hd:
        quality = 'h'
    else:
        quality = 'm'

    m5 = file2md5(url, quality)
    y, is_created = VideoFile.objects.get_or_create(md5=m5, watch_url=url, quality=quality)
    y.latest_ref = datetime.datetime.now()
    y.save()

    if dropbox_user:
        dr, is_created = DownloadRecord.objects.get_or_create(dropbox_user=dropbox_user, vfile=y)
        dr.status = 'queue'
        dr.submit_url = origin_url
        dr.save()
    else:
        dr, is_created = DownloadRecord.objects.get_or_create(session_id=sid, vfile=y)
        dr.status = 'queue'
        dr.submit_url = origin_url
        dr.save()
    return redirect(back_url)


def dropbox_sign(request):
    sess = session.DropboxSession(settings.DROPBOX_APP_KEY, settings.DROPBOX_APP_SECRET,
                                  settings.DROPBOX_ACCESS_TYPE)
    request_token = sess.obtain_request_token()
    url = sess.build_authorize_url(request_token,
                                   oauth_callback=settings.DROPBOX_AUTHRIZED_CALLBACK_URL)
    print url
    request.session['request_key'] = request_token.key
    request.session['request_secret'] = request_token.secret
    return redirect(url)


def dropbox_authrized(request):
    back_url = reverse(index)

    uid = request.GET.get('uid', '')
    oauth_token = request.GET.get('oauth_token', '')
    if not uid and not oauth_token:
        info = u'Dropbox 认证出问题了 :( 麻烦再一遍。'
        return render_to_response('info.html',
                                  {'info': info,
                                   'interval': 3,
                                   'back_url': back_url})

    request_key = request.session.get('request_key')
    request_secret = request.session.get('request_secret')
    if not request_key and not request_secret:
        info = u'请打开浏览器cookie支持。'
        return render_to_response('info.html',
                                  {'info': info,
                                   'interval': 3,
                                   'back_url': back_url})

    request_token = session.OAuthToken(request_key, request_secret)
    sess = session.DropboxSession(settings.DROPBOX_APP_KEY, settings.DROPBOX_APP_SECRET,
                                  settings.DROPBOX_ACCESS_TYPE)
    access_token = sess.obtain_access_token(request_token)

    user, is_created = DropboxUser.objects.get_or_create(uid=uid)
    user.access_key = access_token.key
    user.access_secret = access_token.secret
    #client = client = client.DropboxClient(sess)
    #info = client.account_info()
    user.save()

    request.session['dropbox_uid'] = uid

    info = 'Ok, Dropbox 认证成功 :)'
    return render_to_response('info.html',
                              {'info': info,
                               'interval': 3,
                               'back_url': back_url})


def gusetbook(request):
    return render_to_response('hcrab/guestbook.html')
