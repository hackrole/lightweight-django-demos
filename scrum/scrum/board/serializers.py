#!/usr/bin/env python
# encoding: utf-8

from datetime import date
from rest_framework import serializers
from rest_framework.reverse import reverse
from django.contrib.auth import get_user_model
from django.conf import settings

from .models import Sprint, Task


User = get_user_model()


class SprintSerializer(serializers.ModelSerializer):

    links = serializers.SerializerMethodField(label=u"链接")

    class Meta:
        model = Sprint
        fields = ('id', 'name', 'description', 'end', 'links',)

    def get_links(self, obj):
        request = self.context['request']
        channel = '{proto}://{server}/{channel}'.format(
            proto='wss' if settings.WATERCOOL_SECURE else 'ws',
            server=settings.WATERCOOL_SERVER,
            channel=obj.pk
        )
        return {
            'self': reverse('sprint-detail',
                            kwargs={'pk': obj.pk},
                            request=request),
            'tasks': reverse('task-list',
                             request=request) + '?Sprint={}'.format(obj.pk),
            'channel': channel,
        }

    def validate_end(self, attrs, source):
        end_date = attrs[source]
        new = not self.object
        changed = self.object and self.object.end != end_date
        if (new or changed) and (end_date < date.today()):
            msg = "End date cannot be in the past."
            raise serializers.ValidationError(msg)
        return attrs


class TaskSerializer(serializers.ModelSerializer):
    status_display = serializers.SerializerMethodField(label=u"可读状态")
    assigned = serializers.SlugRelatedField(
        slug_field=User.USERNAME_FIELD, required=False,
        queryset=User.objects.all()
    )
    links = serializers.SerializerMethodField(label=u"连接")

    class Meta:
        model = Task
        fields = ('id', 'name', 'description', 'sprint', 'links',
                  'status', 'order', 'assigned', 'started',
                  'due', 'completed', 'status_display')

    def get_status_display(self, obj):
        return obj.get_status_display()

    def get_links(self, obj):
        request = self.context['request']
        username = obj.get_username()

        links = {
            'self': reverse('task-detail',
                            kwargs={'pk': obj.pk},
                            request=request),
            'tasks': '{}?assigned={}'.format(
                reverse('task-list', request=request), username),
        }
        if obj.sprint_id:
            links['sprint'] = reverse('sprint-detail',
                                      kwargs={'pk': obj.sprint_id},
                                      request=request)

        if obj.assigned:
            kw = {User.USERNAME_FIELD: obj.assigned}
            links['assigned'] = reverse('user-detail',
                                        kwargs=kw,
                                        request=request)

        return links

    def validate_sprint(self, attrs, source):
        sprint = attrs[source]
        if self.object and self.object.pk:
            if sprint != self.object.sprint:
                if self.object.status == Task.STATUS_DONE:
                    msg = 'cannot change the sprint of a completed task'
                    raise serializers.ValidationError(msg)
                if sprint and sprint.end < date.today():
                    msg = 'cannot assign tasks to past sprints'
                    raise serializers.ValidationError(msg)
        else:
            if sprint and sprint.end < date.today():
                msg = 'cannot add tasks to past sprints'
                raise serializers.ValidationError(msg)

        return attrs

    def validate(self, attrs):
        sprint = attrs.get('sprint')
        status = int(attrs.get('status'))
        started = attrs.get('started')
        completed = attrs.get('completed')

        if not sprint and status != Task.STATUS_TODO:
            msg = 'backlog tasks must have "not started" status.'
            raise serializers.ValidationError(msg)
        if started and status == Task.STATUS_TODO:
            msg = 'started date cannot be set for started tasks.'
            raise serializers.ValidationError(msg)
        if completed and status != Task.STATUS_DONE:
            msg = 'Completed date cannot be set for uncompleted tasks.'
            raise serializers.ValidationError(msg)

        return attrs


class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='get_full_name')
    links = serializers.SerializerMethodField(label=u"链接")

    class Meta:
        model = User
        fields = ('id', User.USERNAME_FIELD, 'full_name', 'links', 'is_active')

    def get_links(self, obj):
        request = self.context['request']
        username = obj.get_username()

        return {
            'self': reverse('user-detail',
                            kwargs={User.USERNAME_FIELD: username},
                            request=request),
        }
