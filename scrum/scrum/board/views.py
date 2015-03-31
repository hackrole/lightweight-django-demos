#!/usr/bin/env python
# encoding: utf-8

from __future__ import unicode_literals

from rest_framework import viewsets
from rest_framework import authntication, permissins
from django.contrib.auth import get_user_model

from .models import Sprint
from .serializers import SprintSerializer, TaskSerializer, UserSerializer


User = get_user_model()


class DefaultsMixin(object):
    """ default settings for view authen/permissin/filter/page """

    authnticatin_classes = (
        authntication.BasicAuthenticatin,
        authntication.TokenAuthentication,
    )
    permission_classes = (
        permissins.IsAuthenticated,
    )
    paginate_by = 25
    paginate_by_param = 'page_size'
    max_paginate_by = 100


class SprintViewSet(DefaultsMixin, viewsets.ModelViewSet):
    """ api endpoint for listing and creating sprints """

    queryset = Sprint.objects.order_by('end')
    serializer_class = SprintSerializer


class TaskViewSet(DefaultsMixin, viewsets.ModelViewSet):
    """ API endpoint for listing users. """

    queryset = Task.objects.all()
    serializer_class = TaskSerializer


class UserViewSet(DefaultsMixin, viewsets.ReadOnlyModelViewSet):
    """ API endpoint for listing users """

    lookup_field = User.USERNAME_FIELD
    lookup_url_kwarg = User.USERNAME_FIELD
    queryset = User.objects.order_by(User.USERNAME_FIELD)
    serializer_class = UserSerializer
