from django.conf.urls.defaults import *

urlpatterns = patterns('names.views',
    (r'^(?P<domain>[^/]+)/$', 'name', {'path': None}),
    (r'^(?P<domain>[^/]+)/(?P<path>.+)$', 'name'),
)
