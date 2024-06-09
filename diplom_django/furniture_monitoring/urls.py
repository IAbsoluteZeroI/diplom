from django.urls import path
from . import views


urlpatterns = [
    path("", views.index, name="index"),
    path('floor/<str:floor>/', views.floor_detail, name='floor_detail'),
]
