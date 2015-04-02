#!/usr/bin/env python
# encoding: utf-8

from rest_framework import serializers
from rest_framework.reverse import reverse
from django.contrib.auth import get_user_model

from .models import Sprint, Task


User = get_user_model()


class SprintSerializer(serializers.ModelSerializer):

    links = serializers.SerializerMethodField(label=u"链接")

    class Meta:
        model = Sprint
        fields = ('id', 'name', 'description', 'end', 'links',)

    def get_links(self, obj):
        request = self.context['request']
        return {
            'self': reverse('sprint-detail',
                            kwargs={'pk': obj.pk},
                            request=request),
        }


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

        links = {
            'self': reverse('task-detail',
                            kwargs={'pk': obj.pk},
                            request=request),
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
