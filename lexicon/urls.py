from django.conf.urls import url

from lexicon import views


urlpatterns = [
    url('', views.home, name='home'),
]
