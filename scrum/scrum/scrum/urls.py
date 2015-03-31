#!/usr/bin/env python
# encoding: utf-8

from __future__ import unicode_literals

from django.conf.urls import url, include
from rest_framework.authtoken.views import obtain_auth_token

from board.urls import router


urlpatterns = [
    url(r'^api/token/', obtain_auth_token, name='api-token'),
    url(r'^api/', include(router.url)),
]
