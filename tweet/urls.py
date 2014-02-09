from django.conf.urls import patterns, url

from tweet import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
)
