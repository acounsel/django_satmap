from django.urls import path
from . import views

urlpatterns = [
    path('', views.ProjectList.as_view(), name='project_list'),
    path('project/create/', views.ProjectCreate.as_view(), name='project_create'),
    path('project/<int:pk>/', views.ProjectDetail.as_view(), name='project_detail'),
    path('maps', views.MapList.as_view(), name='map_list'),
    path('map/create/', views.MapCreate.as_view(), name='map_create'),
    path('map/<int:pk>/', views.MapDetail.as_view(), name='map_detail'),
]
