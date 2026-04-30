from django.contrib import admin
from .models import Project, ProjectMembership


class MembershipInline(admin.TabularInline):
    model = ProjectMembership
    extra = 1
    raw_id_fields = ['user']


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'status', 'created_by', 'deadline', 'created_at']
    list_filter = ['status']
    search_fields = ['name', 'description']
    raw_id_fields = ['created_by']
    inlines = [MembershipInline]


@admin.register(ProjectMembership)
class ProjectMembershipAdmin(admin.ModelAdmin):
    list_display = ['project', 'user', 'role', 'joined_at']
    list_filter = ['role']
    raw_id_fields = ['project', 'user']
