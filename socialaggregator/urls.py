"""Urls for emencia-django-socialaggregator"""
from django.conf.urls import url

from .views import ResourceListView
from .views import ResourceByFeedListView

urlpatterns = [
    url(r'^feed/(?P<slug>[-\w]+)/$', ResourceByFeedListView.as_view(),
        name='socialaggregator_resource_by_feed_list_view'),
    url(r'^$', ResourceListView.as_view(),
        name='socialaggregator_resource_list_view'),
]
