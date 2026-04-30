from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.tasks.models import Task


class Command(BaseCommand):
    help = 'Mark tasks as overdue if their due_date has passed and they are not completed.'

    def handle(self, *args, **options):
        today = timezone.now().date()
        updated = Task.objects.filter(
            due_date__lt=today,
            status__in=['todo', 'in_progress']
        ).update(status='overdue')
        self.stdout.write(self.style.SUCCESS(f'Marked {updated} task(s) as overdue.'))
