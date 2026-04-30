from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views import View
from django.http import JsonResponse

from .models import Task, Comment
from .forms import TaskForm, CommentForm, TaskStatusForm
from apps.projects.models import Project, ProjectMembership
from apps.accounts.mixins import AdminRequiredMixin


def _get_project_or_403(request, project_id):
    """Return project if user is a member or admin, else None."""
    project = get_object_or_404(Project, pk=project_id)
    is_admin = hasattr(request.user, 'profile') and request.user.profile.role == 'admin'
    is_member = ProjectMembership.objects.filter(project=project, user=request.user).exists()
    if not is_admin and not is_member and not request.user.is_superuser:
        return None, project
    return project, None


class TaskCreateView(LoginRequiredMixin, View):
    template_name = 'tasks/task_form.html'

    def get(self, request, project_id):
        project, _ = _get_project_or_403(request, project_id)
        if not project:
            messages.error(request, 'You are not a member of this project.')
            return redirect('projects:list')
        form = TaskForm(project=project)
        return render(request, self.template_name, {'form': form, 'project': project, 'title': 'Create Task'})

    def post(self, request, project_id):
        project, _ = _get_project_or_403(request, project_id)
        if not project:
            messages.error(request, 'You are not a member of this project.')
            return redirect('projects:list')
        form = TaskForm(project=project, data=request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.project = project
            task.created_by = request.user
            task.save()
            messages.success(request, f'Task "{task.title}" created.')
            return redirect('projects:detail', pk=project.pk)
        return render(request, self.template_name, {'form': form, 'project': project, 'title': 'Create Task'})


class TaskDetailView(LoginRequiredMixin, View):
    template_name = 'tasks/task_detail.html'

    def get(self, request, task_id):
        task = get_object_or_404(Task, pk=task_id)
        project = task.project
        is_admin = hasattr(request.user, 'profile') and request.user.profile.role == 'admin'
        is_member = ProjectMembership.objects.filter(project=project, user=request.user).exists()
        if not is_admin and not is_member and not request.user.is_superuser:
            messages.error(request, 'Access denied.')
            return redirect('projects:list')
        comments = task.comments.select_related('author').all()
        comment_form = CommentForm()
        status_form = TaskStatusForm(instance=task)
        context = {
            'task': task,
            'comments': comments,
            'comment_form': comment_form,
            'status_form': status_form,
        }
        return render(request, self.template_name, context)

    def post(self, request, task_id):
        task = get_object_or_404(Task, pk=task_id)
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.task = task
            comment.author = request.user
            comment.save()
            messages.success(request, 'Comment added.')
        return redirect('tasks:detail', task_id=task.pk)


class TaskUpdateView(LoginRequiredMixin, View):
    template_name = 'tasks/task_form.html'

    def get(self, request, task_id):
        task = get_object_or_404(Task, pk=task_id)
        project = task.project
        is_admin = hasattr(request.user, 'profile') and request.user.profile.role == 'admin'
        is_assignee = task.assigned_to == request.user
        if not is_admin and not is_assignee and not request.user.is_superuser:
            messages.error(request, 'You can only edit tasks assigned to you.')
            return redirect('tasks:detail', task_id=task.pk)
        form = TaskForm(project=project, instance=task)
        return render(request, self.template_name, {'form': form, 'project': project, 'task': task, 'title': 'Edit Task'})

    def post(self, request, task_id):
        task = get_object_or_404(Task, pk=task_id)
        project = task.project
        is_admin = hasattr(request.user, 'profile') and request.user.profile.role == 'admin'
        is_assignee = task.assigned_to == request.user
        if not is_admin and not is_assignee and not request.user.is_superuser:
            messages.error(request, 'Permission denied.')
            return redirect('tasks:detail', task_id=task.pk)
        form = TaskForm(project=project, data=request.POST, instance=task)
        if form.is_valid():
            form.save()
            messages.success(request, 'Task updated successfully.')
            return redirect('tasks:detail', task_id=task.pk)
        return render(request, self.template_name, {'form': form, 'project': project, 'task': task, 'title': 'Edit Task'})


class TaskDeleteView(LoginRequiredMixin, View):
    template_name = 'tasks/task_confirm_delete.html'

    def get(self, request, task_id):
        task = get_object_or_404(Task, pk=task_id)
        is_admin = hasattr(request.user, 'profile') and request.user.profile.role == 'admin'
        if not is_admin and not request.user.is_superuser:
            messages.error(request, 'Only admins can delete tasks.')
            return redirect('tasks:detail', task_id=task.pk)
        return render(request, self.template_name, {'task': task})

    def post(self, request, task_id):
        task = get_object_or_404(Task, pk=task_id)
        is_admin = hasattr(request.user, 'profile') and request.user.profile.role == 'admin'
        if not is_admin and not request.user.is_superuser:
            messages.error(request, 'Only admins can delete tasks.')
            return redirect('tasks:detail', task_id=task.pk)
        project_pk = task.project.pk
        task.delete()
        messages.success(request, 'Task deleted.')
        return redirect('projects:detail', pk=project_pk)


class UpdateTaskStatusView(LoginRequiredMixin, View):
    def post(self, request, task_id):
        task = get_object_or_404(Task, pk=task_id)
        is_admin = hasattr(request.user, 'profile') and request.user.profile.role == 'admin'
        is_assignee = task.assigned_to == request.user
        if not is_admin and not is_assignee and not request.user.is_superuser:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'error': 'Permission denied'}, status=403)
            messages.error(request, 'Permission denied.')
            return redirect('tasks:detail', task_id=task.pk)

        new_status = request.POST.get('status')
        valid_statuses = [s[0] for s in Task.STATUS_CHOICES]
        if new_status in valid_statuses:
            task.status = new_status
            task.save()
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'status': task.status, 'status_display': task.get_status_display()})
            messages.success(request, f'Task status updated to {task.get_status_display()}.')
        return redirect('tasks:detail', task_id=task.pk)
