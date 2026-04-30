from django.urls import path
from . import views

app_name = 'tasks'

urlpatterns = [
    path('<int:project_id>/create/', views.TaskCreateView.as_view(), name='create'),
    path('<int:task_id>/', views.TaskDetailView.as_view(), name='detail'),
    path('<int:task_id>/edit/', views.TaskUpdateView.as_view(), name='update'),
    path('<int:task_id>/delete/', views.TaskDeleteView.as_view(), name='delete'),
    path('<int:task_id>/status/', views.UpdateTaskStatusView.as_view(), name='status'),
]
