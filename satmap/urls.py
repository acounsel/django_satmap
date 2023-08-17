from django.urls import path
from . import views

urlpatterns = [
    path('', views.ProjectList.as_view(), name='project_list'),
    path('project/create/', views.ProjectCreate.as_view(), name='project_create'),
    path('project/<int:pk>/', views.ProjectDetail.as_view(), name='project_detail'),
    path('project/edit/<int:pk>/', views.ProjectUpdate.as_view(), name='project_edit'),
    path('project/duplicate/<int:pk>/', views.ProjectDuplicate.as_view(), name='project_duplicate'),
    path('project/delete/<int:pk>/', views.ProjectDelete.as_view(), name='project_delete'),
    path('maps', views.MapList.as_view(), name='map_list'),
    path('map/create/', views.MapCreate.as_view(), name='map_create'),
    path('map/<int:pk>/', views.MapDetail.as_view(), name='map_detail'),
    path('map/edit/<int:pk>/', views.MapUpdate.as_view(), name='map_edit'),
    path('map/duplicate/<int:pk>/', views.MapDuplicate.as_view(), name='map_duplicate'),
    path('map/delete/<int:pk>/', views.MapDelete.as_view(), name='map_delete')
]
