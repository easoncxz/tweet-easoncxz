from django.conf.urls import patterns, url
from tweet import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^auth/$', views.auth, name='auth'),
    url(r'^callback/$', views.callback, name='callback'),
    #url(r'^home/$', views.home, name='home'),
)
