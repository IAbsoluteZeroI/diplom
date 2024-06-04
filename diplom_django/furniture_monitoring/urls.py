from django.urls import path
from . import views


urlpatterns = [
    path("", views.index, name="index"),
    path('floor/<str:floor>/', views.floor_detail, name='floor_detail'),
    path("db_tables/", views.db_tables_view, name="db_tables"),
    path("db_tables/<str:table_name>/", views.table_view, name="table"),
    path("track_cameras/", views.track_cameras_view, name="track_cameras"),
]
