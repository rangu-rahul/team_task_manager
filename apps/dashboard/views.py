from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.utils import timezone
from django.db.models import Count, Q

from apps.tasks.models import Task
from apps.projects.models import Project, ProjectMembership


class DashboardView(LoginRequiredMixin, View):
    template_name = 'dashboard/dashboard.html'
    login_url = '/accounts/login/'

    def get(self, request):
        user = request.user
        is_admin = (hasattr(user, 'profile') and user.profile.role == 'admin') or user.is_superuser

        if is_admin:
            all_tasks = Task.objects.all()
            projects = Project.objects.all().prefetch_related('tasks')
        else:
            member_project_ids = ProjectMembership.objects.filter(user=user).values_list('project_id', flat=True)
            all_tasks = Task.objects.filter(
                Q(assigned_to=user) | Q(project_id__in=member_project_ids)
            ).distinct()
            projects = Project.objects.filter(id__in=member_project_ids).prefetch_related('tasks')

        today = timezone.now().date()

        total_tasks = all_tasks.count()
        completed_tasks = all_tasks.filter(status='completed').count()
        in_progress_tasks = all_tasks.filter(status='in_progress').count()
        overdue_tasks = all_tasks.filter(status='overdue').count()
        todo_tasks = all_tasks.filter(status='todo').count()

        # My assigned tasks (paginated manually)
        my_tasks = Task.objects.filter(assigned_to=user).select_related('project').order_by('-updated_at')[:10]

        # Recent activity: latest 10 tasks updated
        recent_tasks = all_tasks.select_related('project', 'assigned_to').order_by('-updated_at')[:10]

        # Overdue task highlights
        overdue_list = all_tasks.filter(status='overdue').select_related('project', 'assigned_to').order_by('due_date')[:5]

        # Project progress
        project_progress = []
        for project in projects:
            project_progress.append({
                'project': project,
                'progress': project.get_progress(),
                'total': project.tasks.count(),
                'completed': project.tasks.filter(status='completed').count(),
            })

        context = {
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks,
            'in_progress_tasks': in_progress_tasks,
            'overdue_tasks': overdue_tasks,
            'todo_tasks': todo_tasks,
            'my_tasks': my_tasks,
            'recent_tasks': recent_tasks,
            'overdue_list': overdue_list,
            'project_progress': project_progress,
            'is_admin': is_admin,
        }
        return render(request, self.template_name, context)
