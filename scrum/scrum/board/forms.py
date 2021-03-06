#!/usr/bin/env python
# encoding: utf-8

from __future__ import unicode_literals

import django_filters
from django.contrib.auth import get_user_model

from .models import Task, Sprint


User = get_user_model()


class NullFilter(django_filters.BooleanFilter):
    """ filter on a field set as null or not """

    def filter(self, qs, value):
        if value is not None:
            return qs.filter(**{'%s__isnull' % self.name: value})

        return qs


class TaskFilter(django_filters.FilterSet):

    backlog = NullFilter(name='sprint')

    class Meta:
        model = Task
        fields = ('sprint', 'status', 'assigned', 'backlog',)

    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self.filter['assign'].extra.update(
            {'to_field_name': User.USERNAME_FIELD})


class SprintFilter(django_filters.FilterSet):

    end_min = django_filters.DateFilter(name="end", lookup_type='gte')
    end_max = django_filters.DateFilter(name="end", lookup_type='lte')

    class Meta:
        model = Sprint
        fields = ('end_min', 'end_max')
