#!/usr/bin/env python
# encoding: utf-8

import django_filters
from .models import Task


class TaskFilter(django_filters.FilterSet):

    class Meta:
        model = Task
        fields = ('sprint', 'status', 'assigned',)
