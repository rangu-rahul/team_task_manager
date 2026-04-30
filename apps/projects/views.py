from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib import messages
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy, reverse
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required

from .models import Project, ProjectMembership
from .forms import ProjectForm, AddMemberForm
from apps.accounts.mixins import AdminRequiredMixin
from apps.tasks.models import Task


class ProjectListView(LoginRequiredMixin, View):
    template_name = 'projects/project_list.html'

    def get(self, request):
        if request.user.is_superuser or (hasattr(request.user, 'profile') and request.user.profile.role == 'admin'):
            projects = Project.objects.all().prefetch_related('memberships', 'tasks')
        else:
            memberships = ProjectMembership.objects.filter(user=request.user).values_list('project_id', flat=True)
            projects = Project.objects.filter(id__in=memberships).prefetch_related('memberships', 'tasks')
        return render(request, self.template_name, {'projects': projects})


class ProjectCreateView(AdminRequiredMixin, View):
    template_name = 'projects/project_form.html'

    def get(self, request):
        form = ProjectForm()
        return render(request, self.template_name, {'form': form, 'title': 'Create Project'})

    def post(self, request):
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.created_by = request.user
            project.save()
            # Add creator as admin member
            ProjectMembership.objects.create(project=project, user=request.user, role='admin')
            messages.success(request, f'Project "{project.name}" created successfully.')
            return redirect('projects:detail', pk=project.pk)
        return render(request, self.template_name, {'form': form, 'title': 'Create Project'})


class ProjectDetailView(LoginRequiredMixin, View):
    template_name = 'projects/project_detail.html'

    def get(self, request, pk):
        project = get_object_or_404(Project, pk=pk)
        # Check access
        is_admin_user = hasattr(request.user, 'profile') and request.user.profile.role == 'admin'
        is_member = ProjectMembership.objects.filter(project=project, user=request.user).exists()
        if not is_admin_user and not is_member and not request.user.is_superuser:
            messages.error(request, 'You are not a member of this project.')
            return redirect('projects:list')

        membership = ProjectMembership.objects.filter(project=project, user=request.user).first()
        members = ProjectMembership.objects.filter(project=project).select_related('user')
        tasks = project.tasks.select_related('assigned_to', 'created_by').order_by('status', '-created_at')

        todo_tasks = tasks.filter(status='todo')
        in_progress_tasks = tasks.filter(status='in_progress')
        completed_tasks = tasks.filter(status='completed')
        overdue_tasks = tasks.filter(status='overdue')

        context = {
            'project': project,
            'membership': membership,
            'members': members,
            'todo_tasks': todo_tasks,
            'in_progress_tasks': in_progress_tasks,
            'completed_tasks': completed_tasks,
            'overdue_tasks': overdue_tasks,
            'progress': project.get_progress(),
        }
        return render(request, self.template_name, context)


class ProjectUpdateView(AdminRequiredMixin, View):
    template_name = 'projects/project_form.html'

    def get(self, request, pk):
        project = get_object_or_404(Project, pk=pk)
        form = ProjectForm(instance=project)
        return render(request, self.template_name, {'form': form, 'title': 'Edit Project', 'project': project})

    def post(self, request, pk):
        project = get_object_or_404(Project, pk=pk)
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            messages.success(request, 'Project updated successfully.')
            return redirect('projects:detail', pk=project.pk)
        return render(request, self.template_name, {'form': form, 'title': 'Edit Project', 'project': project})


class ProjectDeleteView(AdminRequiredMixin, View):
    template_name = 'projects/project_confirm_delete.html'

    def get(self, request, pk):
        project = get_object_or_404(Project, pk=pk)
        return render(request, self.template_name, {'project': project})

    def post(self, request, pk):
        project = get_object_or_404(Project, pk=pk)
        name = project.name
        project.delete()
        messages.success(request, f'Project "{name}" deleted successfully.')
        return redirect('projects:list')


class ManageMembersView(AdminRequiredMixin, View):
    template_name = 'projects/manage_members.html'

    def get(self, request, pk):
        project = get_object_or_404(Project, pk=pk)
        members = ProjectMembership.objects.filter(project=project).select_related('user')
        form = AddMemberForm()
        return render(request, self.template_name, {'project': project, 'members': members, 'form': form})

    def post(self, request, pk):
        project = get_object_or_404(Project, pk=pk)
        action = request.POST.get('action')

        if action == 'add':
            form = AddMemberForm(request.POST)
            if form.is_valid():
                email = form.cleaned_data['email']
                role = form.cleaned_data['role']
                user = User.objects.get(email=email)
                membership, created = ProjectMembership.objects.get_or_create(
                    project=project, user=user, defaults={'role': role}
                )
                if created:
                    messages.success(request, f'{user.username} added to project.')
                else:
                    membership.role = role
                    membership.save()
                    messages.info(request, f'{user.username} role updated.')
            else:
                members = ProjectMembership.objects.filter(project=project).select_related('user')
                return render(request, self.template_name, {'project': project, 'members': members, 'form': form})

        elif action == 'remove':
            user_id = request.POST.get('user_id')
            ProjectMembership.objects.filter(project=project, user_id=user_id).delete()
            messages.success(request, 'Member removed from project.')

        return redirect('projects:members', pk=project.pk)
