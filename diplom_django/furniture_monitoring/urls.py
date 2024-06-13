from django.urls import path
from . import views


urlpatterns = [
    path("", views.index, name="index"),
    path('floor/<str:floor>/', views.floor_detail, name='floor_detail'),
    path('add_event', views.CreateEvent.as_view(),name='add_event'),
    path('cameras/<int:cam_id>/', views.CameraGraphView.as_view(), name='camera-graph-view'),
]
