import django_filters
from apps.tasks.models import Task
from apps.projects.models import Project


class TaskFilter(django_filters.FilterSet):
    project = django_filters.NumberFilter(field_name='project__id')
    status = django_filters.CharFilter(field_name='status')
    priority = django_filters.CharFilter(field_name='priority')
    assigned_to = django_filters.NumberFilter(field_name='assigned_to__id')

    class Meta:
        model = Task
        fields = ['project', 'status', 'priority', 'assigned_to']


class ProjectFilter(django_filters.FilterSet):
    status = django_filters.CharFilter(field_name='status')

    class Meta:
        model = Project
        fields = ['status']
