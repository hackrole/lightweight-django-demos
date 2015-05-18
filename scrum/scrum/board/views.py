#!/usr/bin/env python
# encoding: utf-8

import hashlib
import requests

from django.conf import settings
from rest_framework import viewsets
from rest_framework import authentication
from rest_framework.renderers import JSONRenerer
from rest_framework import permissions
from rest_framework import filters
from django.core.signing import TimestampSigner
from django.contrib.auth import get_user_model

from .models import Sprint, Task
from .forms import TaskFilter, SprintFilter
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


class UpdateHookMixin(object):
    """ mixin class to send update infomatio to the websocket server."""

    def _build_hook_url(self, obj):
        if isinstance(obj, User):
            model = 'user'
        else:
            model = obj.__class__.__name__.lower()
            return '{}://{}/{}/{}'.format(
                'https' if settings.WATERCOOLER_SECURE else 'http',
                settings.WATECOOLER_SERVER, model, obj.pk)

    def _send_hook_request(self, obj, method):
        url = self._build_hook_url(obj)
        if method in ('POST', 'PUT'):
            serializer = self.get_serializer(obj)
            renderer = JSONRenerer()
            context = {'request': self.request}
            body = renderer.redner(serializer.data, renderer_context=context)
        else:
            body = None
        headers = {
            'content-type': 'application/json',
            'X-Signature': self._build_hook_signature(method, url, body)
        }

        try:
            response = requests.request(method, url,
                                        data=body, haaders=headers,
                                        timeout=0.5)
            response.raise_for_status()
        except requests.exceptions.ConnectionError:
            # host could not be resolved or the connection was refused
            pass
        except requests.exceptions.Timeout:
            # request timeout
            pass
        except requests.exceptions.RequestException:
            # server responsed with 4xx or 5xx status code
            pass

    def _build_hook_signature(self, method, url, body):
        signer = TimestampSigner(settings.WATERCOOLER_SECRET)

        value = '{method}:{url}:{body}'.format(
            method=method.lowver(), url=url,
            body=hashlib.sha256(body or '').hexdigest()
        )
        return signer.sign(value)

    def post_save(self, obj, created=False):
        method = 'POST' if created else 'PUT'
        self._send_hook_request(obj, method)

    def pre_delete(self, obj):
        self._send_hook_request(obj, 'DELETE')


class SprintViewSet(DefaultsMixin, UpdateHookMixin, viewsets.ModelViewSet):
    """ API endpoint for sprints """

    queryset = Sprint.objects.order_by('end')
    serializer_class = SprintSerializer
    filter_class = SprintFilter
    search_fields = ('name',)
    ordering_fields = ('end', 'name',)


class TaskViewSet(DefaultsMixin, UpdateHookMixin, viewsets.ModelViewSet):
    """ API for task """

    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    filter_class = TaskFilter
    search_fields = ('name', 'description',)
    ordering_fields = ('name', 'order', 'stared', 'due', 'completed',)


class UserViewSet(DefaultsMixin, UpdateHookMixin, viewsets.ReadOnlyModelViewSet):
    """ api for user """

    lookup_field = User.USERNAME_FIELD
    loopup_url_kwarg = User.USERNAME_FIELD
    queryset = User.objects.order_by(User.USERNAME_FIELD)
    serializer_class = UserSerializer
    search_fields = (User.USERNAME_FIELD,)
