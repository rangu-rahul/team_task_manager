from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from apps.accounts.models import UserProfile
from apps.projects.models import Project, ProjectMembership
from apps.tasks.models import Task
from django.utils import timezone
from datetime import timedelta


class Command(BaseCommand):
    help = 'Seed the database with demo users, projects, and tasks.'

    def handle(self, *args, **options):
        self.stdout.write('Seeding demo data...')

        # Create Admin
        admin, created = User.objects.get_or_create(
            username='admin_demo',
            defaults={'email': 'admin@demo.com', 'first_name': 'Admin', 'last_name': 'User'}
        )
        admin.set_password('Admin@123')
        admin.save()
        profile = admin.profile
        profile.role = 'admin'
        profile.bio = 'Demo admin account with full permissions.'
        profile.save()
        if created:
            self.stdout.write(self.style.SUCCESS('  Created admin user: admin@demo.com / Admin@123'))

        # Create Member 1
        m1, _ = User.objects.get_or_create(
            username='member1',
            defaults={'email': 'member1@demo.com', 'first_name': 'Alice', 'last_name': 'Smith'}
        )
        m1.set_password('Member@123')
        m1.save()
        p1 = m1.profile
        p1.role = 'member'
        p1.bio = 'Frontend developer and UI designer.'
        p1.save()
        self.stdout.write(self.style.SUCCESS('  Created member1: member1@demo.com / Member@123'))

        # Create Member 2
        m2, _ = User.objects.get_or_create(
            username='member2',
            defaults={'email': 'member2@demo.com', 'first_name': 'Bob', 'last_name': 'Jones'}
        )
        m2.set_password('Member@123')
        m2.save()
        p2 = m2.profile
        p2.role = 'member'
        p2.bio = 'Backend engineer specializing in APIs.'
        p2.save()
        self.stdout.write(self.style.SUCCESS('  Created member2: member2@demo.com / Member@123'))

        today = timezone.now().date()

        # Project 1
        proj1, _ = Project.objects.get_or_create(
            name='Website Redesign',
            defaults={
                'description': 'Complete redesign of the company website with modern UX.',
                'created_by': admin,
                'status': 'active',
                'deadline': today + timedelta(days=30),
            }
        )
        for user, role in [(admin, 'admin'), (m1, 'member'), (m2, 'member')]:
            ProjectMembership.objects.get_or_create(project=proj1, user=user, defaults={'role': role})

        tasks1 = [
            ('Design wireframes', m1, 'completed', 'high', today - timedelta(days=5)),
            ('Set up CI/CD pipeline', m2, 'completed', 'medium', today - timedelta(days=3)),
            ('Build homepage component', m1, 'in_progress', 'high', today + timedelta(days=7)),
            ('Write API documentation', m2, 'todo', 'medium', today + timedelta(days=10)),
            ('QA testing phase', None, 'todo', 'low', today + timedelta(days=20)),
        ]
        for title, assignee, st, pri, due in tasks1:
            Task.objects.get_or_create(
                title=title,
                project=proj1,
                defaults={
                    'description': f'Task: {title} for {proj1.name}',
                    'assigned_to': assignee,
                    'created_by': admin,
                    'status': st,
                    'priority': pri,
                    'due_date': due,
                }
            )
        self.stdout.write(self.style.SUCCESS(f'  Created project: {proj1.name} with 5 tasks'))

        # Project 2
        proj2, _ = Project.objects.get_or_create(
            name='Mobile App MVP',
            defaults={
                'description': 'Minimum viable product for the mobile application launch.',
                'created_by': admin,
                'status': 'active',
                'deadline': today + timedelta(days=60),
            }
        )
        for user, role in [(admin, 'admin'), (m1, 'member'), (m2, 'member')]:
            ProjectMembership.objects.get_or_create(project=proj2, user=user, defaults={'role': role})

        tasks2 = [
            ('Define MVP features', admin, 'completed', 'high', today - timedelta(days=10)),
            ('Database schema design', m2, 'overdue', 'high', today - timedelta(days=2)),
            ('Authentication module', m2, 'in_progress', 'high', today + timedelta(days=5)),
            ('Push notification setup', m1, 'todo', 'medium', today + timedelta(days=15)),
            ('Beta testing & feedback', None, 'todo', 'low', today + timedelta(days=50)),
        ]
        for title, assignee, st, pri, due in tasks2:
            Task.objects.get_or_create(
                title=title,
                project=proj2,
                defaults={
                    'description': f'Task: {title} for {proj2.name}',
                    'assigned_to': assignee,
                    'created_by': admin,
                    'status': st,
                    'priority': pri,
                    'due_date': due,
                }
            )
        self.stdout.write(self.style.SUCCESS(f'  Created project: {proj2.name} with 5 tasks'))

        self.stdout.write(self.style.SUCCESS('\nDemo data seeded successfully!'))
        self.stdout.write('  Admin: admin@demo.com / Admin@123')
        self.stdout.write('  Member1: member1@demo.com / Member@123')
        self.stdout.write('  Member2: member2@demo.com / Member@123')
