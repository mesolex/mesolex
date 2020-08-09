from django.conf.urls import url

from narratives import views

urlpatterns = [
    url('', views.narratives_search_view, name='narratives_search'),
]
