from rest_framework import serializers
from django.contrib.auth.models import User
from apps.accounts.models import UserProfile
from apps.projects.models import Project, ProjectMembership
from apps.tasks.models import Task, Comment
from django.utils import timezone


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['role', 'bio', 'avatar']


class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'profile']


class ProjectMembershipSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = ProjectMembership
        fields = ['id', 'user', 'role', 'joined_at']


class ProjectSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)
    members = ProjectMembershipSerializer(source='memberships', many=True, read_only=True)
    progress = serializers.SerializerMethodField()
    task_count = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = ['id', 'name', 'description', 'status', 'deadline', 'created_by',
                  'created_at', 'updated_at', 'members', 'progress', 'task_count']
        read_only_fields = ['created_by', 'created_at', 'updated_at']

    def get_progress(self, obj):
        return obj.get_progress()

    def get_task_count(self, obj):
        return obj.tasks.count()

    def validate_deadline(self, value):
        if value and value < timezone.now().date():
            raise serializers.ValidationError('Deadline cannot be in the past.')
        return value


class CommentSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'author', 'body', 'created_at']
        read_only_fields = ['author', 'created_at']


class TaskSerializer(serializers.ModelSerializer):
    assigned_to = UserSerializer(read_only=True)
    assigned_to_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='assigned_to', write_only=True, required=False, allow_null=True
    )
    created_by = UserSerializer(read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'project', 'project_name',
            'assigned_to', 'assigned_to_id', 'created_by',
            'status', 'priority', 'due_date',
            'created_at', 'updated_at', 'comments'
        ]
        read_only_fields = ['created_by', 'created_at', 'updated_at']

    def validate_due_date(self, value):
        if value and self.instance is None and value < timezone.now().date():
            raise serializers.ValidationError('Due date must be in the future for new tasks.')
        return value


class TaskStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['status']
