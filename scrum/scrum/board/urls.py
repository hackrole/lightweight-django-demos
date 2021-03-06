#!/usr/bin/env python
# encoding: utf-8

from rest_framework.routers import DefaultRouter

from . import views


router = DefaultRouter(False)
router.register(r'sprints', views.SprintViewSet)
router.register(r'tasks', views.TaskViewSet)
router.register(r'users', views.UserViewSet)
