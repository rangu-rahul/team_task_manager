from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend

from apps.projects.models import Project, ProjectMembership
from apps.tasks.models import Task
from .serializers import (
    ProjectSerializer, TaskSerializer, TaskStatusSerializer, UserSerializer
)
from .filters import TaskFilter, ProjectFilter


class IsAdminRole(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return (
            request.user.is_superuser or
            (hasattr(request.user, 'profile') and request.user.profile.role == 'admin')
        )


class CurrentUserView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)


class ProjectListCreateView(generics.ListCreateAPIView):
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminRole]
    filter_backends = [DjangoFilterBackend]
    filterset_class = ProjectFilter

    def get_queryset(self):
        user = self.request.user
        is_admin = (hasattr(user, 'profile') and user.profile.role == 'admin') or user.is_superuser
        if is_admin:
            return Project.objects.all().prefetch_related('memberships', 'tasks')
        member_ids = ProjectMembership.objects.filter(user=user).values_list('project_id', flat=True)
        return Project.objects.filter(id__in=member_ids).prefetch_related('memberships', 'tasks')

    def perform_create(self, serializer):
        project = serializer.save(created_by=self.request.user)
        ProjectMembership.objects.create(project=project, user=self.request.user, role='admin')


class ProjectDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminRole]

    def get_queryset(self):
        user = self.request.user
        is_admin = (hasattr(user, 'profile') and user.profile.role == 'admin') or user.is_superuser
        if is_admin:
            return Project.objects.all()
        member_ids = ProjectMembership.objects.filter(user=user).values_list('project_id', flat=True)
        return Project.objects.filter(id__in=member_ids)


class TaskListCreateView(generics.ListCreateAPIView):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = TaskFilter

    def get_queryset(self):
        user = self.request.user
        is_admin = (hasattr(user, 'profile') and user.profile.role == 'admin') or user.is_superuser
        if is_admin:
            return Task.objects.all().select_related('project', 'assigned_to', 'created_by')
        member_ids = ProjectMembership.objects.filter(user=user).values_list('project_id', flat=True)
        return Task.objects.filter(project_id__in=member_ids).select_related('project', 'assigned_to', 'created_by')

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class TaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        is_admin = (hasattr(user, 'profile') and user.profile.role == 'admin') or user.is_superuser
        if is_admin:
            return Task.objects.all()
        member_ids = ProjectMembership.objects.filter(user=user).values_list('project_id', flat=True)
        return Task.objects.filter(project_id__in=member_ids)

    def destroy(self, request, *args, **kwargs):
        is_admin = (hasattr(request.user, 'profile') and request.user.profile.role == 'admin') or request.user.is_superuser
        if not is_admin:
            return Response({'detail': 'Only admins can delete tasks.'}, status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)


class TaskStatusUpdateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, pk):
        task = get_object_or_404(Task, pk=pk)
        is_admin = (hasattr(request.user, 'profile') and request.user.profile.role == 'admin') or request.user.is_superuser
        is_assignee = task.assigned_to == request.user
        if not is_admin and not is_assignee:
            return Response({'detail': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)
        serializer = TaskStatusSerializer(task, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
