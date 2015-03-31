from django.conf.urls import url
from .view import page


urlpatterns = (
    url(r'^(?P<slug>[\w./-]+)/$', page, name='pge'),
    url(r'^$', page, name='homepge'),
)
