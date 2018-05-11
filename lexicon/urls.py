from django.conf.urls import url

from lexicon import views


urlpatterns = [
    url('', views.LexiconSearchView.as_view(), name='lexicon_search'),
]
