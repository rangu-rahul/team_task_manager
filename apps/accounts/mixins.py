from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin


def role_required(role):
    """Decorator that restricts a view to users with a specific role."""
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('accounts:login')
            try:
                user_role = request.user.profile.role
            except Exception:
                user_role = None
            if user_role != role and not request.user.is_superuser:
                messages.error(request, 'You do not have permission to access this page.')
                return redirect('dashboard:index')
            return view_func(request, *args, **kwargs)
        return _wrapped
    return decorator


class AdminRequiredMixin(LoginRequiredMixin):
    """Mixin that restricts class-based views to admin users."""

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        try:
            role = request.user.profile.role
        except Exception:
            role = None
        if role != 'admin' and not request.user.is_superuser:
            messages.error(request, 'Admin access required.')
            return redirect('dashboard:index')
        return super().dispatch(request, *args, **kwargs)


class ProjectMemberMixin(LoginRequiredMixin):
    """Mixin ensuring user is a member of the project (resolved from URL kwarg pk)."""

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)

    def get_project_membership(self, project):
        from apps.projects.models import ProjectMembership
        try:
            return ProjectMembership.objects.get(project=project, user=self.request.user)
        except ProjectMembership.DoesNotExist:
            return None
