from django.conf.urls import include, url
from rest_framework import routers

from . import api_views

ROUTER = routers.DefaultRouter()
ROUTER.register(r'lexicalentries', api_views.LexicalEntryViewSet)


urlpatterns = [
    url(r'', include(ROUTER.urls)),
    url(
        r'api-auth/',
        include('rest_framework.urls', namespace='rest_framework')
    ),
]
