#!/usr/bin/env python
# encoding: utf-8

from rest_framework import viewsets
from rest_framework import authentication
from rest_framework import permissions
from rest_framework import filters
from django.contrib.auth import get_user_model

from .models import Sprint, Task
from .forms import TaskFilter
from .serializers import SprintSerializer, TaskSerializer, UserSerializer


User = get_user_model()


class DefaultsMixin(object):
    """ default settings for view auth/permission """

    authentication_classes = (
        authentication.BasicAuthentication,
        authentication.TokenAuthentication,
    )
    permission_classes = (
        permissions.IsAuthenticated,
    )
    paginate_by = 2
    paginated_by_param = 'page_size'
    max_paginate_by = 7
    filter_backends = (
        filters.DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    )


class SprintViewSet(DefaultsMixin, viewsets.ModelViewSet):
    """ API endpoint for sprints """

    queryset = Sprint.objects.order_by('end')
    serializer_class = SprintSerializer
    search_fields = ('name',)
    ordering_fields = ('end', 'name',)


class TaskViewSet(DefaultsMixin, viewsets.ModelViewSet):
    """ API for task """

    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    filter_class = TaskFilter
    search_filters = ('name', 'description',)
    ordering_fields = ('name', 'order', 'stared', 'due', 'completed',)


class UserViewSet(DefaultsMixin, viewsets.ReadOnlyModelViewSet):
    """ api for user """

    lookup_field = User.USERNAME_FIELD
    loopup_url_kwarg = User.USERNAME_FIELD
    queryset = User.objects.order_by(User.USERNAME_FIELD)
    serializer_class = UserSerializer
    search_filters = (User.USERNAME_FIELD,)
