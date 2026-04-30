from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views

urlpatterns = [
    # Auth
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Users
    path('users/me/', views.CurrentUserView.as_view(), name='api_me'),

    # Projects
    path('projects/', views.ProjectListCreateView.as_view(), name='api_projects'),
    path('projects/<int:pk>/', views.ProjectDetailView.as_view(), name='api_project_detail'),

    # Tasks
    path('tasks/', views.TaskListCreateView.as_view(), name='api_tasks'),
    path('tasks/<int:pk>/', views.TaskDetailView.as_view(), name='api_task_detail'),
    path('tasks/<int:pk>/status/', views.TaskStatusUpdateView.as_view(), name='api_task_status'),
]
