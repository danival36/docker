# -*- coding: UTF-8 -*-

from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    url(r'^', include('Recommender.urls', namespace="Recommender")),
    url(r'^admin/', include(admin.site.urls)),
]