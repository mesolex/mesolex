from django.conf.urls import include, url
from rest_framework import routers

from . import api_views

router = routers.DefaultRouter()
router.register(r'lexicalentries', api_views.LexicalEntryViewSet)


urlpatterns = [
    url(r'', include(router.urls)),
    url(
        r'api-auth/',
        include('rest_framework.urls', namespace='rest_framework')
    ),
]
