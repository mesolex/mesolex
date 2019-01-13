from django.conf.urls import url

from lexicon import views


urlpatterns = [
    url('', views.lexicon_search_view, name='lexicon_search'),
]
