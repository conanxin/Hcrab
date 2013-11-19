#coding=utf-8
from django.conf.urls import patterns, url
import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^add/$', views.add, name='add'),
    url(r'^guestbook/$', views.gusetbook, name='guest'),
    url(r'^dropbox/signin/$', views.dropbox_sign, name='dropbox_signin'),
    url(r'^dropbox/authorized/$', views.dropbox_authrized, name='dropbox_authorized'),
)

