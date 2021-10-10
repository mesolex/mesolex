from django.urls import path
from query_api import views

urlpatterns = [
    path('search/', views.search),
]